#!/usr/bin/env bash

echo_r () {
    [ $# -ne 1 ] && return 0
    echo -e "\033[31m$1\033[0m"
}
echo_g () {
    [ $# -ne 1 ] && return 0
    echo -e "\033[32m$1\033[0m"
}
echo_y () {
    [ $# -ne 1 ] && return 0
    echo -e "\033[33m$1\033[0m"
}
echo_b () {
    [ $# -ne 1 ] && return 0
    echo -e "\033[34m$1\033[0m"
}

WORK_DIR=/etc/hyperledger/fabric/crypto-config

setGlobals() {
	ORG=$1
	PEER=$2
	DOMAIN=$3
	echo ${DOMAIN}
    export CORE_PEER_LOCALMSPID=${ORG^}MSP
    export CORE_PEER_TLS_ROOTCERT_FILE=${WORK_DIR}/peerOrganizations/${ORG}.${DOMAIN}/peers/${PEER}.${ORG}.${DOMAIN}/tls/ca.crt
    export CORE_PEER_MSPCONFIGPATH=${WORK_DIR}/peerOrganizations/${ORG}.${DOMAIN}/users/Admin@${ORG}.${DOMAIN}/msp
    export CORE_PEER_ADDRESS=${PEER}.${ORG}.${DOMAIN}:7051
	env | grep CORE
}

channelJoinAction () {
	local channel=$1
	peer channel join \
		-b ${channel}.block \
		>&log.txt
}

channelJoin () {
	local channel=$1
	local org=$2
	local peer=$3
	local domain=$4

	[ -z $channel ] && [ -z $org ] && [ -z $peer ] && echo_r "input param invalid" && exit -1

	echo "=== Join org $org/peer $peer into channel ${channel} === "
	setGlobals $org $peer $domain
	channelJoinAction ${channel}
	echo "=== org $org/peer $peer joined into channel ${channel} === "
}

channel_join () {
    echo "Join peers into channel"
    channel=$CHANNEL
    org=${NEW_ORG}
    peers=${NEW_ORG_PEERS//,/ }
    domain=${NEW_ORG_DOMAIN}
    for peer in $peers
    do
        echo "Join $peer of $org into $channel"

        channelJoin $channel $org $peer $domain

        echo "Join $peer of $org into $channel Complete"
    done
    echo "Join peers into channel Complete"
}

channel_join