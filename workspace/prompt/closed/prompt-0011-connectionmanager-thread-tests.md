Created: 2025 November 26

# T04 Prompt: ConnectionManager Thread-Safety Test Refactor

```yaml
prompt_info:
  id: "prompt-0011"
  task_type: "test_refactor"
  source_ref: "change-0008-connectionmanager-thread-test-refactoring"
  date: "2025-11-26"
  priority: "medium"

mcp_config:
  model: "claude-sonnet-4-20250514"
  temperature: 0.2
  max_tokens: 4096
  system_prompt: "Expert Python test developer. Output: corrected test methods only."

context:
  purpose: "Replace lock-patching tests with concurrent execution tests"
  integration: "Replace 3 test methods in src/tests/connectionmanager/test_connectionmanager.py"

specification:
  targets:
    - "test_configure_network_thread_safe"
    - "test_persist_configuration_thread_safe"
    - "test_load_configuration_thread_safe"
  approach: "Spawn threads, execute operations concurrently, collect errors"

implementation:
  pattern: |
    def test_METHOD_thread_safe(self):
        """Verify METHOD handles concurrent calls."""
        results = []
        errors = []
        
        def worker(identifier):
            try:
                # Execute target method with mock/temp data
                results.append(identifier)
            except Exception as e:
                errors.append(e)
        
        threads = [Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Concurrent calls raised errors: {errors}"
        assert len(results) == 10

  test_1: |
    def test_configure_network_thread_safe(self):
        """Verify configure_network handles concurrent calls."""
        with patch('subprocess.run'), patch.object(ConfigManager, 'persist_configuration'):
            results = []
            errors = []
            
            def worker(i):
                try:
                    ConfigManager.configure_network(f"TestSSID{i}", "password123")
                    results.append(i)
                except Exception as e:
                    errors.append(e)
            
            threads = [Thread(target=worker, args=(i,)) for i in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            assert len(errors) == 0, f"Errors: {errors}"
            assert len(results) == 10

  test_2: |
    def test_persist_configuration_thread_safe(self):
        """Verify persist_configuration handles concurrent calls."""
        with TemporaryDirectory() as tmpdir:
            with patch.object(ConfigManager, 'CONFIG_PATH', Path(tmpdir) / 'config.json'):
                results = []
                errors = []
                
                def worker(i):
                    try:
                        ConfigManager.persist_configuration(f"SSID{i}")
                        results.append(i)
                    except Exception as e:
                        errors.append(e)
                
                threads = [Thread(target=worker, args=(i,)) for i in range(10)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
                
                assert len(errors) == 0
                assert len(results) == 10

  test_3: |
    def test_load_configuration_thread_safe(self):
        """Verify load_configuration handles concurrent calls."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.json'
            config_path.write_text('{"configured_ssid": "TestSSID"}')
            
            with patch.object(ConfigManager, 'CONFIG_PATH', config_path):
                results = []
                errors = []
                
                def worker(i):
                    try:
                        ssid = ConfigManager.load_configuration()
                        results.append(ssid)
                    except Exception as e:
                        errors.append(e)
                
                threads = [Thread(target=worker, args=(i,)) for i in range(10)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
                
                assert len(errors) == 0
                assert len(results) == 10
                assert all(r == "TestSSID" for r in results)

deliverable:
  code: "3 corrected test methods"
  integration: "Replace methods in test_connectionmanager.py"
  imports: "Add: from threading import Thread"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
