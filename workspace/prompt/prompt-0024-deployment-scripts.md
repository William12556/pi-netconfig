Created: 2025 December 05

```yaml
prompt_info:
  id: "prompt-0024"
  task_type: "code_generation"
  source_ref: "change-0024-deployment-scripts.md"
  date: "2025-12-05"
  priority: "medium"
  iteration: 1
  coupled_docs:
    change_ref: "change-0024"
    change_iteration: 1

context:
  purpose: "Automate build and deployment with version verification"
  integration: "Shell scripts in project root for Mac build and Pi deployment"
  knowledge_references: []
  constraints:
    - "Bash/sh compatibility"
    - "Standard Unix tools only"
    - "Exit codes: 0 success, 1 failure"

specification:
  description: "Create build.sh, install.sh, and update __init__.py for version control"
  requirements:
    functional:
      - "build.sh: Extract version, update __init__.py, build wheel, verify"
      - "install.sh: Parse version, clean uninstall, install, verify, manage service"
      - "__init__.py: Export __version__ variable"
    technical:
      language: "Bash"
      version: "Compatible with MacOS and Debian"
      standards:
        - "Executable permissions (chmod +x)"
        - "Clear error messages"
        - "Idempotent operations"
  performance: []

design:
  architecture: "Two independent shell scripts plus Python module modification"
  components:
    - name: "build.sh"
      type: "shell script"
      purpose: "Automated build with version verification"
      interface:
        inputs: []
        outputs:
          type: "wheel file in dist/"
          description: "Built package with verified version"
        raises: []
      logic:
        - "Extract version from pyproject.toml using grep/cut"
        - "Update src/pi_netconfig/__init__.py with __version__ = 'X.Y.Z'"
        - "Clean dist/, build/, *.egg-info/"
        - "Run python3 -m build"
        - "Verify wheel exists: dist/pi_netconfig-X.Y.Z-py3-none-any.whl"
        - "Display success message with version and filename"
    
    - name: "install.sh"
      type: "shell script"
      purpose: "Clean deployment with version verification"
      interface:
        inputs:
          - name: "$1"
            type: "string"
            description: "Wheel filename (e.g., pi_netconfig-0.2.6-py3-none-any.whl)"
        outputs:
          type: "installed package"
          description: "Verified installation with service running"
        raises: []
      logic:
        - "Require wheel filename argument, exit if missing"
        - "Extract version from filename using cut"
        - "Stop pi-netconfig service (ignore errors if not running)"
        - "Uninstall: sudo /opt/pi-netconfig/venv/bin/pip uninstall -y pi_netconfig"
        - "Clean cache: sudo rm -rf /opt/pi-netconfig/venv/lib/python*/site-packages/pi_netconfig*"
        - "Install: sudo /opt/pi-netconfig/venv/bin/pip install /tmp/$1"
        - "Verify: Check installed version matches expected"
        - "Start service: sudo systemctl start pi-netconfig"
        - "Display status and version"
    
    - name: "__init__.py"
      type: "Python module"
      purpose: "Export version for runtime access"
      interface:
        inputs: []
        outputs:
          type: "module attribute"
          description: "__version__ string"
        raises: []
      logic:
        - "Add __version__ = 'VERSION' at module level"
        - "Maintained by build.sh, not manually edited"
  
  dependencies:
    internal: []
    external:
      - "grep, cut, sed (Unix text tools)"
      - "python3, pip (Python tools)"
      - "systemctl (systemd)"

data_schema:
  entities: []

error_handling:
  strategy: "Exit immediately on error with descriptive message"
  exceptions: []
  logging:
    level: "stdout messages"
    format: "Clear success/failure indicators"

testing:
  unit_tests: []
  edge_cases:
    - "build.sh: pyproject.toml missing"
    - "build.sh: build fails"
    - "install.sh: no argument provided"
    - "install.sh: version mismatch"
  validation:
    - "Scripts exit 0 on success"
    - "Scripts exit 1 on failure"
    - "Version verification catches mismatches"

deliverable:
  format_requirements:
    - "Executable shell scripts"
    - "Clear comments in scripts"
  files:
    - path: "build.sh"
      content: |
        #!/bin/bash
        # Build script with version verification
        # Usage: ./build.sh
        
        set -e  # Exit on error
        
        # Extract version from pyproject.toml
        VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
        
        if [ -z "$VERSION" ]; then
            echo "ERROR: Could not extract version from pyproject.toml"
            exit 1
        fi
        
        echo "Building pi-netconfig version $VERSION"
        
        # Update __init__.py with version
        echo "__version__ = '$VERSION'" > src/pi_netconfig/__init__.py
        
        # Clean previous builds
        rm -rf dist/ build/ *.egg-info/
        
        # Build wheel
        python3 -m build
        
        # Verify wheel exists
        WHEEL="dist/pi_netconfig-${VERSION}-py3-none-any.whl"
        if [ ! -f "$WHEEL" ]; then
            echo "ERROR: Expected wheel not found: $WHEEL"
            exit 1
        fi
        
        echo "✓ Build successful: $WHEEL"
        ls -lh "$WHEEL"
    
    - path: "install.sh"
      content: |
        #!/bin/bash
        # Install script with version verification
        # Usage: ./install.sh <wheel-filename>
        
        set -e  # Exit on error
        
        if [ -z "$1" ]; then
            echo "ERROR: Wheel filename required"
            echo "Usage: ./install.sh pi_netconfig-X.Y.Z-py3-none-any.whl"
            exit 1
        fi
        
        WHEEL="$1"
        VERSION=$(echo "$WHEEL" | cut -d'-' -f2)
        
        echo "Installing pi-netconfig version $VERSION"
        
        # Stop service (ignore if not running)
        sudo systemctl stop pi-netconfig || true
        
        # Uninstall existing package
        echo "Cleaning existing installation..."
        sudo /opt/pi-netconfig/venv/bin/pip uninstall -y pi_netconfig || true
        
        # Clear cache
        sudo rm -rf /opt/pi-netconfig/venv/lib/python*/site-packages/pi_netconfig*
        
        # Install new version
        echo "Installing from /tmp/$WHEEL"
        sudo /opt/pi-netconfig/venv/bin/pip install "/tmp/$WHEEL"
        
        # Verify version
        INSTALLED=$(/opt/pi-netconfig/venv/bin/python -c "import pi_netconfig; print(pi_netconfig.__version__)")
        
        if [ "$INSTALLED" != "$VERSION" ]; then
            echo "ERROR: Version mismatch - expected $VERSION, got $INSTALLED"
            exit 1
        fi
        
        # Start service
        sudo systemctl start pi-netconfig
        
        echo "✓ Installation successful: version $INSTALLED"
        sudo systemctl status pi-netconfig --no-pager -l
    
    - path: "src/pi_netconfig/__init__.py"
      content: |
        """Pi Network Configuration Tool
        
        Automated WiFi configuration with fallback access point.
        """
        
        __version__ = "0.2.6"

success_criteria:
  - "build.sh creates wheel with correct version"
  - "install.sh deploys and verifies version"
  - "Scripts exit with proper codes"
  - "Version accessible via import pi_netconfig.__version__"

notes: |
  Scripts designed for human execution, not CI/CD.
  Both are idempotent and safe to run multiple times.

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t04_prompt"
```

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
