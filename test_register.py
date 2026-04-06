#!/usr/bin/env python3
"""
Test script to verify registration works
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Test 1: Register via JSON
print("=" * 50)
print("Test 1: Register via JSON")
print("=" * 50)

register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User",
}

response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json=register_data,
    headers={"Content-Type": "application/json"},
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

# Test 2: Try to register duplicate user
print("\n" + "=" * 50)
print("Test 2: Register duplicate user (should fail)")
print("=" * 50)

response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json=register_data,
    headers={"Content-Type": "application/json"},
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

# Test 3: Register with short password
print("\n" + "=" * 50)
print("Test 3: Register with short password (should fail)")
print("=" * 50)

bad_data = {
    "username": "testuser2",
    "email": "test2@example.com",
    "password": "short",
    "full_name": "Test User 2",
}

response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json=bad_data,
    headers={"Content-Type": "application/json"},
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

print("\n✅ Registration tests complete!")
