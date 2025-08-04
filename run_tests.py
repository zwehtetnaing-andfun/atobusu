#!/usr/bin/env python3
"""
Test runner for Atobusu application.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests using pytest."""
    try:
        # Run pytest with coverage
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--cov=atobusu",
            "--cov-report=term-missing"
        ], check=True)
        
        print("\n✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install test dependencies:")
        print("pip install pytest pytest-cov")
        return False


def main():
    """Main entry point."""
    print("🧪 Running Atobusu tests...")
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    if not (project_root / "atobusu").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    success = run_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()