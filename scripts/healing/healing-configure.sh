#! /bin/bash
ctx logger info "Retrieving nodes_to_monitor and deployment_id"
DEPLOYMENT_ID=$(ctx deployment id)
LOG_FILE=$(ctx node properties log_file)
PID_FILE=$(ctx node properties pid_file)
COOLDOWN_FILE=$(ctx node properties cooldown_file)
SCRIPT_DIR="/root/${DEPLOYMENT_ID}"
CONFIG_FILE="/etc/healing/healing_dog_${DEPLOYMENT_ID}"
HEALING_SCRIPT="${SCRIPT_DIR}/healing.py"

pythonPath=$(which python)
NODES_TO_MONITOR="$(ctx instance runtime_properties nodes_to_monitor_path)"
COMMAND="${pythonPath} ${HEALING_SCRIPT} -n ${NODES_TO_MONITOR} -d ${DEPLOYMENT_ID} -l ${LOG_FILE} -c ${COOLDOWN_FILE} -p ${PID_FILE}"

ctx logger info "writing config file - ${CONFIG_FILE}  : ${COMMAND}"
echo "*/1 * * * * root ${COMMAND}" > ${CONFIG_FILE}


ctx logger info "Linking config file to cron.d "
ln -s ${CONFIG_FILE} /etc/cron.d/
