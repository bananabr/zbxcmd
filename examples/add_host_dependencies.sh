#!/bin/sh
# This script takes every trigger of PARENT_HOSTS with priority higher than TRIGGER_PRIO and 
# creates trigger dependencies on every trigger that belongs to hosts in CHILD_HOSTS

ZABBIX_BASE_URL='http://localhost'
ZABBIX_USER='Admin'
ZABBIX_PASSWORD='zabbix'
PARENT_HOST="lab-dc01"
CHILD_HOSTS="8.8.8.8"
TRIGGER_PRIO=2

PARENT_HOST_ID=`python zbxcmd.py -s $ZABBIX_BASE_URL -u $ZABBIX_USER -p $ZABBIX_PASSWORD -c host --method=get -F "host:$PARENT_HOST" -f hostid | jq ".hostid"`
PARENT_TRIGGERS=`python zbxcmd.py -s $ZABBIX_BASE_URL -u $ZABBIX_USER -p $ZABBIX_PASSWORD -c host --method=get -F "host:$PARENT_HOST" -f hostid -f host --include-triggers | jq ".triggers[] | select((.priority | tonumber) > $TRIGGER_PRIO) | .triggerid" | sed 's/"//g'`
echo $PARENT_HOST_ID
echo $PARENT_TRIGGERS
for HOST in $CHILD_HOSTS
do
    echo $HOST
    HOST_TRIGGERS=`python zbxcmd.py -s $ZABBIX_BASE_URL -u $ZABBIX_USER -p $ZABBIX_PASSWORD -c host --method=get -F "host:$HOST" -f hostid --include-triggers | jq ".triggers[] | .triggerid" | sed 's/"//g'`
    echo $HOST_TRIGGERS
    for TRIGGER in $HOST_TRIGGERS
    do
        for PARENT_TRIGGER in $PARENT_TRIGGERS
        do
            python zbxcmd.py -s $ZABBIX_BASE_URL -u $ZABBIX_USER -p $ZABBIX_PASSWORD -c trigger --method=adddependencies -F "triggerid:$TRIGGER" --depends-on $PARENT_TRIGGER
        done
    done
done


