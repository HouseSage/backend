#!/usr/bin/env python3
"""
Test runner for space and domain flow tests.
This script runs all tests in the correct order and provides detailed output.
"""

import sys
import traceback
from test_space_pixel_domain_flow import *

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
    """Run all tests in sequence."""
    print("🚀 Starting Space and Domain Flow Tests")
    print(f"Target URL: {BASE_URL}")
    
    # Define test order
    tests = [
        ("Setup Users", test_01_setup_users),
        ("Create Space Unauthorized", test_02_create_space_unauth),
        ("Create Space User A", test_03_create_space_userA),
        ("Read Space Unauthorized", test_04_read_space_unauth),
        ("Update Space User A", test_05_update_space_userA),
        ("Update Space User B Forbidden", test_06_update_space_userB_forbidden),
        ("Delete Space User B Forbidden", test_07_delete_space_userB_forbidden),
        ("Create Pixel User A", test_08_create_pixel_userA),
        ("Link Pixel User A", test_09_link_pixel_userA),
        ("Unlink Pixel User A", test_10_unlink_pixel_userA),
        ("User B Cannot Read Pixel", test_11_userB_cannot_read_pixel),
        ("User B Cannot Update Pixel", test_12_userB_cannot_update_pixel),
        ("Delete Pixel User A", test_13_delete_pixel_userA),
        ("Create Domain User A", test_15_create_domain_userA),
        ("Create Domain Unauthorized", test_16_create_domain_unauth),
        ("List Domains for Space User A", test_17_list_domains_for_space_userA),
        ("User B Cannot Read Domain", test_18_userB_cannot_read_domain),
        ("Delete Domain User B Forbidden", test_21_delete_domain_userB_forbidden),
        ("Delete Domain User A", test_22_delete_domain_userA),
        ("Delete Space User A", test_99_delete_space_userA),
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