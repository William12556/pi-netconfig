Created: 2025 November 12

# T04 Prompt: WebServer Module

```yaml
prompt_info:
  id: "prompt-0005"
  task_type: "code_generation"
  source_ref: "design-0005-webserver"
  date: "2025-11-12"
  priority: "high"

mcp_config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.2
  max_tokens: 4096
  system_prompt: |
    Expert Python developer. Generate production-quality code following specifications.
    OUTPUT FORMAT: Code only with brief integration notes. No explanations.

context:
  purpose: "HTTP interface on port 8080 for network configuration during AP mode"
  integration: "Started by StateMonitor when entering AP_MODE, stopped when transitioning to CLIENT"
  constraints:
    - "Port 8080 only"
    - "Single-threaded HTTP server sufficient"
    - "No external file dependencies (embedded HTML/CSS/JS)"
    - "No authentication required"

specification:
  description: "Implement HTTP server with embedded single-page HTML interface, REST-like JSON API endpoints, network scanning and configuration capabilities"
  requirements:
    functional:
      - "HTTP server on port 8080, accessible at 192.168.50.1:8080"
      - "GET / - serve embedded HTML configuration page"
      - "GET /api/scan - return JSON network list via ConnectionManager"
      - "GET /api/status - return system state and connection info"
      - "POST /api/configure - accept JSON {ssid, password}, apply via ConnectionManager"
      - "Embedded HTML with network selection, SSID input, password input, connect button"
      - "JavaScript for AJAX calls and UI updates"
      - "CORS headers for API access"
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Thread-safe, comprehensive error handling, debug logging, docstrings, type hints"
  performance:
    - target: "Page load under 500ms"
      metric: "time"
    - target: "API responses under 2 seconds for scan, 1 second for status"
      metric: "time"

design:
  architecture: "http.server with custom request handler, embedded resources"
  components:
    - name: "ConfigHTTPHandler"
      type: "class (extends BaseHTTPRequestHandler)"
      purpose: "Handle HTTP requests"
      interface:
        inputs:
          - name: "request"
            type: "HTTP request"
            description: "GET or POST with path and body"
        outputs:
          type: "HTTP response"
          description: "HTML or JSON with appropriate status code"
        raises:
          - "WebServerError"
      logic:
        - "do_GET(): Route to / or /api/* handlers"
        - "do_POST(): Route to /api/configure"
        - "serve_html_page(): Send embedded HTML with CSS and JS"
        - "handle_scan_request(): Call ConnectionManager.scan_networks(), return JSON"
        - "handle_status_request(): Query StateMonitor/ConnectionManager/APManager, return JSON"
        - "handle_configure_request(): Parse JSON body, validate, call ConnectionManager.configure_network()"
        - "send_json_response(): Set Content-Type, CORS header, send JSON"
        - "send_error_response(): Send JSON error with status code"
    
    - name: "APIEndpoints"
      type: "class"
      purpose: "Organize API logic"
      interface:
        inputs:
          - name: "varies by endpoint"
            type: "varies"
            description: "Endpoint-specific"
        outputs:
          type: "dict"
          description: "JSON-serializable response"
        raises:
          - "ConfigurationError"
      logic:
        - "scan(): Delegate to ConnectionManager, format NetworkInfo to JSON"
        - "configure(ssid, password): Delegate to ConnectionManager, return success/error"
        - "status(): Query components, return state/connection info"
    
    - name: "WebServerManager"
      type: "class"
      purpose: "Manage HTTP server lifecycle"
      interface:
        inputs:
          - name: "port"
            type: "int"
            description: "Default 8080"
        outputs:
          type: "None"
        raises:
          - "PortInUseError"
      logic:
        - "start_server(): Create HTTPServer, bind to 0.0.0.0:8080, run in thread"
        - "stop_server(): Shutdown server, join thread"
        - "is_running(): Return server status"
    
    - name: "start_server"
      type: "function"
      purpose: "Public server start"
    
    - name: "stop_server"
      type: "function"
      purpose: "Public server stop"
  
  dependencies:
    internal:
      - "ConnectionManager - for scan_networks(), configure_network()"
      - "StateMonitor - for current_state"
      - "APManager - for is_active()"
    external:
      - "http.server - HTTP server implementation"
      - "json - JSON serialization"
      - "urllib.parse - URL parsing"
      - "threading - non-blocking server"

data_schema:
  entities:
    - name: "ScanResponse"
      attributes:
        - name: "networks"
          type: "array"
          constraints: "Array of {ssid, signal, security, frequency}"
      validation:
        - "Valid JSON format"
    - name: "StatusResponse"
      attributes:
        - name: "state"
          type: "str"
          constraints: "CLIENT, AP_MODE, CHECKING"
        - name: "ssid"
          type: "str or null"
          constraints: "Currently configured network"
        - name: "ap_active"
          type: "bool"
          constraints: "AP mode status"
    - name: "ConfigureRequest"
      attributes:
        - name: "ssid"
          type: "str"
          constraints: "Required"
        - name: "password"
          type: "str"
          constraints: "Required"

error_handling:
  strategy: "HTTP status codes with JSON error responses"
  exceptions:
    - exception: "WebServerError"
      condition: "Base exception"
      handling: "Log, return 500"
    - exception: "PortInUseError"
      condition: "Port 8080 unavailable"
      handling: "Log critical, raise to StateMonitor"
  logging:
    level: "DEBUG for requests, INFO for success, WARNING for invalid requests, ERROR for failures, CRITICAL for port unavailable"
    format: "Logger name 'WebServer'"

testing:
  unit_tests:
    - scenario: "GET / returns HTML"
      expected: "200 OK with HTML content"
    - scenario: "GET /api/scan returns networks"
      expected: "200 OK with JSON network array"
    - scenario: "POST /api/configure with valid data"
      expected: "200 OK with success message"
    - scenario: "POST /api/configure with invalid JSON"
      expected: "400 Bad Request with error"
  edge_cases:
    - "Port 8080 already in use"
    - "Invalid JSON in POST body"
    - "Missing required fields"
    - "Network scan failure"
  validation:
    - "CORS headers present on API responses"
    - "JSON responses properly formatted"
    - "HTML page includes all required elements"

output_format:
  structure: "code_only"
  integration_notes: "brief"

deliverable:
  files:
    - path: "src/webserver.py"
      content: "Complete web server implementation with embedded HTML/CSS/JS"
  documentation:
    - "Integration: Import start_server(), stop_server(), is_running(). Called by StateMonitor for AP_MODE transitions. Runs on 0.0.0.0:8080."

success_criteria:
  - "Server starts on port 8080"
  - "HTML page served at /"
  - "All API endpoints functional"
  - "JSON responses properly formatted"
  - "CORS headers included"
  - "Error handling returns appropriate status codes"
  - "Server stops gracefully"

notes: "Embedded HTML/CSS/JS to avoid external file dependencies. Simple, touch-friendly UI. High contrast design for outdoor use. Depends on ConnectionManager, StateMonitor, APManager."

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

## Design Specification

**Purpose:** HTTP interface for network configuration during AP mode.

**Endpoints:**

- `GET /` → HTML configuration page
- `GET /api/scan` → `{"networks": [{"ssid": "...", "signal": 85, "security": "WPA2", "frequency": "2.4GHz"}]}`
- `GET /api/status` → `{"state": "AP_MODE", "ssid": "...", "ap_active": true}`
- `POST /api/configure` (body: `{"ssid": "...", "password": "..."}`) → `{"success": true, "message": "..."}`

**HTML Interface:**
- Network scan button
- Network list (auto-populated)
- SSID input field
- Password input field
- Connect button
- Status message area
- Responsive, touch-friendly, high contrast

**Error Responses:**
- 400: Invalid JSON or missing fields
- 404: Unknown path
- 500: Server errors

**Exception Hierarchy:** WebServerError → ServerStartError, PortInUseError

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
