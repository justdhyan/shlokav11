#!/usr/bin/env python3
"""
SHLOKA Backend API Testing Suite
Tests all backend APIs for the Bhagavad Gita guidance app
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Backend URL from frontend environment
BACKEND_URL = "https://repo-finisher-4.preview.emergentagent.com/api"

class SHLOKAAPITester:
    def __init__(self):
        self.results = {
            "emotions_api": {"passed": False, "errors": []},
            "moods_api": {"passed": False, "errors": []},
            "guidance_api": {"passed": False, "errors": []},
            "error_handling": {"passed": False, "errors": []}
        }
        self.session = requests.Session()
        self.session.timeout = 10

    def test_emotions_api(self):
        """Test GET /api/emotions endpoint"""
        print("🧪 Testing Emotions API...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/emotions")
            
            if response.status_code != 200:
                self.results["emotions_api"]["errors"].append(f"Status code: {response.status_code}")
                return
            
            emotions = response.json()
            
            # Verify it's a list
            if not isinstance(emotions, list):
                self.results["emotions_api"]["errors"].append("Response is not a list")
                return
            
            # Verify we have 5 emotions
            if len(emotions) != 5:
                self.results["emotions_api"]["errors"].append(f"Expected 5 emotions, got {len(emotions)}")
                return
            
            # Verify structure of each emotion
            expected_fields = ["_id", "name_english", "name_sanskrit", "description", "icon"]
            expected_emotion_ids = ["fear", "anger", "grief", "confusion", "detachment"]
            
            found_emotion_ids = []
            for emotion in emotions:
                # Check all required fields exist
                for field in expected_fields:
                    if field not in emotion:
                        self.results["emotions_api"]["errors"].append(f"Missing field '{field}' in emotion")
                        return
                
                found_emotion_ids.append(emotion["_id"])
                
                # Verify data types and content
                if not isinstance(emotion["name_english"], str) or not emotion["name_english"]:
                    self.results["emotions_api"]["errors"].append(f"Invalid name_english for emotion {emotion['_id']}")
                    return
                
                if not isinstance(emotion["name_sanskrit"], str) or not emotion["name_sanskrit"]:
                    self.results["emotions_api"]["errors"].append(f"Invalid name_sanskrit for emotion {emotion['_id']}")
                    return
            
            # Verify all expected emotion IDs are present
            for expected_id in expected_emotion_ids:
                if expected_id not in found_emotion_ids:
                    self.results["emotions_api"]["errors"].append(f"Missing emotion ID: {expected_id}")
                    return
            
            self.results["emotions_api"]["passed"] = True
            print("✅ Emotions API test passed")
            
        except requests.exceptions.RequestException as e:
            self.results["emotions_api"]["errors"].append(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            self.results["emotions_api"]["errors"].append(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            self.results["emotions_api"]["errors"].append(f"Unexpected error: {str(e)}")

    def test_moods_api(self):
        """Test GET /api/moods/{emotion_id} endpoint"""
        print("🧪 Testing Moods API...")
        
        emotion_ids = ["fear", "anger", "grief", "confusion", "detachment"]
        expected_mood_counts = {
            "fear": 3,
            "anger": 3, 
            "grief": 3,
            "confusion": 3,
            "detachment": 3
        }
        
        try:
            for emotion_id in emotion_ids:
                response = self.session.get(f"{BACKEND_URL}/moods/{emotion_id}")
                
                if response.status_code != 200:
                    self.results["moods_api"]["errors"].append(f"Status code {response.status_code} for emotion {emotion_id}")
                    return
                
                moods = response.json()
                
                # Verify it's a list
                if not isinstance(moods, list):
                    self.results["moods_api"]["errors"].append(f"Response for {emotion_id} is not a list")
                    return
                
                # Verify expected number of moods
                expected_count = expected_mood_counts[emotion_id]
                if len(moods) != expected_count:
                    self.results["moods_api"]["errors"].append(f"Expected {expected_count} moods for {emotion_id}, got {len(moods)}")
                    return
                
                # Verify structure of each mood
                expected_fields = ["_id", "emotion_id", "name", "description"]
                
                for mood in moods:
                    # Check all required fields exist
                    for field in expected_fields:
                        if field not in mood:
                            self.results["moods_api"]["errors"].append(f"Missing field '{field}' in mood for {emotion_id}")
                            return
                    
                    # Verify emotion_id matches
                    if mood["emotion_id"] != emotion_id:
                        self.results["moods_api"]["errors"].append(f"Mood emotion_id mismatch: expected {emotion_id}, got {mood['emotion_id']}")
                        return
                    
                    # Verify data types
                    if not isinstance(mood["name"], str) or not mood["name"]:
                        self.results["moods_api"]["errors"].append(f"Invalid name for mood {mood['_id']}")
                        return
            
            self.results["moods_api"]["passed"] = True
            print("✅ Moods API test passed")
            
        except requests.exceptions.RequestException as e:
            self.results["moods_api"]["errors"].append(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            self.results["moods_api"]["errors"].append(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            self.results["moods_api"]["errors"].append(f"Unexpected error: {str(e)}")

    def test_guidance_api(self):
        """Test GET /api/guidance/{mood_id} endpoint"""
        print("🧪 Testing Guidance API...")
        
        # Test with known mood IDs from the sample data
        mood_ids = [
            "fear_future", "fear_death", "anger_injustice", 
            "grief_loss", "confusion_purpose", "detachment_loneliness"
        ]
        
        try:
            for mood_id in mood_ids:
                response = self.session.get(f"{BACKEND_URL}/guidance/{mood_id}")
                
                if response.status_code != 200:
                    self.results["guidance_api"]["errors"].append(f"Status code {response.status_code} for mood {mood_id}")
                    return
                
                guidance = response.json()
                
                # Verify it's an object (not a list)
                if not isinstance(guidance, dict):
                    self.results["guidance_api"]["errors"].append(f"Response for {mood_id} is not an object")
                    return
                
                # Verify structure
                expected_fields = ["_id", "mood_id", "title", "verse_reference", "sanskrit_verse", "english_translation", "guidance_text"]
                
                for field in expected_fields:
                    if field not in guidance:
                        self.results["guidance_api"]["errors"].append(f"Missing field '{field}' in guidance for {mood_id}")
                        return
                
                # Verify mood_id matches
                if guidance["mood_id"] != mood_id:
                    self.results["guidance_api"]["errors"].append(f"Guidance mood_id mismatch: expected {mood_id}, got {guidance['mood_id']}")
                    return
                
                # Verify content quality
                if not isinstance(guidance["sanskrit_verse"], str) or len(guidance["sanskrit_verse"]) < 10:
                    self.results["guidance_api"]["errors"].append(f"Invalid sanskrit_verse for mood {mood_id}")
                    return
                
                if not isinstance(guidance["english_translation"], str) or len(guidance["english_translation"]) < 10:
                    self.results["guidance_api"]["errors"].append(f"Invalid english_translation for mood {mood_id}")
                    return
                
                if not isinstance(guidance["guidance_text"], str) or len(guidance["guidance_text"]) < 20:
                    self.results["guidance_api"]["errors"].append(f"Invalid guidance_text for mood {mood_id}")
                    return
                
                # Verify verse reference format
                if "Bhagavad Gita" not in guidance["verse_reference"]:
                    self.results["guidance_api"]["errors"].append(f"Invalid verse_reference format for mood {mood_id}")
                    return
            
            self.results["guidance_api"]["passed"] = True
            print("✅ Guidance API test passed")
            
        except requests.exceptions.RequestException as e:
            self.results["guidance_api"]["errors"].append(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            self.results["guidance_api"]["errors"].append(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            self.results["guidance_api"]["errors"].append(f"Unexpected error: {str(e)}")

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("🧪 Testing Error Handling...")
        
        try:
            # Test invalid emotion_id
            response = self.session.get(f"{BACKEND_URL}/moods/invalid_emotion")
            if response.status_code != 404:
                self.results["error_handling"]["errors"].append(f"Expected 404 for invalid emotion, got {response.status_code}")
                return
            
            # Test invalid mood_id
            response = self.session.get(f"{BACKEND_URL}/guidance/invalid_mood")
            if response.status_code != 404:
                self.results["error_handling"]["errors"].append(f"Expected 404 for invalid mood, got {response.status_code}")
                return
            
            self.results["error_handling"]["passed"] = True
            print("✅ Error handling test passed")
            
        except requests.exceptions.RequestException as e:
            self.results["error_handling"]["errors"].append(f"Request failed: {str(e)}")
        except Exception as e:
            self.results["error_handling"]["errors"].append(f"Unexpected error: {str(e)}")

    def run_all_tests(self):
        """Run all tests and return results"""
        print(f"🚀 Starting SHLOKA Backend API Tests")
        print(f"📡 Testing against: {BACKEND_URL}")
        print("=" * 50)
        
        self.test_emotions_api()
        self.test_moods_api()
        self.test_guidance_api()
        self.test_error_handling()
        
        return self.results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result["passed"])
        
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            
            if not result["passed"] and result["errors"]:
                for error in result["errors"]:
                    print(f"  ❌ {error}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! SHLOKA backend is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
            return False

def main():
    tester = SHLOKAAPITester()
    results = tester.run_all_tests()
    success = tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()