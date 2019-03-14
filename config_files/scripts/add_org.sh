#!/bin/bash

#前提条件：脚本执行目录需要包含configtx.yaml配置文件和crypto-config证书目录(包含需要新增的组织信息)
#使用./addorg.sh mychannel false Org3MSP在普通通道中增加新的组织信息
#使用./addorg.sh e2e-orderer-syschan ture Org3MSP在系统通道中增加新的组织信息

#CHANNEL_NAME="$1"
#SYSCHANNELFlAG="$2"
#ORGMSP="$3"
#TLS_ENABLED=false

#需要修改以下几个变量为实际路径
WORK_DIR=/etc/hyperledger/fabric/crypto-config
#WORK_DIR=/home/haifeng/fabric-binary/peer/etc/hyperledger/fabric/addorg/crypto-config
configtxlator=/root/configtxlator
#peer=../bin/peer
configtxgen=/root/configtxgen

setGlobals() {
	ORG=$1
	DOMAIN=$2
    export CORE_PEER_LOCALMSPID=${ORG^}MSP
    export CORE_PEER_TLS_ROOTCERT_FILE=${WORK_DIR}/peerOrganizations/${ORG}.${DOMAIN}/peers/peer0.${ORG}.${DOMAIN}/tls/ca.crt
    export CORE_PEER_MSPCONFIGPATH=${WORK_DIR}/peerOrganizations/${ORG}.${DOMAIN}/users/Admin@org1.${ORG}.${DOMAIN}/msp
    export CORE_PEER_ADDRESS=peer0.${ORG}.${DOMAIN}:7051
	env | grep CORE
}


setOrdererEnv() {
    ORG=$1
    DOMAIN=$2

	export CORE_PEER_LOCALMSPID=${ORG^}MSP
	export CORE_PEER_MSPCONFIGPATH=${WORK_DIR}/ordererOrganizations/${DOMAIN}/users/Admin@${DOMAIN}/msp/
	export ORDERER_CA=${WORK_DIR}/ordererOrganizations/${DOMAIN}/orderers/orderer.${DOMAIN}/msp/tlscacerts/tlsca.${DOMAIN}-cert.pem

	env | grep CORE
}

function getChannelConfig () {

    ORG=$1
    DOMAIN=$2
    CHANNEL=$3
	setOrdererEnv $ORG $DOMAIN

    echo "Fetching the most recent configuration block for the channel"
    if [ -z "$CORE_PEER_TLS_ENABLED" -o "$CORE_PEER_TLS_ENABLED" = "false" ]; then
        set -x
        peer channel fetch config ${CHANNEL}.pb -o orderer.${DOMAIN}:7050 -c ${CHANNEL} --cafile $ORDERER_CA
        set +x
    else
        set -x
        peer channel fetch config ${CHANNEL}.pb -o orderer.${DOMAIN}:7050 -c ${CHANNEL} --tls --cafile $ORDERER_CA
        set +x
    fi

    echo "Decoding config block to JSON and isolating config to $CHANNEL.json"
        set -x
        ${configtxlator} proto_decode --input ${CHANNEL}.pb --type common.Block | jq .data.data[0].payload.data.config > ${CHANNEL}.json
        set +x
}


function generateUpdateConfig () {
#	${configtxgen} -printOrg ${ORGMSP} -profile ./configtx.yaml > ./${ORGMSP}.json
    ORG=$1
    CHANNEL=$2
    set -x
    jq -s '.[0] * {"channel_group":{"groups":{"Application":{"groups": {"${ORG^}MSP":.[1]}}}}}' ${CHANNEL}.json ./channel-artifacts/${ORG}.json > ${CHANNEL}_config.json
	${configtxlator} proto_encode --input ${CHANNEL}.json --type common.Config > original_${CHANNEL}.pb
	${configtxlator} proto_encode --input ${CHANNEL}_config.json --type common.Config > modified_${CHANNEL}.pb
	${configtxlator} compute_update --channel_id ${CHANNEL} --original original_${CHANNEL}.pb --updated modified_${CHANNEL}.pb > ${CHANNEL}_update.pb
	${configtxlator} proto_decode --input ${CHANNEL}_update.pb  --type common.ConfigUpdate > channel_update.json
	echo '{"payload":{"header":{"channel_header":{"channel_id":"'${CHANNEL}'", "type":2}},"data":{"config_update":'$(cat channel_update.json)'}}}' | jq . > ${CHANNEL}_update_envelope.json
	${configtxlator} proto_encode --input ${CHANNEL}_update_envelope.json --type common.Envelope > ${CHANNEL}_update_Org_envelope.pb
	set +x
}

function orgSignatureNewOrg () {

    orgs=${ORGS//,/ }
    for org in $orgs
    do
        domain=`eval echo '$'"${org^^}_DOMAIN"`
        setGlobals $org $domain
    peer channel signconfigtx -f ${CHANNEL}_update_Org_envelope.pb
    done
}

function updateChannelConfig () {

    ORG=$1
    DOMAIN=$2
    CHANNEL=$3
	setOrdererEnv $ORG $DOMAIN

	if [ -z "$CORE_PEER_TLS_ENABLED" -o "$CORE_PEER_TLS_ENABLED" = "false" ]; then
		peer channel update -f ${CHANNEL}_update_Org_envelope.pb -c ${CHANNEL} -o orderer.${DOMAIN}:7050
	else
		peer channel update -f ${CHANNEL}_update_Org_envelope.pb -c ${CHANNEL} -o orderer.${DOMAIN}:7050 --tls --cafile $ORDERER_CA
	fi
}

getChannelConfig $ORDERER_ORG $ORDERER_DOMAIN $CHANNEL

generateUpdateConfig $NEW_ORG $CHANNEL

orgSignatureNewOrg

updateChannelConfig $ORDERER_ORG $ORDERER_DOMAIN $CHANNEL