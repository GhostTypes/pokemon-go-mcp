#!/usr/bin/env python3
"""
Test runner script for Pokemon Go MCP scraper tests
Runs all tests with --disable-warnings flag and manages test fixtures
"""

import subprocess
import sys
import os
import shutil
import emoji

def cleanup_fixtures():
    """Remove test fixtures directory"""
    fixtures_dir = os.path.join('tests', 'fixtures')
    if os.path.exists(fixtures_dir):
        print("Cleaning up test fixtures...")
        shutil.rmtree(fixtures_dir)
        print("Test fixtures cleaned up.")
    else:
        print("No test fixtures to clean up.")

def run_tests():
    """Run all tests with --disable-warnings flag"""
    print("Starting tests...")
    
    # Run pytest with disable-warnings flag
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 'tests/', '-v', '--disable-warnings'
    ], capture_output=False, text=True)
    
    return result.returncode

def main():
    """Main function"""
    print("Leekduck Scraper Test Runner")
    print("=" * 30)
    
    # Always cleanup fixtures first to ensure fresh data
    cleanup_fixtures()
    
    # Run tests
    exit_code = run_tests()
    
    print("\nTest run completed.")
    if exit_code == 0:
        print(emoji.emojize("All tests passed! :check_mark_button:"))
    else:
        print(emoji.emojize("Test failure!! :stop_sign:"))
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())