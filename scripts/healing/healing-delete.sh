#!/usr/bin/env bash
DEPLOYMNET_ID=$(ctx deployment id)

CONFIG_DIR="/etc/healing"
SCRIPT_DIR="/root/${DEPLOYMNET_ID}"
CONFIG_FILE_NAME="healing_dog_${DEPLOYMNET_ID}"
CONFIG_FILE="${CONFIG_DIR}/${CONFIG_FILE_NAME}"
CRON_JOB="/etc/cron.d/${CONFIG_FILE_NAME}"
LOG_FILE=$(ctx node properties log_file)
COOLDOWN_FILE=$(ctx node properties cooldown_file)
PID_FILE=$(ctx node properties pid_file)

ctx logger info "Removing config dir: ${CONFIG_DIR}, cron job: ${CRON_JOB} and working directory ${SCRIPT_DIR}"

rm ${CRON_JOB} 2>/dev/null
rm -r ${CONFIG_DIR} 2>/dev/null
rm -r ${SCRIPT_DIR} 2>/dev/null
rm ${LOG_FILE} 2>/dev/null
rm ${COOLDOWN_FILE} 2>/dev/null
rm ${PID_FILE} 2>/dev/null
