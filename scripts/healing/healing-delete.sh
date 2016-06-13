DEPLOYMNET_ID=$(ctx deployment id)
CONFIG_DIR="/etc/healing"
SCRIPT_BASE="/root"


SCRIPT_DIR="${SCRIPT_DIR}/${DEPLOYMNET_ID}"


HEALING_SCRIPT="${SCRIPT_DIR}/healing.py"

currVenv="${SCRIPT_DIR}/env"

CONFIG_FILE_NAME="healing_dog_${DEPLOYMNET_ID}"

CONFIG_FILE="${CONFIG_DIR}/${CONFIG_FILE_NAME}"


rm /etc/cron.d/${CONFIG_FILE_NAME}

rm ${CONFIG_FILE}

rm ${HEALING_SCRIPT}

