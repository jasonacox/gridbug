# GridBug
This is a simple tool to monitor network connectivity between nodes and display status graph.

<img width="709" alt="image" src="https://user-images.githubusercontent.com/836718/193499507-faad0b45-d41f-4a72-afbb-0d3ed5f240f0.png">

## How it Works
The `gridbug.py` service pulls in a list of other gridbug nodes. It then proceeds to poll each of these nodes and records the state (link up or down).  

One of the gridbug nodes is designated as the server and the other grid nodes can send their results to that node.  The server node builds a direction graph of connectiity between all the gridbug nodes and renders a HTML page using the [cytoscape](https://cytoscape.org/) JavaScript visualization library.

## Configuration

### Environmental Settings

* GRIDBUGCONF = Path to gridbug.conf config file
* GRIDBUGLIST = Path to gridbugs.json node list
* BUGLISTURL = URL to gridbugs.json (overrides above)

## Quick Start

1. Create a `gridbug.conf` file and update with your specific location details. Make sure you update `ID` to be the unique name of the node.

* gridbug.conf - Configuration File
    ```conf
    [GRIDBUG]
    DEBUG = no
    # Unique name of this node
    ID = localhost
    ROLE = node
    CONSOLE = gridbug.html
    SERVERNODE = localhost:8777

    [API]
    # Port for API requests
    ENABLE = yes
    PORT = 8777

    [BUGS]
    # List of gridbug nodes
    WAIT = 10
    TTL = 60

    [ALERT]
    # Notify connectivity issues
    ENABLE = yes
    ```                             

1. Create a `gridbugs.json` file and add the list of nodes for your grid. The `host` is the address and should include the port (8777) where `id` is the unique name of the node (matching gridbug.conf `ID`) for each node.

* gridbugs.json - List of Grid Nodes
    ```json
    {
        "version": 1,
        "gridbugs": [{
            "host": "ptr.example.com:8777",
            "id": "jasonacox.com"
        }, {
            "host": "10.0.1.2:8777",
            "id": "LAN"
        }, {
            "host": "localhost:8777",
            "id": "origin"
        }]
    }
    ```

3. Run the Docker Container to listen on port 8777.

    ```bash
    docker run \
    -d \
    -p 8777:8777 \
    -e GRIDBUGCONF='/var/lib/gridbug/gridbug.conf' \
    -e GRIDBUGLIST='/var/lib/gridbug/gridbugs.json' \
    -v ${PWD}:/var/lib/gridbug \
    --name gridbug \
    --restart unless-stopped \
    jasonacox/gridbug
    ```

3. View the GridBug Console and API Calls

    Console: http://localhost:8777/

    ```bash
    # Get Version and Status
    curl -i http://localhost:8777/stats

    # Get Current Weather Data
    curl -i http://localhost:8777/text   # Text version of console
    curl -i http://localhost:8777/bugs   # List of gridbug nodes
    curl -i http://localhost:8777/graph  # nternal graph of connectivity (JSON)
    ```


### Direct Running

Alternatively, you can just run the python server from the `run.sh` startup script.

