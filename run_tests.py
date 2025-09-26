#!/usr/bin/env python3
"""
Test runner for Songs CLI application
Now uses pytest to run the organized test modules in the test/ folder
"""

import subprocess
import sys
import os

def run_tests():
    """Run the test suite using pytest"""
    print("🎵 Songs CLI - Test Runner")
    print("=" * 40)
    
    # Check if test directory exists
    if not os.path.exists('test'):
        print("❌ Test directory 'test/' not found!")
        return False
    
    # Run tests using pytest
    try:
        result = subprocess.run([sys.executable, '-m', 'pytest', 'test/', '-v'], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_specific_test(test_file):
    """Run a specific test file"""
    print(f"🎵 Running specific test: {test_file}")
    print("=" * 40)
    
    test_path = f"test/{test_file}" if not test_file.startswith('test/') else test_file
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pytest', test_path, '-v'], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        success = run_specific_test(test_file)
    else:
        success = run_tests()
    
    if success:
        print("\n✅ Tests completed successfully!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
