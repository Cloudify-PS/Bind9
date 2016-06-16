import sys
from cloudify_rest_client import CloudifyClient
from influxdb.influxdb08 import InfluxDBClient
from influxdb.influxdb08.client import InfluxDBClientError
from os import utime
from os import getpid 
from os import path
import datetime

# check against influxdb which nodes are available CPUtotal
# autoheal only missing nodes comparing to the node_instances that are taken from cloudify
# Checking it only for compute nodes

COOL_DOWN_PATH = '/tmp/cooldown'
LOG_FILE_PATH = '/tmp/logfile.log'
PID_FILE_PATH = '/tmp/pid_file'


def cool_down():
    if path.isfile(COOL_DOWN_PATH):
        now = datetime.datetime.now()
        then = datetime.datetime.fromtimestamp(path.getmtime(COOL_DOWN_PATH))
        time_delta = now - then
        seconds = time_delta.total_seconds()
        if seconds < 420:
            return True
    else:
        pass
    return False


def check_heal(nodes_to_monitor, deployment_id):
    if cool_down():
        print('Exiting from check_heal...\n')
        exit(0)
    influx_client = InfluxDBClient(host='localhost', port=8086, database='cloudify')
    log_file = open(LOG_FILE_PATH, 'w')
    log_file.write('In check_heal\n')
    cloudify_client = CloudifyClient('localhost')
    # compare influx data (monitoring) to Cloudify desired state

    for node_name in nodes_to_monitor:
        for instance_id in nodes_to_monitor[node_name]:
            log_file.write("deployment_id is {0}\n".format(deployment_id))
            log_file.write("node_name is {0}\n".format(node_name))
            log_file.write("instance.id is {0}\n".format(instance_id))
            q_string = 'SELECT MEAN(value) FROM /' + deployment_id + '\.' + node_name + '\.' + instance_id + '\.cpu_total_system/ GROUP BY time(10s) '\
                     'WHERE  time > now() - 40s'
            log_file.write('query string is:{0}\n'.format(q_string))
            try:
                result = influx_client.query(q_string)
                log_file.write('Query result is {0} \n'.format(result))
                if not result:
                    log_file.write("Opening {0} and closing it\n".format(COOL_DOWN_PATH))
                    open(COOL_DOWN_PATH, 'a').close()
                    log_file.write("utime {0}\n".format(COOL_DOWN_PATH))
                    utime(COOL_DOWN_PATH, None)
                    log_file.write("Healing {0}\n".format(instance_id))
                    execution_id = cloudify_client.executions.start(deployment_id, 'heal', {'node_instance_id': instance_id})
                    log_file.write('execution_id is {0}\n'.format(str(execution_id)))
            except InfluxDBClientError as ee:
                log_file.write('DBClienterror {0}\n'.format(str(ee)))
                log_file.write('instance id is {0}\n'.format(str(instance_id)))
            except Exception as e:
                log_file.write(str(e))


def main(argv):
    pid_file = open(PID_FILE_PATH, 'w')
    pid_file.write('%i' % getpid())
    pid_file.close()
    for i in range(len(argv)):
        print("argv={0}\n".format(argv[i]))
    with open(argv[1]) as f:
        lines = filter(None, f.read().split('\n'))
        nodes_to_monitor = {}
        for line in lines:
            node_name, instance_id = line.split(',')
            nodes = nodes_to_monitor.get(node_name, [])
            nodes.append(instance_id)
            nodes_to_monitor[node_name] = nodes

    deployment_id = argv[2]
    print("nodes={0}\n".format(nodes_to_monitor))
    check_heal(nodes_to_monitor, deployment_id)

if __name__ == '__main__':
    main(sys.argv)
