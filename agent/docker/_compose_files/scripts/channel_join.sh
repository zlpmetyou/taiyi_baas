#!/bin/bash

# Importing useful functions for cc testing
if [ -f ./func_new.sh ]; then
 source ./func_new.sh
elif [ -f scripts/func_new.sh ]; then
 source scripts/func_new.sh
fi

## Join all the peers to the channel

echo "Join peers into channels"
channels=${APP_CHANNELS//,/ }
for channel in $channels
do
    echo "Join peers into $channel"
    channel_orgs=`eval echo '$'"${channel^^}_ORGS"`
    for org in ${channel_orgs//,/ }
    do
        echo "Join peers of $org into $channel"
        channle_org_peers=`eval echo '$'"${org^^}"`
        for peer in ${channle_org_peers//,/ }
        do
            echo_b "=== Join peer $peer from org $org into $channel start... ==="
            channelJoin $channel $org $peer
            echo_b "=== Join peer $peer from org $org into $channel Complete... ==="
        done
        echo "Join peers of $org into $channel Complete"
    done
    echo "Join peers into $channel Complete"
done
echo "Join peers into channels Complete"

#var=${ORGS//,/}  #org1

#for org in $var
#do
#    result=`eval echo '$'"${org^^}"`
#    for peer in ${result//,/ }  # peer0 peer1
#    do
#    channelJoin ${APP_CHANNEL} $org $peer
#    done
#done

#echo_g "=== Join peers ${PEERS} from org ${ORGS} into ${APP_CHANNEL} Complete ==="

#echo

#ORG2=(peer0 peer1)
#ORG1=(peer3 peer4)
#ORGS=(org1 org2)
#
#for org in ${ORGS[@]}
#do
#    eval "for j in \${${org^^}[@]}
#          do
#           echo \$j
#          done"
#done
