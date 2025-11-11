Created: 2025 November 11

# WebServer Module Design

## Table of Contents

[Project Info](<#project info>)
[Module Overview](<#module overview>)
[Scope](<#scope>)
[Design Constraints](<#design constraints>)
[Component Details](<#component details>)
[HTTP Endpoints](<#http endpoints>)
[HTML Interface](<#html interface>)
[Interfaces](<#interfaces>)
[Error Handling](<#error handling>)
[Cross References](<#cross references>)
[Version History](<#version history>)

---

## Project Info

**Project:** pi-netconfig  
**Module:** WebServer  
**Version:** 1.0.0  
**Date:** 2025-11-11  
**Author:** William Watson  
**Master Design:** [design-0000-master.md](<design-0000-master.md>)

[Return to Table of Contents](<#table of contents>)

---

## Module Overview

**Purpose:** Provide HTTP interface on port 8080 for network configuration when device is in AP mode.

**Responsibilities:**
- Serve HTML configuration interface
- Handle network scan requests
- Process configuration submissions
- Provide API endpoints for status queries
- Embed HTML/CSS/JavaScript resources

**Context:** Started by StateMonitor when entering AP_MODE, stopped when transitioning to CLIENT mode.

[Return to Table of Contents](<#table of contents>)

---

## Scope

**In Scope:**
- HTTP server on port 8080
- Single-page HTML configuration interface
- REST-like JSON API endpoints
- Network scanning via ConnectionManager
- Configuration application via ConnectionManager
- Embedded HTML/CSS/JavaScript (no external files)
- CORS headers for API access
- Error responses with appropriate HTTP status codes

**Out of Scope:**
- HTTPS/TLS encryption
- User authentication
- Session management
- Multi-page navigation
- File upload/download
- WebSocket support
- Server-sent events
- Static file serving from filesystem

[Return to Table of Contents](<#table of contents>)

---

## Design Constraints

**Technical:**
- Must run on port 8080 (no conflicts with standard ports)
- Single-threaded HTTP server (sufficient for configuration use case)
- Must work without external file dependencies
- No authentication (local AP network assumed secure)

**Implementation:**
- Language: Python 3.11+
- Framework: http.server (stdlib)
- External libraries: http.server, json, urllib.parse (stdlib only)
- Standards: PEP 8 compliance, type hints, HTTP/1.1

**Performance:**
- Page load: < 500ms
- API response: < 2 seconds for scan, < 1 second for status
- Configuration application: < 10 seconds

[Return to Table of Contents](<#table of contents>)

---

## Component Details

### ConfigHTTPHandler Class

**Purpose:** Custom HTTP request handler for configuration interface

**Inherits From:** `http.server.BaseHTTPRequestHandler`

**Key Methods:**

```python
def do_GET(self) -> None
```
- Routes GET requests to appropriate handlers
- Paths: `/`, `/api/scan`, `/api/status`
- Returns: HTML (for `/`) or JSON (for `/api/*`)
- Handles 404 for unknown paths

```python
def do_POST(self) -> None
```
- Routes POST requests to appropriate handlers
- Path: `/api/configure`
- Expects: JSON body with ssid and password
- Returns: JSON response with success status
- Handles 400 for invalid JSON or missing fields

```python
def serve_html_page(self) -> None
```
- Sends HTTP 200 response
- Content-Type: text/html
- Body: Complete HTML page with embedded CSS/JS
- Includes configuration form and network list

```python
def handle_scan_request(self) -> None
```
- Calls ConnectionManager.scan_networks()
- Formats results as JSON array
- Response format: `{"networks": [{"ssid": str, "signal": int, "security": str}]}`
- Sends HTTP 200 on success
- Sends HTTP 500 on scan failure

```python
def handle_status_request(self) -> None
```
- Queries StateMonitor for current state
- Queries ConnectionManager for configured network
- Response format: `{"state": str, "ssid": str|null, "ap_active": bool}`
- Sends HTTP 200

```python
def handle_configure_request(self) -> None
```
- Parses JSON body
- Validates ssid and password presence
- Calls ConnectionManager.configure_network(ssid, password)
- Response format: `{"success": bool, "message": str}`
- Sends HTTP 200 on success, HTTP 400 on validation error, HTTP 500 on configuration failure

```python
def send_json_response(self, data: dict, status: int = 200) -> None
```
- Sets Content-Type: application/json
- Sets CORS header: Access-Control-Allow-Origin: *
- Sends status code and JSON body
- Handles JSON serialization

```python
def send_error_response(self, status: int, message: str) -> None
```
- Sends JSON error response
- Format: `{"error": message}`
- Common status codes: 400, 404, 500

### APIEndpoints Class

**Purpose:** Organize API logic separately from HTTP handler

**Key Methods:**

```python
async def scan() -> dict
```
- Delegates to ConnectionManager.scan_networks()
- Formats NetworkInfo objects to JSON-serializable dicts
- Returns: `{"networks": [...]}`

```python
async def configure(ssid: str, password: str) -> dict
```
- Delegates to ConnectionManager.configure_network()
- Returns: `{"success": True, "message": "Configuration applied"}`
- Raises: ConfigurationError with user-friendly message

```python
async def status() -> dict
```
- Queries StateMonitor.current_state
- Queries ConnectionManager.load_configuration()
- Queries APManager.is_active()
- Returns: `{"state": "CLIENT"|"AP_MODE", "ssid": str|null, "ap_active": bool}`

### WebServerManager Class

**Purpose:** Manage HTTP server lifecycle

**Key Methods:**

```python
async def start_server(port: int = 8080) -> None
```
- Creates HTTPServer instance with ConfigHTTPHandler
- Binds to 0.0.0.0:8080 (accessible on all interfaces)
- Starts server in separate thread (non-blocking)
- Sets server_running = True
- Raises: WebServerError if port unavailable

```python
async def stop_server() -> None
```
- Gracefully shuts down HTTP server
- Closes all connections
- Joins server thread
- Sets server_running = False
- Best-effort operation (logs but doesn't raise on errors)

```python
def is_running() -> bool
```
- Returns: server_running status

[Return to Table of Contents](<#table of contents>)

---

## HTTP Endpoints

### GET /

**Purpose:** Serve main configuration page

**Response:**
- Status: 200 OK
- Content-Type: text/html
- Body: Complete HTML page with embedded CSS and JavaScript

**HTML Content:**
- Network scan button
- Available networks list (populated via AJAX)
- SSID selection/input field
- Password input field
- Connect button
- Status display area
- Automatic network refresh on page load

### GET /api/scan

**Purpose:** Scan for available WiFi networks

**Response:**
- Status: 200 OK
- Content-Type: application/json
- Body:
```json
{
  "networks": [
    {
      "ssid": "NetworkName",
      "signal": 85,
      "security": "WPA2",
      "frequency": "2.4GHz"
    }
  ]
}
```

**Error Response:**
- Status: 500 Internal Server Error
- Body: `{"error": "Scan failed: <reason>"}`

### GET /api/status

**Purpose:** Get current system state and configuration

**Response:**
- Status: 200 OK
- Content-Type: application/json
- Body:
```json
{
  "state": "AP_MODE",
  "ssid": "PreviousNetwork",
  "ap_active": true
}
```

**Fields:**
- `state`: Current operational state (CLIENT, AP_MODE, CHECKING)
- `ssid`: Currently configured network (null if none)
- `ap_active`: Whether AP mode is currently active

### POST /api/configure

**Purpose:** Apply network configuration

**Request:**
- Content-Type: application/json
- Body:
```json
{
  "ssid": "NetworkName",
  "password": "network_password"
}
```

**Success Response:**
- Status: 200 OK
- Body: `{"success": true, "message": "Configuration applied. Connecting..."}`

**Error Responses:**
- Status: 400 Bad Request - Invalid JSON or missing fields
  - Body: `{"error": "Missing required field: ssid"}`
- Status: 400 Bad Request - Validation failure
  - Body: `{"error": "SSID must be 1-32 characters"}`
- Status: 500 Internal Server Error - Configuration failure
  - Body: `{"error": "Failed to connect: <reason>"}`

[Return to Table of Contents](<#table of contents>)

---

## HTML Interface

### Page Structure

**Title:** Pi Network Configuration

**Sections:**
1. **Header:** Application title and current status
2. **Network List:** Display of available networks with signal strength indicators
3. **Configuration Form:** SSID input, password input, connect button
4. **Status Messages:** Success/error feedback to user

### User Interaction Flow

1. User connects to PiConfig-XXXX AP (password: piconfig123)
2. User navigates to http://192.168.50.1:8080
3. Page automatically scans for networks and displays list
4. User selects network from list or manually enters SSID
5. User enters password
6. User clicks "Connect" button
7. JavaScript makes POST request to /api/configure
8. Status message displays "Connecting..."
9. On success: displays "Connected! AP will deactivate shortly."
10. On failure: displays error message, allows retry

### JavaScript Functionality

**On Page Load:**
- Automatic call to /api/scan
- Populate network list with results
- Sort by signal strength

**Scan Button:**
- Manual trigger of network scan
- Update network list with new results

**Network Selection:**
- Click on network item populates SSID field
- Pre-selects network in form

**Connect Button:**
- Validates form inputs (non-empty)
- Sends POST to /api/configure
- Displays loading indicator
- Shows result message

**Status Polling:**
- Optional: periodic /api/status requests
- Updates connection status display

### CSS Styling

**Design Principles:**
- Clean, minimal interface
- Large, touch-friendly buttons
- Clear visual hierarchy
- Responsive layout (mobile-friendly)
- High contrast for outdoor use

**Color Scheme:**
- Background: Light (#f5f5f5)
- Primary: Blue (#2196F3)
- Success: Green (#4CAF50)
- Error: Red (#f44336)
- Text: Dark gray (#333)

[Return to Table of Contents](<#table of contents>)

---

## Interfaces

### Public Functions

```python
async def start_server(port: int = 8080) -> None
```
**Purpose:** Start HTTP server  
**Parameters:** port (default: 8080)  
**Returns:** None  
**Raises:** WebServerError if port unavailable

```python
async def stop_server() -> None
```
**Purpose:** Stop HTTP server  
**Parameters:** None  
**Returns:** None  
**Raises:** None (best-effort shutdown)

```python
def is_running() -> bool
```
**Purpose:** Check if server currently running  
**Parameters:** None  
**Returns:** Server running status

### Component Interactions

**From StateMonitor:**
- `start_server()` - called when entering AP_MODE
- `stop_server()` - called when transitioning to CLIENT
- `is_running()` - called to verify server state

**To ConnectionManager:**
- `scan_networks()` - called on GET /api/scan
- `configure_network()` - called on POST /api/configure
- `load_configuration()` - called on GET /api/status

**To StateMonitor:**
- Query current_state for /api/status

**To APManager:**
- `is_active()` - called for /api/status

[Return to Table of Contents](<#table of contents>)

---

## Error Handling

### Exception Hierarchy

```python
class WebServerError(PiNetConfigError):
    """Base exception for web server operations"""
    pass

class ServerStartError(WebServerError):
    """Server start failure"""
    pass

class PortInUseError(WebServerError):
    """Port 8080 already in use"""
    pass
```

### Error Conditions and Handling

**Port 8080 Unavailable:**
- Condition: Socket bind fails (address in use)
- Handling: Raise PortInUseError
- Recovery: Log critical error, attempt service restart
- Message: "Port 8080 in use. Check for conflicting services."

**Invalid JSON in POST:**
- Condition: JSON parse error
- Handling: Return HTTP 400 with error message
- Recovery: User corrects input and retries
- Response: `{"error": "Invalid JSON in request body"}`

**Missing Required Fields:**
- Condition: SSID or password not in JSON
- Handling: Return HTTP 400 with specific field name
- Recovery: User provides missing field
- Response: `{"error": "Missing required field: ssid"}`

**Network Scan Failure:**
- Condition: ConnectionManager.scan_networks() raises exception
- Handling: Return HTTP 500 with error details
- Recovery: User retries scan
- Response: `{"error": "Scan failed: <details>"}`

**Configuration Failure:**
- Condition: ConnectionManager.configure_network() raises exception
- Handling: Return HTTP 500 with error message
- Recovery: User verifies credentials and retries
- Response: `{"error": "Failed to connect: invalid password"}`

**Server Thread Exception:**
- Condition: Unhandled exception in HTTP handler thread
- Handling: Log error with traceback, continue serving
- Recovery: Isolated to single request, server continues

### Logging

**Level: DEBUG**
- HTTP request details (method, path, headers)
- API endpoint calls
- JSON request/response bodies

**Level: INFO**
- Server start/stop events
- Successful configuration applications
- Network scan requests and result counts

**Level: WARNING**
- Invalid JSON requests
- Missing required fields
- Network scan failures (non-critical)

**Level: ERROR**
- Configuration failures
- Port binding failures
- Server thread exceptions

**Level: CRITICAL**
- Server start failure (port unavailable)
- Unable to stop server gracefully

[Return to Table of Contents](<#table of contents>)

---

## Cross References

**Master Design:** [design-0000-master.md](<design-0000-master.md>)

**Related Modules:**
- [StateMonitor](<design-0002-statemonitor.md>) - Controls server lifecycle
- [ConnectionManager](<design-0003-connectionmanager.md>) - Provides scanning and configuration
- [APManager](<design-0004-apmanager.md>) - Provides AP network for server access

**Dependencies:**
- http.server (stdlib) - HTTP server implementation
- json (stdlib) - JSON serialization
- urllib.parse (stdlib) - URL parsing
- threading (stdlib) - Non-blocking server operation

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-11 | William Watson | Initial module design extracted from master |

[Return to Table of Contents](<#table of contents>)

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
