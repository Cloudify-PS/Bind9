#!/usr/bin/env bash

host_node_name=$(ctx source node name)
host_instance_id=$(ctx source instance id)
# high risk of race condition
NODES_TO_MONITOR_PATH=$(ctx target instance runtime_properties nodes_to_monitor_path)
echo "${host_node_name},${host_instance_id}" | sudo tee -a ${NODES_TO_MONITOR_PATH}

