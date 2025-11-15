Created: 2025 November 14

# Issue: pytest-asyncio Not Installed or Configured

```yaml
issue_info:
  id: "issue-0006"
  title: "pytest-asyncio warnings: Unknown config option and mark - async tests cannot execute"
  date: "2025-11-14"
  reporter: "Domain 1"
  status: "open"
  severity: "high"
  type: "defect"

source:
  origin: "test_result"
  test_ref: "pytest execution - 22 warnings"
  description: "pytest reports unknown config option 'asyncio_mode' and unknown mark 'pytest.mark.asyncio', indicating pytest-asyncio plugin not properly installed despite being in pyproject.toml dependencies"

affected_scope:
  components:
    - name: "test environment"
      file_path: "pyproject.toml [project.optional-dependencies.dev]"
    - name: "test_statemonitor.py"
      file_path: "src/tests/statemonitor/test_statemonitor.py"
  designs:
    - design_ref: "test-0003-statemonitor.md"
  version: "0.2.0"

reproduction:
  steps:
    - "Execute: pytest src/tests/"
    - "Observe 22 warnings about unknown asyncio marks"
    - "Observe warning about unknown config option"
  frequency: "always"
  preconditions: "pytest execution environment"
  test_data: "N/A"
  error_output: |
    PytestConfigWarning: Unknown config option: asyncio_mode
    PytestUnknownMarkWarning: Unknown pytest.mark.asyncio - is this a typo?

behavior:
  expected: "pytest-asyncio plugin recognizes @pytest.mark.asyncio decorators and async test functions execute properly"
  actual: "pytest treats @pytest.mark.asyncio as unknown mark, async tests may not execute correctly"
  impact: |
    - 20 async test functions in test_statemonitor.py may not execute properly
    - asyncio_mode configuration ignored
    - Potential test failures or incorrect test execution
  workaround: "Install pytest-asyncio: pip install pytest-asyncio"

environment:
  python_version: "3.9.6"
  os: "Darwin"
  dependencies:
    - library: "pytest-asyncio"
      version: ">=0.21.0 (specified but apparently not installed)"
  domain: "test_environment"

analysis:
  root_cause: |
    pyproject.toml specifies pytest-asyncio>=0.21.0 in [project.optional-dependencies.dev]
    but package appears not installed in test execution environment.
    
    Possible causes:
    1. Development dependencies not installed (pip install -e .[dev] not executed)
    2. Virtual environment issue
    3. pytest discovering tests but plugin not loaded
    
    Evidence:
    - pytest successfully loaded: pytest-8.4.1
    - pytest-cov loaded: plugins: cov-6.2.1
    - pytest-mock loaded: plugins: mock-3.14.1
    - pytest-asyncio NOT listed in loaded plugins
  
  technical_notes: |
    pyproject.toml configuration:
    [project.optional-dependencies]
    dev = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",  # Specified
        "pytest-cov>=4.0.0",
    ]
    
    [tool.pytest.ini_options]
    asyncio_mode = "auto"  # Configuration exists but not recognized
    
    Loaded plugins from pytest output:
    plugins: anyio-4.9.0, cov-6.2.1, mock-3.14.1
    
    Notice: anyio loaded (different async plugin) but NOT pytest-asyncio
    
    Impact on test execution:
    - 20 @pytest.mark.asyncio decorated tests in test_statemonitor.py
    - Tests may execute synchronously without proper async handling
    - Async fixtures and context may not work correctly
  
  related_issues: []

resolution:
  assigned_to: "Human"
  target_date: "2025-11-14"
  approach: |
    Install development dependencies:
    
    From project root:
    pip install -e '.[dev]'
    
    Or explicitly:
    pip install pytest-asyncio>=0.21.0
    
    Then re-run tests to verify:
    pytest src/tests/ -v
    
    Expected: pytest-asyncio appears in loaded plugins list
  
  change_ref: ""
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verified_date: ""
  verified_by: ""
  test_results: "After installation, verify plugin loads and warnings disappear"
  closure_notes: ""

traceability:
  design_refs:
    - "test-0003-statemonitor.md"
  change_refs: []
  test_refs:
    - "test-0003-statemonitor.md"

notes: |
  This is an environment configuration issue, not a code defect.
  
  Resolution priority: High (before issue-0005) because:
  - Affects 20 test cases (statemonitor async tests)
  - Quick fix (simple pip install)
  - No code changes required
  
  Alternative: Some test frameworks can execute async tests without pytest-asyncio,
  but explicit plugin installation ensures proper async handling per governance design.

version_history:
  - version: "1.0"
    date: "2025-11-14"
    author: "Domain 1"
    changes:
      - "Initial issue creation from pytest warning analysis"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
