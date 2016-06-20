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
    parser.add_argument('-ct',
                        '--cooldown-time',
                        metavar='<cooldown time>')
    parser.add_argument('-p',
                        '--pid-file',
                        metavar='<pid file>')
    parser.add_argument('-db',
                        '--database',
                        metavar='<database name>')
    parser.add_argument('-h',
                        '--host',
                        metavar='<host>')
    parser.add_argument('-i',
                        '--influxdb-port',
                        metavar='<influxdb port>')
    parser.add_argument('-t',
                        '--time-diff',
                        metavar='<time diff>')

    return parser.parse_args()


def cool_down(cooldown_path, cooldown_time):
    if os.path.isfile(cooldown_path):
        now = datetime.datetime.now()
        then = datetime.datetime.fromtimestamp(
            os.path.getmtime(cooldown_path))
        time_delta = now - then
        seconds = time_delta.total_seconds()
        if seconds < int(cooldown_time):
            return True
    else:
        pass
    return False


def check_heal(nodes_to_monitor,
               deployment_id,
               cooldown_path,
               cooldown_time,
               time_diff,
               influxdb_port,
               database,
               host,
               logger):
    if cool_down(cooldown_path, cooldown_time):
        logger.info('Exiting from check_heal...')
        exit(0)
    logger.info('In check_heal. Getting clients.')
    influx_client = InfluxDBClient(host=host,
                                   port=int(influxdb_port),
                                   database=database)
    cloudify_client = CloudifyClient(host)
    # compare influx data (monitoring) to Cloudify desired state

    for node_name in nodes_to_monitor:
        instances = cloudify_client.node_instances.list(deployment_id,
                                                        node_name)
        for instance in instances:
            logger.info("Deployment_id: %s, node_name: %s, instance_id: %s "
                        % (deployment_id, node_name, instance.id))
            q_string = 'SELECT MEAN(value) FROM ' \
                       '/{0}\.{1}\.{2}\.cpu_total_system/ GROUP BY time(10s) ' \
                       'WHERE  time > now() - {3}s'.format(deployment_id,
                                                           node_name,
                                                           instance.id,
                                                           time_diff)
            logger.info('query string is:{0}'.format(q_string))
            try:
                result = influx_client.query(q_string)
                logger.info('Query result is {0} \n'.format(result))
                if not result:
                    logger.info("Opening {0} and closing it\n".format(
                        cooldown_path))
                    open(cooldown_path, 'a').close()
                    logger.info("utime {0}\n".format(cooldown_path))
                    os.utime(cooldown_path, None)
                    logger.info("Healing {0}\n".format(instance.id))
                    execution = cloudify_client.executions.start(
                        deployment_id,
                        'heal',
                        {'node_instance_id': instance.id})
                    logger.info('execution: {0}'.format(str(execution)))
            except InfluxDBClientError as ee:
                logger.info('DBClienterror {0}\n'.format(str(ee)))
                logger.info('instance id is {0}\n'.format(str(instance.id)))
            except Exception as e:
                logger.error('An error : %s' % str(e))


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
    with open(pid_file_path, 'w') as pid_file:
        pid_file.write('%i' % os.getpid())
    with open(args.nodes_to_monitor) as f:
        nodes_to_monitor = list(set(filter(None, f.read().split('\n'))))
    logger.info('Nodes to monitor: %s' % str(nodes_to_monitor))
    check_heal(nodes_to_monitor,
               args.deployment_id,
               args.cooldown_file,
               args.cooldown_time,
               args.time_diff,
               args.influxdb_port,
               args.database,
               args.host,
               logger)

if __name__ == '__main__':
    main()
