#!/usr/bin/env bash

host_name=$(ctx source instance runtime_properties external_name)
host_name=$(echo $host_name | tr '_' '-')
# high risk of race condition
NODES_TO_MONITOR_PATH=$(ctx target instance runtime_properties nodes_to_monitor_path)
echo ${host_name} | sudo tee -a ${NODES_TO_MONITOR_PATH}

