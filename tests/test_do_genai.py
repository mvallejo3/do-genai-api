"""
Test script for DigitalOcean GenAI service.

This script tests basic functionality of the do_genai service.
Run with: python test_do_genai.py
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from services.do_genai import DigitalOceanGenAI

# Load environment variables
load_dotenv()


def test_initialization():
    """Test that the service can be initialized."""
    print("Testing initialization...")
    try:
        client = DigitalOceanGenAI()
        print("✓ Service initialized successfully")
        return client
    except ValueError as e:
        print(f"✗ Initialization failed: {e}")
        print("  Make sure DIGITALOCEAN_API_TOKEN is set in your environment")
        return None
    except Exception as e:
        print(f"✗ Unexpected error during initialization: {e}")
        return None


def test_list_workspaces(client):
    """Test listing workspaces."""
    print("\nTesting list_workspaces...")
    try:
        result = client.list_workspaces()
        print(f"✓ Successfully listed workspaces")
        if 'workspaces' in result:
            print(f"  Found {len(result['workspaces'])} workspace(s)")
        return True
    except Exception as e:
        print(f"✗ Failed to list workspaces: {e}")
        return False


def test_list_models(client):
    """Test listing models."""
    print("\nTesting list_models...")
    try:
        result = client.list_models(public_only=True)
        print(f"✓ Successfully listed models")
        if 'models' in result:
            print(f"  Found {len(result['models'])} model(s)")
        return True
    except Exception as e:
        print(f"✗ Failed to list models: {e}")
        return False


def test_list_knowledge_bases(client):
    """Test listing knowledge bases."""
    print("\nTesting list_knowledge_bases...")
    try:
        result = client.list_knowledge_bases()
        print(f"✓ Successfully listed knowledge bases")
        if 'knowledge_bases' in result:
            print(f"  Found {len(result['knowledge_bases'])} knowledge base(s)")
        return True
    except Exception as e:
        print(f"✗ Failed to list knowledge bases: {e}")
        return False


def test_list_agents(client):
    """Test listing agents."""
    print("\nTesting list_agents...")
    try:
        result = client.list_agents()
        print(f"✓ Successfully listed agents")
        if 'agents' in result:
            print(f"  Found {len(result['agents'])} agent(s)")
        return True
    except Exception as e:
        print(f"✗ Failed to list agents: {e}")
        return False


def test_list_datacenter_regions(client):
    """Test listing datacenter regions."""
    print("\nTesting list_datacenter_regions...")
    try:
        result = client.list_datacenter_regions()
        print(f"✓ Successfully listed datacenter regions")
        if 'regions' in result:
            print(f"  Found {len(result['regions'])} region(s)")
        return True
    except Exception as e:
        print(f"✗ Failed to list datacenter regions: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("DigitalOcean GenAI Service Test")
    print("=" * 60)
    
    # Test initialization
    client = test_initialization()
    if not client:
        print("\n✗ Cannot proceed without a valid client")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_list_workspaces,
        test_list_models,
        test_list_knowledge_bases,
        test_list_agents,
        test_list_datacenter_regions,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test(client):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)


if __name__ == '__main__':
    main()

