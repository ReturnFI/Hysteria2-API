# Hysteria2-API

[![PyPI version](https://badge.fury.io/py/hysteria2-api.svg)](https://badge.fury.io/py/hysteria2-api)
[![Python Versions](https://img.shields.io/pypi/pyversions/hysteria2-api.svg)](https://pypi.org/project/hysteria2-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client library for interacting with the Hysteria2 proxy server API.

## Installation

```bash
pip install hysteria2-api
```

## Quick Start

```python
from hysteria2_api import Hysteria2Client

# Initialize the client
client = Hysteria2Client(
    base_url="http://127.0.0.1:25413",  # Replace with your Hysteria2 API URL
    secret="your_secret_here"           # Replace with your API secret
)

# Get traffic statistics with automatic clearing
traffic_stats = client.get_traffic_stats(clear=True)
for user_id, stats in traffic_stats.items():
    print(f"User: {user_id}")
    print(f"Upload: {stats.upload_bytes} bytes")
    print(f"Download: {stats.download_bytes} bytes")

# Check which users are online
online_users = client.get_online_clients()
for user_id, status in online_users.items():
    if status.is_online:
        print(f"User {user_id} is online with {status.connections} connection(s)")

# Kick specific users
client.kick_clients(["user1", "user2"])
```

## Features

- **Traffic Statistics**: Get traffic data for all clients with option to clear after retrieval
- **Online Status**: Check which clients are currently connected and how many connections they have
- **User Management**: Kick clients by their IDs
- **Type Support**: Full type hinting support for better IDE integration
- **Error Handling**: Specialized exception classes for different error scenarios

## API Reference

### Hysteria2Client

The main client class for interacting with the Hysteria2 API.

```python
client = Hysteria2Client(
    base_url="http://127.0.0.1:25413",  # Base URL of the Hysteria2 API
    secret="your_secret_here",          # API secret for authentication
    timeout=10                          # Request timeout in seconds
)
```

#### Methods

- **get_traffic_stats(clear=False)**
  - Gets traffic statistics for all clients
  - Parameters:
    - `clear` (bool): Whether to clear statistics after retrieval
  - Returns: Dictionary mapping client IDs to `TrafficStats` objects

- **get_online_clients()**
  - Gets online status for all clients
  - Returns: Dictionary mapping client IDs to `OnlineStatus` objects

- **kick_clients(client_ids)**
  - Kicks clients by their IDs
  - Parameters:
    - `client_ids` (List[str]): List of client IDs to kick
  - Returns: True if successful, raises exception otherwise

### Data Models

#### TrafficStats

Represents traffic statistics for a client.

```python
stats = TrafficStats(tx=1024, rx=2048)
```

- **Properties**:
  - `tx` (int): Transmitted bytes (upload)
  - `rx` (int): Received bytes (download)
  - `upload_bytes` (int): Alias for tx
  - `download_bytes` (int): Alias for rx

#### OnlineStatus

Represents online status information for clients.

```python
status = OnlineStatus(connections=2)
```

- **Properties**:
  - `connections` (int): Number of active connections
  - `is_online` (bool): Whether the client is online (has at least one connection)

### Exceptions

- **Hysteria2Error**: Base exception for all Hysteria2 API errors
- **Hysteria2AuthError**: Raised when authentication with the API fails
- **Hysteria2ConnectionError**: Raised when there's an error connecting to the API

## Example: Traffic Monitoring Script

Here's an example of a script that monitors traffic and updates a local JSON file:

```python
#!/usr/bin/env python3
import json
import os
from hysteria2_api import Hysteria2Client

# Define static variables
CONFIG_FILE = '/etc/hysteria/config.json'
USERS_FILE = '/etc/hysteria/users.json'
API_BASE_URL = 'http://127.0.0.1:25413'

def traffic_status():
    # ANSI color codes
    green = '\033[0;32m'
    cyan = '\033[0;36m'
    NC = '\033[0m'  # No Color

    # Load config to get API secret
    with open(CONFIG_FILE, 'r') as config_file:
        config = json.load(config_file)
        secret = config.get('trafficStats', {}).get('secret')

    if not secret:
        print("Error: Secret not found in config.json")
        return

    # Initialize API client
    client = Hysteria2Client(base_url=API_BASE_URL, secret=secret)

    # Get data from API
    traffic_stats = client.get_traffic_stats(clear=True)
    online_status = client.get_online_clients()

    # Load existing user data
    users_data = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as users_file:
            users_data = json.load(users_file)

    # Update user data with new information
    for user_id in list(users_data.keys()):
        users_data[user_id]["status"] = "Offline"

    for user_id, status in online_status.items():
        if user_id in users_data:
            users_data[user_id]["status"] = "Online" if status.is_online else "Offline"
        else:
            users_data[user_id] = {
                "upload_bytes": 0,
                "download_bytes": 0,
                "status": "Online" if status.is_online else "Offline"
            }

    for user_id, stats in traffic_stats.items():
        if user_id in users_data:
            users_data[user_id]["upload_bytes"] += stats.upload_bytes
            users_data[user_id]["download_bytes"] += stats.download_bytes
        else:
            online = user_id in online_status and online_status[user_id].is_online
            users_data[user_id] = {
                "upload_bytes": stats.upload_bytes,
                "download_bytes": stats.download_bytes,
                "status": "Online" if online else "Offline"
            }

    # Save updated data
    with open(USERS_FILE, 'w') as users_file:
        json.dump(users_data, users_file, indent=4)

    # Display traffic data
    print("Traffic Data:")
    print("-------------------------------------------------")
    print(f"{'User':<15} {'Upload':<15} {'Download':<15} {'Status':<10}")
    print("-------------------------------------------------")

    for user, entry in users_data.items():
        upload = format_bytes(entry.get("upload_bytes", 0))
        download = format_bytes(entry.get("download_bytes", 0))
        status = entry.get("status", "Offline")

        print(f"{user:<15} {green}{upload:<15}{NC} {cyan}{download:<15}{NC} {status:<10}")

def format_bytes(bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}"
        bytes /= 1024
    return f"{bytes:.2f}PB"

if __name__ == "__main__":
    traffic_status()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Hysteria2](https://github.com/apernet/hysteria) - The high-performance proxy protocol this library interacts with