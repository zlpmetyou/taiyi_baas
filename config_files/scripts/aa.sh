#!/bin/bash

CHANNELS=channel1,channel2
CHANNEL1_ORGS=org1,org2
CHANNEL2_ORGS=org2,
CHANNEL1_CREATE_ORG=org1
CHANNEL1_CREATE_PEER=peer0
CHANNEL2_CREATE_ORG=org2
CHANNEL2_CREATE_PEER=peer0


#var=org1,org2
#ORG1=peer0,peer1
var=${CHANNELS//,/ }
echo $var
for channel in $var
do
    channel_create_org=`eval echo '$'"${channel^^}_CREATE_ORG"`
    channel_create_peer=`eval echo '$'"${channel^^}_CREATE_PEER"`
    channel_orgs=`eval echo '$'"${channel^^}_ORGS"`
    echo $channel_create_org
    echo $channel_create_peer
    echo $channel_orgs
    echo "${channel}.tx"
#    for peer in ${result//,/ }
 #   do
  #  echo $peer
  #  done
done