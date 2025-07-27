#!/usr/bin/env python3
"""
Test runner for link flow tests.
This script runs all link flow tests in sequence and provides detailed output.
"""

import sys
import traceback
from test_link_flow import *

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
    """Run all link flow tests in sequence."""
    print("🚀 Starting Link Flow Tests")
    print(f"Target URL: {BASE}")
    
    # Define test order
    tests = [
        ("Bootstrap Users and Spaces", test_01_users_spaces),
        ("Create Pixel and Domain", test_02_pixel_domain),
        ("Create Minimal Link", test_03_create_minimal_link),
        ("Create Minimal Link without Space", test_03a_create_minimal_link_without_space),
        ("Create Full Link", test_04_create_full_link),
        ("Create Bad URL", test_05_create_bad_url),
        ("Create Duplicate Short Code", test_06_create_duplicate_shortcode),
        ("List Links with Space Filter", test_07_list_links_space_filter),
        ("Read Link Unauthenticated", test_08_read_link_unauth),
        ("Update Title and Tags", test_09_update_title_tags),
        ("Toggle Is Active", test_10_toggle_is_active),
        ("Password Flow", test_11_password_flow),
        ("Expired Link", test_12_expired_link),
        ("Inactive Link Redirect", test_13_inactive_link_redirect),
        ("User B Cannot Update or Delete", test_14_userB_cannot_update_or_delete),
        ("Delete Link User A", test_15_delete_link_userA),
        ("Cleanup Space", test_99_cleanup_space),
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