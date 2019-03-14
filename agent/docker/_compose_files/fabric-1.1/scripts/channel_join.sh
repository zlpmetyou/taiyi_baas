#!/bin/bash

# Importing useful functions for cc testing
if [ -f ./func.sh ]; then
 source ./func.sh
elif [ -f scripts/func.sh ]; then
 source scripts/func.sh
fi

## Join all the peers to the channel
echo_b "=== Join peers ${PEERS} from org ${ORGS} into ${APP_CHANNEL}... ==="

for org in ${ORGS[@]}
do
#	for peer in ${org[@]}
#	do
#		channelJoin ${APP_CHANNEL} $org $peer
#	done
    eval "for peer in \${${org^^}[@]}
          do
            channelJoin ${APP_CHANNEL} $org $peer
          done"
done

echo_g "=== Join peers ${PEERS} from org ${ORGS} into ${APP_CHANNEL} Complete ==="

echo

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
