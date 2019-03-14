#!/bin/bash

# Importing useful functions for cc testing
if [ -f ./func_new.sh ]; then
 source ./func_new.sh
elif [ -f scripts/func_new.sh ]; then
 source scripts/func_new.sh
fi

## Create channel
echo_b "=== Creating channel ${APP_CHANNEL} with ${APP_CHANNEL_TX}... ==="

channelCreate "${APP_CHANNEL}" "${APP_CHANNEL_TX}"  "${CHANNEL_CREATE_ORG}" "${CHANNEL_CREATE_PEER}"

echo_g "=== Created channel ${APP_CHANNEL} with ${APP_CHANNEL_TX} ==="

echo
