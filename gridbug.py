#!/usr/bin/env python
# gridbug - Monitor Network Conditions
# -*- coding: utf-8 -*-
"""
 Python module to monitor network conditions by polling other gridbugs

 Author: Jason A. Cox
 For more information see https://github.com/jasonacox/gridbug

 GridBug
    This tool will poll a list of gridbug nodes to verify connectivity
    and will log any performance issues and optionally alert on it
    via pushing data to tools like New Relic, Datadog and Pager Duty

    CONFIGURATION FILE - On startup will look for gridbug.conf
    which includes the following parameters:

        [GRIDBUG]
        DEBUG = no
        ID = localhost
        # Role: server, node
        ROLE = node
        CONSOLE = gridbug.html
        SERVERNODE = localhost:8777
        GRIDKEY = CRuphacroN2hOfachlsWipaxi4ude1rlbIn4v0Vispiho7tuWeSPADrUdR2pE0rl

        [API]
        # Port for API requests
        ENABLE = yes
        PORT = 8777

        [BUGS]
        POLL = 10
        TTL = 30
        TIMEOUT = 10

        [ALERT]
        # Notify connectivity issues
        ENABLE = yes

    ENVIRONMENTAL (overrides above):
        GRIDBUGCONF = Path to gridbug.conf config file
        GRIDBUGLIST = Path to gridbugs.json node list
        BUGLISTURL = URL to gridbugs.json (overrides config)
        GRIDKEY = Private key for grid (overrides above)
        GB_ROLE = node or server
        GB_ID = Node ID
        GB_CONSOLE = HTML file for console
        GB_SERVERNODE = Default node to test
        GB_GRIDKEY = Private key for grid
        GB_APIPORT = TCP Port to Listen
        GB_POLL = Time in seconds to wait between tests
        GB_TTL = Time in seconds to identify dead node
        GB_TIMEOUT = Time in seconds to wait for response

    The API service of gridbug has the following functions:
        /           - GridBug Console - displays graph of nodes      
        /text       - Human friendly display of current conditions
        /bugs       - List of gridbug nodes
        /stats      - Internal gridbug metrics
        /graph      - Internal graph of connectivity (JSON)

"""
# Modules
from __future__ import print_function
import threading
import time
import logging
import json
import requests
import resource
import datetime
import sys
import os
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from socketserver import ThreadingMixIn 
import configparser

BUILD = "0.0.2"
MAXPAYLOAD = 4000       # Reject payload if above this size
CONFIGFILE = os.getenv("GRIDBUGCONF", "gridbug.conf")
GRIDBUGLIST = os.getenv("GRIDBUGLIST", "gridbugs.json")
BUGLISTURL = os.getenv("BUGLISTURL", "") 
URL = ""

# Load Configuration File
config = configparser.ConfigParser(allow_no_value=True)
if os.path.exists(CONFIGFILE):
    config.read(CONFIGFILE)
    DEBUGMODE = config["GRIDBUG"]["DEBUG"].lower() == "yes"
    ID = config["GRIDBUG"]["ID"]
    ROLE = config["GRIDBUG"]["ROLE"]
    CONSOLE = config["GRIDBUG"]["CONSOLE"]
    SERVERNODE = config["GRIDBUG"]["SERVERNODE"]
    GRIDKEY = config["GRIDBUG"]["GRIDKEY"]

    # GridBug API
    API = config["API"]["ENABLE"].lower() == "yes"
    APIPORT = int(config["API"]["PORT"])

    # GridBugs
    GBPOLL = int(config["BUGS"]["POLL"])
    TTL = int(config["BUGS"]["TTL"])
    TIMEOUT = int(config["BUGS"]["TIMEOUT"])
    
    # Alerts
else:
    # No config file - Display Error
    sys.stderr.write("GridBug Server %s\nERROR: No config file. Fix and restart.\n" % BUILD)
    sys.stderr.flush()
    while(True):
        time.sleep(3600)

# Environment vars override config
ROLE = os.getenv("GB_ROLE", ROLE) 
ID = os.getenv("GB_ID", ID) 
CONSOLE = os.getenv("GB_CONSOLE", CONSOLE) 
SERVERNODE = os.getenv("GB_SERVERNODE", SERVERNODE) 
GRIDKEY = os.getenv("GB_GRIDKEY", GRIDKEY) 
APIPORT = os.getenv("GB_APIPORT", APIPORT) 
GBPOLL = os.getenv("GB_POLL", GBPOLL) 
TTL = os.getenv("GB_TTL", TTL) 
TIMEOUT = os.getenv("GB_TIMEOUT", TIMEOUT) 

# Logging
log = logging.getLogger(__name__)
if DEBUGMODE:
    logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)
    log.setLevel(logging.DEBUG)
    log.debug("GridBug [%s]\n" % BUILD)

# Global Stats
serverstats = {}
serverstats['GridBug'] = BUILD
serverstats['node_id'] = ID
serverstats['gets'] = 0
serverstats['posts'] = 0
serverstats['errors'] = 0
serverstats['timeout'] = 0
serverstats['poll'] = 0
serverstats['uri'] = {}
serverstats['ts'] = int(time.time())         # Timestamp for Now
serverstats['start'] = int(time.time())      # Timestamp for Start 
serverstats['clear'] = int(time.time())      # Timestamp of lLast Stats Clear

# Global Variables
running = True
bugs = {}
graph = {"nodes": [], "edges": []}

# Add bugs to dict
def addbug(host, id):
    """
    Function to add a grid bug if not already in dict
    """
    for b in bugs["gridbugs"]:
        if b["id"] == id:
            return False
    bugs["gridbugs"].append({"host": host, "id": id})
    log.debug("GRAPH: Added bug %s %s" % (id, host))
    return True

# Graph Functions
def updategraph(payload=False):
    """
    Function to update graph data
    """
    global bugs, graph
    currentts = time.time()
    alive = False
    if True:
        if payload:
            # Update based on received measurements
            source = payload["node_id"]
            if "node_host" in payload:
                sourcehost = payload["node_host"]
            else:
                sourcehost = ""
        else:
            # Update based on our measurements
            source = ID
            payload = bugs
        for n in payload["gridbugs"]:
            target = n["id"]
            targethost = n["host"]
            # Add any new nodes to bugs database for polling
            if sourcehost != "":
                addbug(sourcehost, source)
            addbug(targethost, source)
            # Update graph
            if "alive" in n:
                alive = n["alive"]
            id = "%s.%s" % (source,target)
            if source not in graph["nodes"]:
                graph["nodes"].append(source)
            if target not in graph["nodes"]:
                graph["nodes"].append(target)
            found = False
            # Update edges if they are from an authorized source
            for e in graph["edges"]:
                if e["id"] == id and e["source"] == source:
                    e["ts"] = currentts
                    if alive:
                        e["color"] = "green"
                    else:
                        e["color"] = "red"
                    found = True
                else:
                    if "ts" in e and (e["ts"] + TTL < currentts):
                        # Edge has aged out
                        e["color"] = "gray"
            if not found:
                graph["edges"].append({"id": id, "source": source, "target": target, "alive": alive})
        return True
    else:
        sys.stderr.write("Invalid payload - ignored\n")
        return False

# Threads
def pollgridbugs():
    """
    Thread to poll for current conditions and update graph
    """
    global running, serverstats, URL, bugs
    sys.stderr.write(" + pollgridbugs thread\n")
    nextupdate = time.time()

    # Time Loop to update current conditions data
    while(running):
        currentts = time.time()

        # Is it time for an update?
        if currentts >= nextupdate:
            nextupdate = currentts + GBPOLL

            for node in bugs['gridbugs']:
                URL = "http://%s/ping" % node['host']
                log.debug("Ping URL = %s\n" % URL)
                serverstats['poll'] += 1
                try:
                    response = requests.get(URL, timeout=TIMEOUT)
                    if response.status_code == 200: 
                        log.debug("Got response from grid %s %s" % (node['id'], node['host']))
                        node['alive'] = True 
                        # Attempt to send payload to update node
                        try:
                            headers = {'key': GRIDKEY}
                            sname = "http://%s/post" % node['host']
                            r = requests.post(sname, json=bugs, headers=headers)
                            log.debug("Sent graph to node %s %s" % (node['id'], node['host']))
                            # print("Sent graph to node %s %s" % (node['id'], node['host']))
                        except:
                            #print("Unable to send graph to node %s" % node['host'])
                            log.debug("Unable to send graph to node %s" % node['host'])
                        # Attempt to poll node for any graph updates
                        try:
                            sname = "http://%s/bugs" % node['host']
                            r = requests.get(sname, timeout=TIMEOUT)
                            payload = r.json()
                            updategraph(payload)
                        except:
                            log.debug("Unable to update graph from node %s" % node['host'])
 
                    else:
                        # no response
                        log.debug("Got %d response from grid %s %s" % 
                            (response.status_code, node['id'], node['host'])) 
                        node['alive'] = False 
                except:
                    # no response 
                    log.debug("No response from grid %s %s" % (node['id'], node['host']))   
                    node['alive'] = False 
                    pass

            # Update graph based on discovery
            updategraph()

            # Send in update to server node
            try:
                headers = {'key': GRIDKEY}
                sname = "http://%s/post" % SERVERNODE
                r = requests.post(sname, json=bugs, headers=headers, timeout=TIMEOUT)
                log.debug(f"SENT: Status Code: {r.status_code}, Response: {r.json()}")
            except:
                log.debug("Unable to update server %s" % SERVERNODE)

        time.sleep(5)
    sys.stderr.write('\r ! pollgridbugs Exit\n')

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    pass

class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if DEBUGMODE:
            sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))
        else:
            pass

    def address_string(self):
        # replace function to avoid lookup delays
        host, hostport = self.client_address[:2]
        return host

    def do_POST(self):
        global URL
        self.send_response(200)
        message = "Error"
        contenttype = 'application/json'
        if self.path == '/post':
            message = '{"status": "OK"}'   
            content_len = int(self.headers.get('content-length', 0))
            if content_len > MAXPAYLOAD:
                message = "Error: Received Heavy Payload - Ignoring"
            else:
                post_body = self.rfile.read(content_len)
                try:
                    post_json = json.loads(post_body)
                    key = self.headers.get('key', '')
                    log.debug("POST from %s (key = %s) json: %r" % (post_json["node_id"], key, post_json))
                    if key != GRIDKEY:
                        log.debug("- Unauthorized Payload from %s" % post_json["node_id"])
                    else:
                        log.debug("+ Authorized Payload from %s" % post_json["node_id"])
                        updategraph(post_json)
                except:
                    log.debug("Error: Invalid Payload")
                    message = "Error: Invalid Payload"
        else:
            # Error
            message = "Error: Unsupported Request"

        # Counts 
        if "Error" in message:
            log.debug("POST Path %s = %s" % (self.path, message))
            serverstats['errors'] = serverstats['errors'] + 1
        else:
            if self.path in serverstats["uri"]:
                serverstats["uri"][self.path] += 1
            else:
                serverstats["uri"][self.path] = 1
        serverstats['posts'] = serverstats['posts'] + 1

        # Send headers and payload
        self.send_header('Content-type',contenttype)
        self.send_header('Content-Length', str(len(message)))
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))

    def do_GET(self):
        global URL, CONSOLE
        self.send_response(200)
        message = "Error"
        contenttype = 'application/json'
        result = {}  # placeholder
        if self.path == '/ping':
            message = '{"status": "OK"}'
        elif self.path == '/favicon.ico':
            contenttype = 'image/x-icon'
            message = 'data:image/x-icon;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQEAYAAABPYyMiAAAABmJLR0T///////8JWPfcAAAACXBIWXMAAABIAAAASABGyWs+AAAAF0lEQVRIx2NgGAWjYBSMglEwCkbBSAcACBAAAeaR9cIAAAAASUVORK5CYII='
        elif self.path == '/text':
            # Display friendly intro
            contenttype = 'text/html'
            message = '<html>\n<head><meta http-equiv="refresh" content="5" />\n'
            message += '<style>p, td, th { font-family: Helvetica, Arial, sans-serif; font-size: 10px;}</style>\n' 
            message += '<style>h1 { font-family: Helvetica, Arial, sans-serif; font-size: 20px;}</style>\n' 
            message += '</head>\n<body>\n<h1>GridBug %s v%s - ID %s</h1>\n\n' % (ROLE.title(), BUILD, ID)
            if len(bugs['gridbugs']) < 1:
                message = message + "<p>Error: No gridbug data available</p>"
            else:
                message = message + '<table>\n<tr><th align ="right">GridBug ID</th><th align ="right">Alive</th></tr>'
                for i in bugs['gridbugs']:
                    if 'alive' in i:
                        message = message + '<tr><td align ="right">%s</td><td align ="right">%s</td></tr>\n' % (i['id'],i['alive'])
                message = message + "</table>\n"
            message = message + '\n<p>Page refresh: %s</p>\n</body>\n</html>' % (
                str(datetime.datetime.fromtimestamp(time.time())))
        elif self.path == '/stats':
            # Give Internal Stats
            serverstats['ts'] = int(time.time())
            serverstats['mem'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            message = json.dumps(serverstats)
        elif self.path == '/bugs' or self.path == '/gridbugs.json':
            message = json.dumps(bugs)
        elif self.path == '/raw':
            message = json.dumps(graph)
        elif self.path == '/graph':
            nodes = []
            edges = []
            for n in graph["nodes"]:
                nodes.append({"data": {"id": n}})
            for e in graph["edges"]:
                edges.append({"data": e })
            output = {"nodes": nodes, "edges": edges}
            message = json.dumps(output)
        elif self.path == '/' or self.path == '/gridbug.html':
            contenttype = 'text/html'
            try:
                with open(CONSOLE, 'r') as f:
                    message = f.read()
                    f.close()
            except:
                message = "Error: Unable to open gridbug.html"
        elif self.path == '/time':
            ts = time.time()
            result["local_time"] = str(datetime.datetime.fromtimestamp(ts))
            result["ts"] = ts
            result["utc"] = str(datetime.datetime.utcfromtimestamp(ts)) 
            message = json.dumps(result)
        else:
            # Error
            message = "Error: Unsupported Request"

        # Counts 
        if "Error" in message:
            log.debug("GET Path %s = %s" % (self.path, message))
            serverstats['errors'] = serverstats['errors'] + 1
        else:
            if self.path in serverstats["uri"]:
                serverstats["uri"][self.path] += 1
            else:
                serverstats["uri"][self.path] = 1
        serverstats['gets'] = serverstats['gets'] + 1

        # Send headers and payload
        self.send_header('Content-type',contenttype)
        self.send_header('Content-Length', str(len(message)))
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))

def api(port):
    """
    API Server - Thread to listen for commands on port 
    """
    sys.stderr.write(" + apiServer thread - Listening on http://localhost:%d\n" % port)

    with ThreadingHTTPServer(('', port), handler) as server:
        try:
            # server.serve_forever()
            while running:
                server.handle_request()
        except:
            print(' CANCEL \n')
    sys.stderr.write('\r ! apiServer Exit\n')

# MAIN Thread
if __name__ == "__main__":
    # Create threads
    thread_pollgridbugs = threading.Thread(target=pollgridbugs)
    thread_api = threading.Thread(target=api, args=(APIPORT,))
    
    # Print header
    sys.stderr.write("GridBug %s [%s] - ID: %s\n" % (ROLE.title(), BUILD, ID))
    sys.stderr.write("* Configuration Loaded [%s]\n" % CONFIGFILE)
    sys.stderr.write(" + GridBug - Debug: %s, Activate API: %s, API Port: %s\n" 
        % (DEBUGMODE, API, APIPORT))
    sys.stderr.write(" + GridKey: [%s]\n" % GRIDKEY)

    # Load the bugs
    if BUGLISTURL == "":
        # Load from local file
        try:
            with open(GRIDBUGLIST, 'r') as f:
                bugs = json.load(f)
                f.close()
                sys.stderr.write(" + Loaded [%s]: %d bugs loaded (version %d)\n" 
                    % (GRIDBUGLIST, len(bugs['gridbugs']), bugs['version']))
        except:
            sys.stderr.write("ERROR: Unable to load grid bug list - tried %s\n" % GRIDBUGLIST)
            sys.exit()
    else:
        # Load from URL
        try:
            r = requests.get(BUGLISTURL)
            bugs = r.json()
            sys.stderr.write(" + Loaded [%s]: %d bugs loaded (version %d)\n" 
                % (BUGLISTURL, len(bugs['gridbugs']), bugs['version']))
        except:
            sys.stderr.write("ERROR: Unable to load grid bug list - tried %s\n" % BUGLISTURL)
            sys.exit()

    # Validate bugs DB
    nodes = []
    for n in bugs['gridbugs']:
        if n["id"] in nodes:
            sys.stderr.write("ERROR: Found duplicates in grid bug list - IDs must be unique\n")
            sys.exit()
        nodes.append(n["id"])
        if n["id"] == ID:
            HOST = n["host"]    # Self Hostname of Grid Node
        print(n)
    if ID not in nodes:
        # TODO We need to add ourself - error out for now
        # me = {"id": ID, "host": "localhost"}
        sys.stderr.write("ERROR: Unable to find myself in the grid bug list - exiting\n")
        sys.exit()

    # Add local identity to DB
    bugs['node_id'] = ID
    bugs['node_role'] = ROLE
    bugs['node_build'] = BUILD
    bugs['node_host'] = HOST

    # Start threads
    sys.stderr.write("* Starting threads\n")
    thread_pollgridbugs.start()
    thread_api.start()
    sys.stderr.flush()
    
    log.debug("Start Polling" )
    try:
        while(True):
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        running = False
        # Close down API thread
        requests.get('http://localhost:%d/stop' % APIPORT)
        print("\r", end="")

    sys.stderr.write("* Stopping\n")
    sys.stderr.flush()
