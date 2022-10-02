# GridBug
Simple webservice to monitor and poll other GridBug nodes to monitor network connectivity.

## Configuration

#### Environmental Settings

* `GRIDBUGCONF` = Path to gridbug.conf config file

* `BUGLISTURL` = URL to gridbug.conf (overrides config)

#### Configuration Files

* gridbug.conf - Configuration File
    ```conf
    [GRIDBUG]
    DEBUG = no
    ID = localhost
    # Role: server, node
    ROLE = node

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
```
    The API service of gridbug has the following functions:
        /           - Human friendly display of current conditions
        /json       - All current gridbug status in JSON format
        /stats      - Internal gridbug metrics
```
