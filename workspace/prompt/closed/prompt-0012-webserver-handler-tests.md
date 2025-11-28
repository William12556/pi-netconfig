Created: 2025 November 26

# T04 Prompt: WebServer Handler Test Refactor

```yaml
prompt_info:
  id: "prompt-0012"
  task_type: "test_refactor"
  source_ref: "change-0009-webserver-handler-test-methodology"
  date: "2025-11-26"
  priority: "high"

mcp_config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.2
  max_tokens: 8192
  system_prompt: "Expert Python test developer. Output: corrected test methods only."

context:
  purpose: "Refactor handler tests to avoid BaseHTTPRequestHandler instantiation"
  integration: "Replace 13 test methods in src/tests/webserver/test_webserver.py"

specification:
  approach: "Test methods directly using Mock handler with injected attributes"
  pattern: |
    def test_METHOD(self):
        handler = Mock(spec=ConfigHTTPHandler)
        handler.path = '/target/path'
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        
        ConfigHTTPHandler.METHOD(handler)
        
        # Assertions

targets:
  handler_tests:
    - "test_do_get_serves_html_for_root"
    - "test_do_get_handles_scan_request"
    - "test_do_get_handles_status_request"
    - "test_do_get_returns_404_for_unknown_path"
    - "test_do_post_handles_configure_request"
    - "test_do_post_validates_ssid_required"
    - "test_do_post_validates_password_required"
    - "test_do_post_returns_404_for_unknown_path"
    - "test_send_json_response_includes_cors_headers"
  
  manager_tests:
    - "test_stop_server_shuts_down_gracefully"
    - "test_stop_server_joins_thread"
    - "test_start_server_uses_default_port"
    - "test_start_server_raises_port_in_use_error"

implementation:
  example_get_test: |
    def test_do_get_serves_html_for_root(self):
        """GET / returns HTML configuration page."""
        handler = Mock(spec=ConfigHTTPHandler)
        handler.path = '/'
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        
        ConfigHTTPHandler.do_GET(handler)
        
        handler.send_response.assert_called_once_with(200)
        handler.send_header.assert_any_call('Content-type', 'text/html')
        assert b'<!DOCTYPE html>' in handler.wfile.write.call_args[0][0]

  example_post_test: |
    def test_do_post_handles_configure_request(self):
        """POST /api/configure processes network configuration."""
        handler = Mock(spec=ConfigHTTPHandler)
        handler.path = '/api/configure'
        handler.headers = {'Content-Length': '30'}
        handler.rfile = Mock()
        handler.rfile.read = Mock(return_value=b'{"ssid":"TestNet","password":"pass123"}')
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        
        with patch('webserver.configure_network', return_value=True):
            ConfigHTTPHandler.do_POST(handler)
        
        handler.send_response.assert_called_once_with(200)

  manager_fix: |
    def test_stop_server_shuts_down_gracefully(self):
        """stop_server() shuts down and closes server."""
        manager = WebServerManager(port=8080)
        mock_server = Mock()
        manager.server = mock_server
        manager.server_thread = Mock()
        
        manager.stop_server()
        
        mock_server.shutdown.assert_called_once()
        mock_server.server_close.assert_called_once()

deliverable:
  code: "13 corrected test methods"
  integration: "Replace methods in test_webserver.py"
  notes: "Adjust imports if needed; maintain existing test structure"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
