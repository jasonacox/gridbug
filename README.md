# GridBug
This is a simple tool to monitor network connectivity between nodes and display a graph.

<img width="489" alt="image" src="https://user-images.githubusercontent.com/836718/193515045-d705c6d2-6918-449d-bb98-4e1ee0e98a0d.png">

## How it Works
The `gridbug.py` service pulls in a list of other GridBug nodes. It then proceeds to poll each of these nodes and records the state (link up or down).  

All of the GridBug nodes act as servers and clients.  Every node attempts to converge on the same graph by polling and sharing updates with each other. Each node builds a directional graph of connectivity between all the GridBug nodes and renders that as an HTML page using the [cytoscape](https://cytoscape.org/) JavaScript visualization library.


## Quick Start

A `setup.sh` script is available to help get you started.

* **ID** - Every GridBug node needs a unique `ID` that will show up on the visualization. Make this descriptive enough to identify where it is on the grid.  For example, 'CA-datacenter' and 'East-1-Cloud'.  Each node will also need a URL (hostname:8777) that is accessible by the other GridBug nodes.
* **GRIDKEY** - You will need to set a unique key (string of alphanumeric characters without spaces) for your grid network. This will be a shared key by all the GridBug nodes to authenticate other friendly GridNodes. This allow for dynamically adding new nodes to the grid as well.

    ```bash
    # Clone the Project
    git clone https://github.com/jasonacox/gridbug.git

    # Run the Setup script
    cd gridbug
    ./setup.sh

    # Open http://hostname:8777 to see the GridBug console
    ```

## Manual Setup

1. Create a `gridbug.conf` file (example below) and update with your specific location details. Make sure you update `ID` to be the unique name of the node.  

2. The `GRIDKEY` token should be a unique key (string of alphanumeric characters). It should be the same for all the GridBug nodes in your network.  GridBug will reject any updates from nodes that do not match this key.

* gridbug.conf - Configuration File
    ```conf
    [GRIDBUG]
    DEBUG = no
    ID = localhost
    NODEURL = example.com:8777
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
    # Notify connectivity issues - TODO
    ENABLE = yes
    ```
    
    * Note: There are environmental overrides that can be used to set all of the above configuration options.

3. Create a `gridbugs.json` seed file and add some nodes for your grid. The `host` is the address and should include the port (e.g. `:8777`) where `id` is the unique name of the node (matching gridbug.conf `ID`) for each node.

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

    * Note: This does not need to be the complete list of GridBugs in your network as GridBug will propagate discovered notes across the grid. If `host` and `id` are missing for the local node, it will automatically add `ID` and `NODEURL` from above config.

4. Run the Docker Container to listen on port 8777.

    ```bash
    docker run \
    -d \
    -p 8777:8777 \
    -e GRIDBUGCONF='/var/lib/gridbug/gridbug.conf' \
    -e GRIDBUGLIST='/var/lib/gridbug/gridbugs.json' \
    -v ${PWD}:/var/lib/gridbug:ro \
    --name gridbug \
    --user ${UID} \
    --restart unless-stopped \
    jasonacox/gridbug
    ```

5. View the GridBug Console and API Calls

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

Alternatively, you can just run the python server from a startup script:

```bash
python3 gridbug.py
```

