#! /bin/bash
DEPLOYMNET_ID=$(ctx deployment id)

CONFIG_DIR="/etc/healing"
SCRIPT_BASE="/root"


SCRIPT_DIR="${SCRIPT_BASE}/${DEPLOYMNET_ID}"


HEALING_SCRIPT="${SCRIPT_DIR}/healing.py"

currVenv="${SCRIPT_DIR}/env"



NODES_TO_MONITOR="$(ctx node properties nodes_to_monitor)"
NODES_TO_MONITOR=$(echo ${NODES_TO_MONITOR} | sed "s/u'/'/g")



ctx logger info "nodes_to_monitor = ${NODES_TO_MONITOR}"
ctx logger info "Retrieving nodes_to_monitor and deployment_id"

CONFIG_FILE="${CONFIG_DIR}/healing_dog_${DEPLOYMNET_ID}"


COMMAND="${currVenv}/bin/python ${HEALING_SCRIPT} \"${NODES_TO_MONITOR}\" ${DEPLOYMNET_ID}"

ctx logger info "writing config file - ${CONFIG_FILE}  : ${COMMAND}"
echo "*/1 * * * * ${COMMAND}" > ${CONFIG_FILE}


ctx logger info "Linking config file to cron.d "
ln -s ${CONFIG_FILE} /etc/cron.d/
