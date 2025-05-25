#!/usr/bin/env python3
"""Setup and run script for Pokemon Go MCP Server."""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    if description:
        print(f"🚀 {description}")
    print(f"Running: {' '.join(cmd)}")
    print('='*50)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ Success: {description if description else 'Command completed'}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description if description else 'Command failed'}")
        print(f"Exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Please make sure the required tools are installed.")
        return False


def setup_environment():
    """Set up the development environment."""
    print("🏗️  Setting up Pokemon Go MCP Server development environment...")
    
    # Check if uv is available
    if subprocess.run(["uv", "--version"], capture_output=True).returncode == 0:
        print("✅ Found uv package manager")
        
        # Install dependencies
        if not run_command(["uv", "sync", "--all-extras", "--dev"], "Installing dependencies with uv"):
            return False
            
    else:
        print("⚠️  uv not found, falling back to pip")
        
        # Create virtual environment if it doesn't exist
        if not Path("venv").exists():
            if not run_command([sys.executable, "-m", "venv", "venv"], "Creating virtual environment"):
                return False
        
        # Activate and install
        if os.name == 'nt':  # Windows
            pip_cmd = ["venv\\Scripts\\pip"]
        else:  # Unix-like
            pip_cmd = ["venv/bin/pip"]
        
        if not run_command(pip_cmd + ["install", "-e", ".[dev,cli]"], "Installing with pip"):
            return False
    
    print("\n🎉 Environment setup complete!")
    return True


def run_tests():
    """Run the test suite."""
    print("🧪 Running test suite...")
    
    if subprocess.run(["uv", "--version"], capture_output=True).returncode == 0:
        return run_command(["uv", "run", "pytest", "-v"], "Running tests with uv")
    else:
        if os.name == 'nt':  # Windows
            python_cmd = ["venv\\Scripts\\python"]
        else:  # Unix-like
            python_cmd = ["venv/bin/python"]
        
        return run_command(python_cmd + ["-m", "pytest", "-v"], "Running tests with venv")


def run_server(dev_mode=False):
    """Run the MCP server."""
    if dev_mode:
        print("🔧 Starting server in development mode...")
        if subprocess.run(["uv", "--version"], capture_output=True).returncode == 0:
            return run_command(["uv", "run", "mcp", "dev", "server.py"], "Starting development server")
        else:
            print("❌ Development mode requires uv. Please install uv or use --prod mode.")
            return False
    else:
        print("🚀 Starting Pokemon Go MCP Server...")
        if subprocess.run(["uv", "--version"], capture_output=True).returncode == 0:
            return run_command(["uv", "run", "python", "server.py"], "Starting server with uv")
        else:
            if os.name == 'nt':  # Windows
                python_cmd = ["venv\\Scripts\\python"]
            else:  # Unix-like
                python_cmd = ["venv/bin/python"]
            
            return run_command(python_cmd + ["server.py"], "Starting server with venv")


def lint_code():
    """Run code linting and formatting."""
    print("🔍 Running code quality checks...")
    
    success = True
    
    if subprocess.run(["uv", "--version"], capture_output=True).returncode == 0:
        # Format code
        success &= run_command(["uv", "run", "ruff", "format", "."], "Formatting code")
        # Check linting
        success &= run_command(["uv", "run", "ruff", "check", "."], "Linting code")
        # Type checking
        success &= run_command(["uv", "run", "pyright"], "Type checking")
    else:
        print("⚠️  uv not found, skipping lint checks")
        print("Install uv for the best development experience: https://docs.astral.sh/uv/")
    
    return success


def install_in_claude():
    """Install the server in Claude Desktop."""
    print("🤖 Installing in Claude Desktop...")
    
    if subprocess.run(["uv", "--version"], capture_output=True).returncode == 0:
        server_path = Path.cwd() / "server.py"
        return run_command([
            "uv", "run", "mcp", "install", str(server_path), 
            "--name", "Pokemon Go Data"
        ], "Installing in Claude Desktop")
    else:
        print("❌ Claude Desktop integration requires uv package manager")
        print("Please install uv: https://docs.astral.sh/uv/")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Pokemon Go MCP Server Setup and Runner")
    parser.add_argument("command", choices=[
        "setup", "test", "run", "dev", "lint", "claude", "all"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    print("🎮 Pokemon Go MCP Server")
    print("=" * 40)
    
    if args.command == "setup":
        setup_environment()
        
    elif args.command == "test":
        run_tests()
        
    elif args.command == "run":
        run_server(dev_mode=False)
        
    elif args.command == "dev":
        run_server(dev_mode=True)
        
    elif args.command == "lint":
        lint_code()
        
    elif args.command == "claude":
        install_in_claude()
        
    elif args.command == "all":
        print("🎯 Running complete setup and validation...")
        success = True
        success &= setup_environment()
        success &= lint_code()
        success &= run_tests()
        
        if success:
            print("\n🎉 All checks passed! You can now run:")
            print("  python run.py run    # Start the server")
            print("  python run.py dev    # Start in development mode")
            print("  python run.py claude # Install in Claude Desktop")
        else:
            print("\n❌ Some checks failed. Please review the output above.")
            sys.exit(1)


if __name__ == "__main__":
    main()
