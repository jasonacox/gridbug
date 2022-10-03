# GridBug
This is a simple tool to monitor network connectivity between nodes and display status graph.

<img width="741" alt="image" src="https://user-images.githubusercontent.com/836718/193484099-9d20c5a4-7778-44bb-8f92-e63514d72510.png">

## How it Works
The `gridbug.py` service pulls in a list of other gridbug nodes. It then proceeds to poll each of these nodes and records the state (link up or down).  

One of the gridbug nodes is designated as the server and the other grid nodes can send their results to that node.  The server node builds a direction graph of connectiity between all the gridbug nodes and renders a HTML page using the [cytoscape](https://cytoscape.org/) JavaScript visualization library.

## Configuration

### Environmental Settings

* `GRIDBUGCONF` = Path to gridbug.conf config file

* `BUGLISTURL` = URL to gridbugs.json (overrides config)

### Configuration Files

* gridbug.conf - Configuration File
    ```conf
    [GRIDBUG]
    DEBUG = no
    ID = localhost
    # Role: server, node
    ROLE = node
    CONSOLE = gridbug.html
    SERVERNODE = localhost:8777

    [API]
    # Port for API requests
    ENABLE = yes
    PORT = 8777

    [BUGS]
    # List of gridbug nodes
    WAIT = 1
    CONFIGFILE = gridbugs.json

    [ALERT]
    # Notify connectivity issues
    ENABLE = yes
    ```                             

* gridbugs.json - List of Grid Nodes
    ```json
    {
        "version": 1,
        "gridbugs": [{
            "host": "35.202.193.158",
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

### Running

See the `run.sh` startup

    The API service of gridbug has the following functions:
        /           - GridBug Console - displays graph of nodes      
        /text       - Human friendly display of current conditions
        /bugs       - List of gridbug nodes
        /stats      - Internal gridbug metrics
        /graph      - Internal graph of connectivity (JSON)
