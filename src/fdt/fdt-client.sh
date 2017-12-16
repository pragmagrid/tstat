#!/bin/bash
#
# fdt-client .sh - script to start client 
# from fdt web site
#

if [ $# -lt 1 ]; then
    echo "***************************************************"
    echo "************** Parameters needed ******************"
    echo "***************************************************"
    java -jar fdt.jar -h
    exit 0
fi

found=false
for param in $*; do
    if [ "$param" == "-c" ]; then
        found=true
        break
    fi
done

if [ "$found" == "false" ]; then
    echo "***************************************************"
    echo "******* Please specify the server address *********"
    echo "***************************************************"
    java -jar fdt.jar -h    
    exit 0
fi

java -jar fdt.jar $*
