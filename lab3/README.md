# Packet Crafting Project

This project implements a packet crafting library in Python, inspired by Scapy. It allows users to create, send, and receive network packets across various layers of the networking stack.

## Project Structure

- **layers/**: Contains classes representing different layers of the networking stack.
  - `__init__.py`: Initializes the layers package.
  - `base.py`: Base class for network layers.
  - `ether.py`: Ethernet layer implementation.
  - `ip.py`: Internet Protocol layer implementation.
  - `icmp.py`: Internet Control Message Protocol layer implementation.
  - `udp.py`: User Datagram Protocol layer implementation.
  - `tcp.py`: Transmission Control Protocol layer implementation.
  - `dns.py`: Domain Name System layer implementation.

- **net/**: Contains networking-related classes and functions.
  - `__init__.py`: Initializes the net package.
  - `sockets.py`: Functions for managing raw sockets.

- **utils/**: Contains utility functions for the project.
  - `__init__.py`: Initializes the utils package.
  - `helpers.py`: Helper functions for checksum calculations and IP address conversions.

- **examples/**: Contains example scripts demonstrating the usage of the library.
  - `ping_example.py`: Example of sending an ICMP ping request.
  - `dns_example.py`: Example of sending a DNS query.
  - `tcp_http_example.py`: Example of establishing a TCP connection and performing an HTTP GET request.

- **api.py**: Main API for the project, providing functions to send and receive packets.

- **self_check.py**: Contains self-check functions to test the functionality of the implemented layers.

- **requirements.txt**: Lists the dependencies required for the project.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd lab3
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the self-check script to ensure everything is working:
   ```
   python self_check.py
   ```

## Usage Examples

### ICMP Ping Example
To send an ICMP ping request, you can use the `ping_example.py` script:
```
python examples/ping_example.py
```

### DNS Query Example
To send a DNS query, use the `dns_example.py` script:
```
python examples/dns_example.py
```

### TCP HTTP Example
To establish a TCP connection and perform an HTTP GET request, run:
```
python examples/tcp_http_example.py
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.