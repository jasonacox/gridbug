# GridBug
Simple webservice to monitor and poll other GridBug nodes to monitor network connectivity.

<img width="615" alt="image" src="https://user-images.githubusercontent.com/836718/193483485-c19a5e25-8c4f-46bd-b8f0-5853c0074f87.png">

## Configuration

#### Environmental Settings

* `GRIDBUGCONF` = Path to gridbug.conf config file

* `BUGLISTURL` = URL to gridbugs.json (overrides config)

#### Configuration Files

* gridbug.conf - Configuration File
    ```conf
    [GRIDBUG]
    DEBUG = no
    ID = localhost
    # Role: server, node
    ROLE = node
    CONSOLE = gridbug.html

    [API]
    # Port for API requests
    ENABLE = yes
    PORT = 80

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
            "host": "10.0.1.2",
            "id": "LAN"
        }, {
            "host": "localhost",
            "id": "origin"
        }]
    }
    ```

### Running

See the `run.sh` startup

    The API service of gridbug has the following functions:
        /           - GirdBug Console - displays graph of nodes      
        /text       - Human friendly display of current conditions
        /bugs       - List of gridbug nodes
        /stats      - Internal gridbug metrics
        /graph      - Internal graph of connectivity (JSON)
