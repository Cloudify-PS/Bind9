#! /bin/bash

DEPLOYMNET_ID=$(ctx deployment id)

CONFIG_DIR="/etc/healing"
SCRIPT_BASE="/root"


ctx logger info "Retrieving deployment_id"



SCRIPT_DIR="${SCRIPT_BASE}/${DEPLOYMNET_ID}"


ctx logger info "Creating Directories Config : ${CONFIG_DIR} , scripts ${SCRIPT_DIR}"

mkdir -p ${CONFIG_DIR}



currVenv="${SCRIPT_DIR}/env"
ctx logger info "deployment_id = ${DEPLOYMNET_ID}, virtual env is ${currVenv}"
pipPath=${currVenv}/bin/pip
ctx logger info "Running ${pipPath} install influxdb  ... "
${pipPath} install influxdb
statusCode=$?
if [ $statusCode -gt 0 ]; then 
  ctx logger info "Aborting due to a failure with exit code ${statusCode} in ${pipPath} install influxdb"
  exit ${statusCode}
fi

ctx logger info "Downloading scripts/healing/healing.py and Copying it to ${SCRIPT_DIR}"

cp $(ctx download-resource scripts/healing/healing.py) ${SCRIPT_DIR}
status_code=$?
ctx logger info "ctx download-resource status code is ${status_code}"