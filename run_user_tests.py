#!/usr/bin/env python3
"""
Test runner for user flow tests.
This script runs all user flow tests in sequence and provides detailed output.
"""

import sys
import traceback
from test_user_flow import *

def run_test(test_name, test_func):
    """Run a single test and handle exceptions."""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")
    
    try:
        test_func()
        print(f"✅ PASS: {test_name}")
        return True
    except Exception as e:
        print(f"❌ FAIL: {test_name}")
        print(f"Error: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()
        return False

def main():
    """Run all user flow tests in sequence."""
    print("🚀 Starting User Flow Tests")
    print(f"Target URL: {BASE_URL}")
    
    # Define test order
    tests = [
        ("Create Valid User", test_create_valid_user),
        ("Create User with Invalid Email", test_create_user_invalid_email),
        ("Create User with Short Password", test_create_user_short_password),
        ("Create User with Duplicate Email", test_create_user_duplicate_email),
        ("Login with Correct Credentials", test_login_success),
        ("Access Profile Unauthenticated", test_get_user_profile_unauthenticated),
        ("Access Profile with Token", test_get_user_profile_authenticated),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total: {passed + failed}")
    
    if failed == 0:
        print(f"\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 {failed} test(s) failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 