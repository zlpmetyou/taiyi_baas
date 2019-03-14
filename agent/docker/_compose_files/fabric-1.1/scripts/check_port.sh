#!/bin/bash

#
#if [ $# -ne 6 ]; then
#    echo "some ports has missed:"
#    exit
#fi
for var in "$@"; do
    while :
    do
        result=`echo -e "\n" | telnet ${var/:/ } | grep Connected | wc -l`
        if [ ${result} -eq 1 ]; then
          echo "$var is Open."
          break
        else
          echo "$var is closed,try again"
          continue
        fi
    done

done



