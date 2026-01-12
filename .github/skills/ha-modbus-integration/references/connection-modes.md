# Connection Modes
- tcp: socket framer; set host/port, timeout (~5s), optional delay after connect.
- rtuovertcp: RTU framer over TCP for gateways; often needs message_wait_milliseconds spacing (e.g., 30 ms) and optional small delay after connect.
- serial: RTU over RS-485; set baudrate/bytesize/parity/stopbits; tune timeout and message_wait_milliseconds (defaults 30 ms).
- Always serialize IO per client (async lock). Keep one client instance per hub/config entry.
