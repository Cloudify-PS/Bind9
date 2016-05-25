#! /bin/bash
DPLID=$(ctx deployment id)
read PID < /tmp/pid_file_${DPLID}
kill -9 $PID
rm /tmp/pid_file_${DPLID}

# cleanup cron
crontab_file=/tmp/mycron
currVenv=/root/${DPLID}/env

sudo crontab -l | grep -v ${currVenv} > ${crontab_file}
sudo crontab ${crontab_file}

status_code=$?
ctx logger info "crontab ${crontab_file} status code is ${status_code}"
currCrontab=`sudo crontab -l`
ctx logger info "currCrontab is ${currCrontab}"