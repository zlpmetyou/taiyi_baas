#!/bin/bash


var=org1,org2
ORG1=peer0,peer1
var=${var//,/ }

for el in $var
do
    result=`eval echo '$'"${el^^}"`
    for peer in ${result//,/ }
    do
    echo $peer
    done
done