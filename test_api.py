#!/usr/bin/env python3
"""
Simple test script to verify the Songs API is working
Run this after starting the API server to test basic functionality
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    """Test basic API functionality"""
    print("🧪 Testing Songs API...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure it's running on http://localhost:8000")
        return False
    
    # Test creating a song
    test_song = {
        "title": "Test Song",
        "artist": "Test Artist",
        "user": "test_user",
        "genre": "Test Genre",
        "year": 2023
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/songs", json=test_song)
        if response.status_code == 201:
            print("✅ Song creation passed")
            song_data = response.json()
            song_id = song_data["id"]
            print(f"   Created song ID: {song_id}")
        else:
            print(f"❌ Song creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Song creation error: {e}")
        return False
    
    # Test getting songs
    try:
        response = requests.get(f"{API_BASE_URL}/songs?user=test_user")
        if response.status_code == 200:
            songs = response.json()
            print(f"✅ Get songs passed - Found {len(songs)} songs")
        else:
            print(f"❌ Get songs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get songs error: {e}")
        return False
    
    # Test searching songs
    try:
        response = requests.get(f"{API_BASE_URL}/songs/search?q=test&user=test_user")
        if response.status_code == 200:
            search_result = response.json()
            print(f"✅ Search songs passed - Found {search_result['total_count']} results")
        else:
            print(f"❌ Search songs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Search songs error: {e}")
        return False
    
    # Test updating a song
    try:
        update_data = {"genre": "Updated Genre"}
        response = requests.put(f"{API_BASE_URL}/songs/{song_id}?user=test_user", json=update_data)
        if response.status_code == 200:
            print("✅ Song update passed")
        else:
            print(f"❌ Song update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Song update error: {e}")
        return False
    
    # Test playing a song
    try:
        response = requests.post(f"{API_BASE_URL}/songs/{song_id}/play?user=test_user")
        if response.status_code == 200:
            print("✅ Play song passed")
        else:
            print(f"❌ Play song failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Play song error: {e}")
        return False
    
    # Test getting user stats
    try:
        response = requests.get(f"{API_BASE_URL}/users/test_user/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ User stats passed - Total songs: {stats['total_songs']}")
        else:
            print(f"❌ User stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User stats error: {e}")
        return False
    
    # Test deleting a song
    try:
        response = requests.delete(f"{API_BASE_URL}/songs/{song_id}?user=test_user")
        if response.status_code == 200:
            print("✅ Song deletion passed")
        else:
            print(f"❌ Song deletion failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Song deletion error: {e}")
        return False
    
    print("\n🎉 All API tests passed!")
    return True

if __name__ == "__main__":
    print("Starting API tests in 2 seconds...")
    time.sleep(2)
    test_api()
