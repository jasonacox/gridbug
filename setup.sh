#!/bin/bash
#
# Interactive Setup Script for GridBug
# by Jason Cox - 8 Oct 2022

# Stop on Errors
set -e

# Determine version
VER=`grep "BUILD = " gridbug.py | cut -d\" -f2`

echo "GridBug (v${VER}) - SETUP"
echo "-----------------------------------------"

# Verify not running as root
if [ "$EUID" -eq 0 ]; then 
  echo "ERROR: Running this as root will cause permission issues."
  echo ""
  echo "Please ensure your local user in in the docker group and run without sudo."
  echo "   sudo usermod -aG docker \$USER"
  echo "   $0"
  echo ""
  exit 1
fi

# Docker Dependency Check
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: docker is not available or not runnning."
    echo "This script requires docker, please install and try again."
    exit 1
fi

GB_CONFIG="gridbug.conf"
GB_CONFIG_TEMPLATE="gridbug.conf.template"
GB_BUGS="gridbugs.json"

# Configuration File 
if [ -f ${GB_CONFIG} ]; then
    echo "Configuration file found:"
    echo ""
    cat ${GB_CONFIG}
    echo ""
    read -r -p "Update these? [y/N] " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        rm ${GB_CONFIG}
    else
        echo "Using existing ${GB_CONFIG}."
    fi
fi

# Create Config
if [ ! -f ${GB_CONFIG} ]; then
    echo "Enter details for this GridBug node..."
    read -p 'Gridbug Node ID: ' GB_ID
    read -p 'External URL with port (e.g. example.com:8777): ' GB_URL
    read -p 'Unique Grid Key: ' GB_KEY
    read -p 'TCP Port to use (e.g. 8777): ' GB_PORT
    if [ -z "${GB_PORT}" ]; then 
        GB_PORT=8777
    cp "${GB_CONFIG_TEMPLATE}" "${GB_CONFIG}"
    sed -i.bak "s@ZZ_ID@${GB_ID}@g;s@ZZ_URL@${GB_URL}@g;s@ZZ_KEY@${GB_KEY}@g;;s@ZZ_PORT@${GB_PORT}@g" "${GB_CONFIG}"
    echo ""

    # GridBug List File 
    if [ -f ${GB_BUGS} ]; then
        echo "GridBug list file found:"
        echo ""
        cat ${GB_BUGS}
        echo ""
        read -r -p "Update these? [y/N] " response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            rm ${GB_BUGS}
        else
            echo "Using existing ${GB_BUGS}."
        fi
    fi

    # Create GridBug Node List
    if [ ! -f ${GB_BUGS} ]; then
        python gen.py "${GB_URL}" "${GB_ID}"
        echo ""
        cat ${GB_BUGS}
        echo ""
    fi
fi

# Run Docker
echo "Starting up GridBug..."
docker run \
-d \
-p 8777:8777 \
-e GRIDBUGCONF='/var/lib/gridbug/gridbug.conf' \
-e GRIDBUGLIST='/var/lib/gridbug/gridbugs.json' \
-v ${PWD}:/var/lib/gridbug \
--name gridbug \
--restart unless-stopped \
jasonacox/gridbug

# Done
echo ""
echo "Done"