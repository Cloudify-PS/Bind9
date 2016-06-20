#!/usr/bin/env bash

host_node_name=$(ctx target node name)
# high risk of race condition
NODES_TO_MONITOR_PATH=$(ctx source instance runtime_properties nodes_to_monitor_path)
echo "${host_node_name}" | sudo tee -a ${NODES_TO_MONITOR_PATH}

