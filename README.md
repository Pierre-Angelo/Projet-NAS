# ProjetGNS3-grp19
	


## Features

- Generates complete Cisco router configurations.
- Supports IPv6 configurations.
- Configures BGP settings, including neighbor relationships and route maps.
- Applies OSPF or RIP configurations based on the network design.
- Sets up interface configurations, including Loopback and GigabitEthernet interfaces.
- Implements community lists for BGP route filtering.

## Prerequisites

- Python 3.x
- A JSON file containing the network intent and configuration details.

## Usage

1. Prepare a JSON file with your network's configuration intent. The JSON structure should include details for each router, such as AS number, routing protocol, border router information, hostname, OSPF costs, and interfaces.

2. Run the script with the path to your JSON file as an argument:

   ```bash
   python3 generate_config.py path/to/your/intent_file.json
   ```

3. The script will generate configuration files for each router defined in the JSON file and save them to the specified directory within the project structure.

## JSON File Structure

- `routers`: An array of objects, each representing a router's configuration.
- `config_files`: Specifies the directory and filename for each router's configuration file.
- `network_name`: The name of your network, used in the directory path for saving configurations.

## Output

The script generates configuration files for each router and saves them in the specified project directory structure. The file path is constructed using the `network_name` and details from the `config_files` mapping in the JSON file.

## Customization

You can customize the script to include additional routing protocols, interfaces, or configuration elements as needed by adjusting the Python classes and methods.
