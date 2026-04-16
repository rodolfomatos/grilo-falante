"""
Test script for Admin Auth Module.
"""

import asyncio
import sys

sys.path.insert(0, "/home/rodolfo/src/grilo_falante_v3.0")


def test_auth():
    print("=" * 60)
    print("Admin Auth Module - Test")
    print("=" * 60)

    from grilo_admin.auth import (
        create_access_token,
        decode_token,
        get_password_hash,
        user_store,
        verify_password,
    )
    from grilo_admin.models import UserRole

    print("\n1. Testing password hashing...")
    password = "testpassword123"
    hashed = get_password_hash(password)
    print(f"   Password: {password}")
    print(f"   Hash: {hashed[:50]}...")
    assert verify_password(password, hashed), "Password verification failed"
    assert not verify_password("wrongpassword", hashed), "Wrong password should fail"
    print("   ✅ Password hashing works")

    print("\n2. Testing JWT token creation...")
    token, expires_in = create_access_token(
        user_id="test-user-123",
        email="test@example.com",
        role=UserRole.ADMIN,
    )
    print(f"   Token: {token[:50]}...")
    print(f"   Expires in: {expires_in} seconds")
    assert token, "Token should not be empty"
    print("   ✅ JWT creation works")

    print("\n3. Testing JWT token decoding...")
    token_data = decode_token(token)
    assert token_data, "Token data should not be None"
    assert token_data.user_id == "test-user-123", "User ID mismatch"
    assert token_data.email == "test@example.com", "Email mismatch"
    assert token_data.role == UserRole.ADMIN, "Role mismatch"
    print(f"   Decoded user_id: {token_data.user_id}")
    print(f"   Decoded email: {token_data.email}")
    print(f"   Decoded role: {token_data.role.value}")
    print("   ✅ JWT decoding works")

    print("\n4. Testing invalid token...")
    invalid = decode_token("invalid.token.here")
    assert invalid is None, "Invalid token should return None"
    print("   ✅ Invalid token handling works")

    print("\n5. Testing user store...")
    users = user_store.list_all()
    print(f"   Total users in store: {len(users)}")
    for user in users:
        print(f"   - {user['email']} ({user['role']})")
    print("   ✅ User store works")

    print("\n6. Testing default admin credentials...")
    admin = user_store.get_by_email("admin@example.com")
    assert admin, "Default admin should exist"
    assert admin["role"] == UserRole.ADMIN.value, "Admin role mismatch"
    assert verify_password("admin123", admin["password_hash"]), "Default password mismatch"
    print("   ✅ Default admin credentials work")

    print("\n" + "=" * 60)
    print("All auth tests passed!")
    print("=" * 60)


def test_api():
    print("\n" + "=" * 60)
    print("Admin API - Test")
    print("=" * 60)

    from fastapi.testclient import TestClient
    from grilo_admin import app

    client = TestClient(app)

    print("\n1. Testing health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy", "Health status should be healthy"
    print(f"   Response: {data}")
    print("   ✅ Health endpoint works")

    print("\n2. Testing login with default admin...")
    response = client.post(
        "/auth/users/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )
    assert response.status_code == 200, f"Login failed: {response.status_code}"
    data = response.json()
    assert "access_token" in data, "Response should contain access_token"
    assert data["user"]["email"] == "admin@example.com", "Email mismatch"
    token = data["access_token"]
    print(f"   Token: {token[:30]}...")
    print(f"   User: {data['user']['email']} ({data['user']['role']})")
    print("   ✅ Login works")

    print("\n3. Testing protected route with token...")
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, f"Protected route failed: {response.status_code}"
    data = response.json()
    print(f"   Response: {data}")
    print("   ✅ Protected route works")

    print("\n4. Testing protected route without token...")
    response = client.get("/protected")
    assert response.status_code in (401, 403), f"Should return 401/403 without token, got {response.status_code}"
    print("   ✅ Missing token handling works")

    print("\n5. Testing wrong credentials...")
    response = client.post(
        "/auth/users/login",
        json={"email": "admin@example.com", "password": "wrongpassword"},
    )
    assert response.status_code in (401, 422), f"Should return 401/422 for wrong password, got {response.status_code}"
    print("   ✅ Wrong password handling works")

    print("\n6. Testing list users (admin)...")
    response = client.get(
        "/auth/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, f"List users failed: {response.status_code}"
    data = response.json()
    print(f"   Users: {len(data)}")
    print("   ✅ List users works")

    print("\n" + "=" * 60)
    print("All API tests passed!")
    print("=" * 60)


def test_system_endpoints():
    print("\n" + "=" * 60)
    print("System Endpoints - Test")
    print("=" * 60)

    from fastapi.testclient import TestClient
    from grilo_admin import app

    client = TestClient(app)

    print("\n1. Getting admin token...")
    response = client.post(
        "/auth/users/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    print(f"   Token obtained")

    auth_headers = {"Authorization": f"Bearer {token}"}

    print("\n2. Testing system status...")
    response = client.get("/admin/system/status", headers=auth_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Uptime: {data.get('uptime_human', 'N/A')}")
        print(f"   Plugins: {data.get('plugins', {}).get('total', 0)}")
        print("   ✅ System status works")
    else:
        print(f"   ⚠️ Status code: {response.status_code}")

    print("\n3. Testing system health...")
    response = client.get("/admin/system/health", headers=auth_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Healthy: {data.get('healthy', 'N/A')}")
        print("   ✅ System health works")
    else:
        print(f"   ⚠️ Status code: {response.status_code}")

    print("\n4. Testing plugins list...")
    response = client.get("/admin/plugins", headers=auth_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Total plugins: {data.get('total', 0)}")
        print("   ✅ Plugins list works")
    else:
        print(f"   ⚠️ Status code: {response.status_code}")

    print("\n5. Testing cache clear (admin only)...")
    response = client.post("/admin/system/cache/clear", headers=auth_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Cache clear works (admin)")
    else:
        print(f"   ⚠️ Status code: {response.status_code}")

    print("\n" + "=" * 60)
    print("System endpoints tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_auth()
    test_api()
    test_system_endpoints()
