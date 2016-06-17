import argparse
import datetime
import logging
import os

from cloudify_rest_client import CloudifyClient
from influxdb.influxdb08 import InfluxDBClient
from influxdb.influxdb08.client import InfluxDBClientError

# check against influxdb which nodes are available CPUtotal
# autoheal only missing nodes comparing to the node_instances that are taken from cloudify
# Checking it only for compute nodes


def _parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-l',
                        '--logfile',
                        required=True,
                        metavar='<log file path>')
    parser.add_argument('-d',
                        '--deployment-id',
                        metavar='<deployment id>')
    parser.add_argument('-n',
                        '--nodes-to-monitor',
                        metavar='<nodes to monitor file path>')
    parser.add_argument('-c',
                        '--cooldown-file',
                        metavar='<cooldown file>')
    parser.add_argument('-p',
                        '--pid-file',
                        metavar='<pid file>')

    return parser.parse_args()


def cool_down(cool_down_path):
    if os.path.isfile(cool_down_path):
        now = datetime.datetime.now()
        then = datetime.datetime.fromtimestamp(
            os.path.getmtime(cool_down_path))
        time_delta = now - then
        seconds = time_delta.total_seconds()
        if seconds < 420:
            return True
    else:
        pass
    return False


def check_heal(nodes_to_monitor, deployment_id, cool_down_path, logger):
    if cool_down(cool_down_path):
        logger.info('Exiting from check_heal...')
        exit(0)
    logger.info('In check_heal. Getting clients.')
    influx_client = InfluxDBClient(host='localhost',
                                   port=8086,
                                   database='cloudify')
    cloudify_client = CloudifyClient('localhost')
    # compare influx data (monitoring) to Cloudify desired state

    for node_name in nodes_to_monitor:
        for instance_id in nodes_to_monitor[node_name]:
            logger.info("Deployment_id: %s, node_name: %s, instance_id: %s "
                        % (deployment_id, node_name, instance_id))
            q_string = 'SELECT MEAN(value) FROM /' + deployment_id + '\.' + node_name + '\.' + instance_id + '\.cpu_total_system/ GROUP BY time(10s) '\
                     'WHERE  time > now() - 40s'
            logger.info('query string is:{0}'.format(q_string))
            try:
                result = influx_client.query(q_string)
                logger.info('Query result is {0} \n'.format(result))
                if not result:
                    logger.info("Opening {0} and closing it\n".format(
                        cool_down_path))
                    open(cool_down_path, 'a').close()
                    logger.info("utime {0}\n".format(cool_down_path))
                    os.utime(cool_down_path, None)
                    logger.info("Healing {0}\n".format(instance_id))
                    execution_id = cloudify_client.executions.start(deployment_id, 'heal', {'node_instance_id': instance_id})
                    logger.info('execution_id is {0}\n'.format(str(execution_id)))
            except InfluxDBClientError as ee:
                logger.info('DBClienterror {0}\n'.format(str(ee)))
                logger.info('instance id is {0}\n'.format(str(instance_id)))
            except Exception as e:
                logger.info(str(e))


def _set_logger(args):
    logger = logging.getLogger('HEALING')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(args.logfile)
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(fh)
    return logger


def main():
    args = _parse_args()
    logger = _set_logger(args)
    pid_file_path = args.pid_file
    cool_down_path = args.cooldown_file
    with open(pid_file_path, 'w') as pid_file:
        pid_file.write('%i' % os.getpid())
    with open(args.nodes_to_monitor) as f:
        lines = filter(None, f.read().split('\n'))
        nodes_to_monitor = {}
        for line in lines:
            node_name, instance_id = line.split(',')
            nodes = nodes_to_monitor.get(node_name, [])
            nodes.append(instance_id)
            nodes_to_monitor[node_name] = nodes
    logger.info('Nodes to monitor: %s' % str(nodes_to_monitor))
    check_heal(nodes_to_monitor,
               args.deployment_id,
               cool_down_path,
               logger)

if __name__ == '__main__':
    main()
