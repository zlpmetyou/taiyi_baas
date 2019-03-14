#!/bin/bash

# Importing useful functions for cc testing
if [ -f ./func_new.sh ]; then
 source ./func_new.sh
elif [ -f scripts/func_new.sh ]; then
 source scripts/func_new.sh
fi

## Create channel
echo "=== Creating channels... ==="
channels=${APP_CHANNELS//,/ }  #末尾有空格
for channel in $channels
do
    channel_create_org=`eval echo '$'"${channel^^}_CREATE_ORG"`
    channel_create_peer=`eval echo '$'"${channel^^}_CREATE_PEER"`

    channel_tx="${channel}.tx"
    echo_b "=== Creating channel $channel with $channel_tx... ==="
    channelCreate $channel $channel_tx $channel_create_org $channel_create_peer
    echo_g "=== Created channel $channel with $channel_tx... ==="
done

echo "=== Created channels... ==="
