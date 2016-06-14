DEPLOYMNET_ID=$(ctx deployment id)

CONFIG_DIR="/etc/healing"
SCRIPT_DIR="/root/${DEPLOYMNET_ID}"
CONFIG_FILE_NAME="healing_dog_${DEPLOYMNET_ID}"
CONFIG_FILE="${CONFIG_DIR}/${CONFIG_FILE_NAME}"
CRON_JOB="/etc/cron.d/${CONFIG_FILE_NAME}"

ctx logger info "Removing config dir: ${CONFIG_DIR}, cron job: ${CRON_JOB} and working directory ${SCRIPT_DIR}"

rm ${CRON_JOB}
rm -r ${CONFIG_DIR}
rm -r ${SCRIPT_DIR}

