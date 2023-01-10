#!/bin/bash
#
# Example startup to simulate a diskless / serverless setup (e.g. AWS ECS, Azure ACS)
#
# by Jason Cox - 9 Jan 2023

# Set these environmental variables
export BUGLISTURL="https://jasonacox.com/gridbugs.json"  # URL to gridbugs.json file 
export GB_ID="cloud-us-west"                             # Name for this node 
export GB_DEBUG="no"                                     # Debug mode yes/no
export GB_NODEURL="autodiscover"                         # or Address/IP:PORT for this node
export GB_GRIDKEY="RaNdomKeY-4-your-Grid"                # Unique key for your grid network

# Start
python3 gridbug.py
