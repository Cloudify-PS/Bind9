#! /bin/bash

ctx logger info "Retrieving nodes_to_monitor and deployment_id"

NTM="$(ctx node properties nodes_to_monitor)"

ctx logger info "nodes_to_monitor = ${NTM}"
NTM=$(echo ${NTM} | sed "s/u'/'/g")
DPLID=$(ctx deployment id)
currVenv=/root/${DPLID}/env
ctx logger info "deployment_id = ${DPLID}, virtual env is ${currVenv}"
pipPath=${currVenv}/bin/pip
ctx logger info "Running ${pipPath} install influxdb  ... "
${pipPath} install influxdb
statusCode=$?
if [ $statusCode -gt 0 ]; then 
  ctx logger info "Aborting due to a failure with exit code ${statusCode} in ${pipPath} install influxdb"
  exit ${statusCode}
fi

ctx logger info "Downloading scripts/healing/healing.py ..."
LOC=$(ctx download-resource scripts/healing/healing.py)
status_code=$?
ctx logger info "ctx download-resource status code is ${status_code}"
ctx logger info "LOC is ${LOC}"