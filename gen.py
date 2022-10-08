#!/usr/bin/env python
# gridbug node json file generator
# -*- coding: utf-8 -*-
"""
 Generate the gridbugs.json file

 Author: Jason A. Cox
 For more information see https://github.com/jasonacox/gridbug

 Command line: python gen.py [host] [id]
      [host] and [id] are optional but will be added as a node if provided

"""
# Modules
from __future__ import print_function
import json, sys

# Backward compatibility for python2
try:
    input = raw_input
except NameError:
    pass

BUGSFILE = "gridbugs.json"
bugs = {"version": 1, "gridbugs": []}

print(len(sys.argv))

if len(sys.argv) >= 3:
    # Add command line node entry
    host = sys.argv[1]
    id = sys.argv[2]
    bugs["gridbugs"].append({"host": host, "id": id})

print("GRIDBUG Node Entry")
print("------------------------------------------------------")
print("* ID is the unique name of the host (e.g. cloud-1).")
print("* URL is the externally available address that other")
print("  nodes will call and MUST have a port number but")
print("  not the http prefix (e.g. my.example.com:8777)")
print("")

x = 1
while True:
    print ("[GridBug Entry %d]" % x)
    print ("  Enter GridBug Node ID (enter to stop): ", end="")
    id = input()
    if id == "":
        break
    print ("  Enter GridBug Hostname URL (enter to stop): ", end="")
    host = input()
    if host == "":
        break
    bugs["gridbugs"].append({"host": host, "id": id})
    print("")
    x = x = 1

print("")
print("Writing out %s..." % BUGSFILE)
with open(BUGSFILE, 'w') as f:
    json.dump(bugs, f, indent=4)
