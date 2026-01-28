#!/usr/bin/env python3
"""
SHLOKA Backend API Testing - Enhanced Emotions Feature
Tests the enhanced emotions feature with 11 emotions (5 original + 6 new)
"""

import requests
import json
import sys
from typing import List, Dict, Any

# Backend URL from frontend/.env
BACKEND_URL = "https://error-resolve-14.preview.emergentagent.com/api"

class SHLOKAAPITester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.failed_tests = []
        
    def log_result(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        }
        self.test_results.append(result)
        if not success:
            self.failed_tests.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_emotions_api(self):
        """Test GET /api/emotions - Should return 11 emotions"""
        print("\n=== Testing Emotions API ===")
        
        try:
            response = requests.get(f"{self.backend_url}/emotions", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Emotions API Status", False, f"Expected 200, got {response.status_code}", response.text)
                return False
                
            emotions = response.json()
            
            # Check total count
            if len(emotions) != 11:
                self.log_result("Emotions Count", False, f"Expected 11 emotions, got {len(emotions)}")
                return False
            
            self.log_result("Emotions Count", True, f"Correctly returns 11 emotions")
            
            # Expected emotions (5 original + 6 new)
            expected_emotions = {
                "fear": "Fear", "anger": "Anger", "grief": "Grief", 
                "confusion": "Confusion", "detachment": "Detachment",
                "joy": "Joy", "doubt": "Doubt", "pride": "Pride",
                "desire": "Desire", "envy": "Envy", "despair": "Despair"
            }
            
            # Check each emotion has required fields
            found_emotions = {}
            for emotion in emotions:
                required_fields = ["_id", "name_english", "name_sanskrit", "description", "icon"]
                missing_fields = [field for field in required_fields if field not in emotion]
                
                if missing_fields:
                    self.log_result(f"Emotion {emotion.get('_id', 'unknown')} Fields", False, 
                                  f"Missing fields: {missing_fields}")
                    continue
                
                found_emotions[emotion["_id"]] = emotion["name_english"]
                self.log_result(f"Emotion {emotion['_id']} Structure", True, 
                              f"All required fields present")
            
            # Check if all expected emotions are present
            missing_emotions = set(expected_emotions.keys()) - set(found_emotions.keys())
            if missing_emotions:
                self.log_result("Expected Emotions", False, f"Missing emotions: {missing_emotions}")
                return False
            
            # Check new emotions specifically
            new_emotions = ["joy", "doubt", "pride", "desire", "envy", "despair"]
            for emotion_id in new_emotions:
                if emotion_id in found_emotions:
                    self.log_result(f"New Emotion {emotion_id}", True, 
                                  f"Found: {found_emotions[emotion_id]}")
                else:
                    self.log_result(f"New Emotion {emotion_id}", False, "Not found")
            
            self.log_result("Emotions API", True, "All emotions correctly returned with proper structure")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result("Emotions API Connection", False, f"Connection error: {str(e)}")
            return False
        except Exception as e:
            self.log_result("Emotions API", False, f"Unexpected error: {str(e)}")
            return False
    
    def test_moods_api_for_new_emotions(self):
        """Test GET /api/moods/{emotion_id} for new emotions"""
        print("\n=== Testing Moods API for New Emotions ===")
        
        new_emotions = ["joy", "doubt", "pride", "desire", "envy", "despair"]
        all_passed = True
        
        for emotion_id in new_emotions:
            try:
                response = requests.get(f"{self.backend_url}/moods/{emotion_id}", timeout=10)
                
                if response.status_code != 200:
                    self.log_result(f"Moods API - {emotion_id}", False, 
                                  f"Expected 200, got {response.status_code}")
                    all_passed = False
                    continue
                
                moods = response.json()
                
                # Each emotion should have exactly 3 moods
                if len(moods) != 3:
                    self.log_result(f"Moods Count - {emotion_id}", False, 
                                  f"Expected 3 moods, got {len(moods)}")
                    all_passed = False
                    continue
                
                self.log_result(f"Moods Count - {emotion_id}", True, f"Correctly returns 3 moods")
                
                # Check mood structure
                for mood in moods:
                    required_fields = ["_id", "emotion_id", "name", "description"]
                    missing_fields = [field for field in required_fields if field not in mood]
                    
                    if missing_fields:
                        self.log_result(f"Mood Structure - {mood.get('_id', 'unknown')}", False,
                                      f"Missing fields: {missing_fields}")
                        all_passed = False
                        continue
                    
                    if mood["emotion_id"] != emotion_id:
                        self.log_result(f"Mood Emotion ID - {mood['_id']}", False,
                                      f"Expected emotion_id {emotion_id}, got {mood['emotion_id']}")
                        all_passed = False
                        continue
                
                self.log_result(f"Moods API - {emotion_id}", True, 
                              f"All 3 moods have correct structure and emotion_id")
                
            except requests.exceptions.RequestException as e:
                self.log_result(f"Moods API Connection - {emotion_id}", False, f"Connection error: {str(e)}")
                all_passed = False
            except Exception as e:
                self.log_result(f"Moods API - {emotion_id}", False, f"Unexpected error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_guidance_api_for_new_emotions(self):
        """Test GET /api/guidance/{mood_id} for new emotions guidance"""
        print("\n=== Testing Guidance API for New Emotions ===")
        
        # Test mood IDs for new emotions (as specified in the review request)
        test_mood_ids = [
            "joy_gratitude", "joy_peace", 
            "doubt_faith", "doubt_teachings",
            "pride_achievement", "pride_knowledge",
            "desire_wealth", "desire_pleasure",
            "envy_success", "envy_happiness",
            "despair_effort", "despair_future"
        ]
        
        all_passed = True
        
        for mood_id in test_mood_ids:
            try:
                response = requests.get(f"{self.backend_url}/guidance/{mood_id}", timeout=10)
                
                if response.status_code != 200:
                    self.log_result(f"Guidance API - {mood_id}", False,
                                  f"Expected 200, got {response.status_code}")
                    all_passed = False
                    continue
                
                guidance = response.json()
                
                # Check required fields
                required_fields = ["_id", "mood_id", "title", "verse_reference", 
                                 "sanskrit_verse", "english_translation", "guidance_text"]
                missing_fields = [field for field in required_fields if field not in guidance]
                
                if missing_fields:
                    self.log_result(f"Guidance Structure - {mood_id}", False,
                                  f"Missing fields: {missing_fields}")
                    all_passed = False
                    continue
                
                # Check verse reference format
                verse_ref = guidance.get("verse_reference", "")
                if not verse_ref.startswith("Bhagavad Gita"):
                    self.log_result(f"Verse Reference Format - {mood_id}", False,
                                  f"Expected 'Bhagavad Gita X.Y' format, got: {verse_ref}")
                    all_passed = False
                    continue
                
                # Check Sanskrit verse is not empty and contains Sanskrit characters
                sanskrit_verse = guidance.get("sanskrit_verse", "")
                if not sanskrit_verse or len(sanskrit_verse.strip()) < 10:
                    self.log_result(f"Sanskrit Verse Content - {mood_id}", False,
                                  "Sanskrit verse is empty or too short")
                    all_passed = False
                    continue
                
                # Check if Sanskrit verse contains Devanagari characters (basic check)
                has_sanskrit = any('\u0900' <= char <= '\u097F' for char in sanskrit_verse)
                if not has_sanskrit:
                    self.log_result(f"Sanskrit Verse Script - {mood_id}", False,
                                  "Sanskrit verse doesn't contain Devanagari characters")
                    all_passed = False
                    continue
                
                # Check English translation is meaningful
                english_translation = guidance.get("english_translation", "")
                if not english_translation or len(english_translation.strip()) < 20:
                    self.log_result(f"English Translation - {mood_id}", False,
                                  "English translation is empty or too short")
                    all_passed = False
                    continue
                
                # Check guidance text is meaningful
                guidance_text = guidance.get("guidance_text", "")
                if not guidance_text or len(guidance_text.strip()) < 50:
                    self.log_result(f"Guidance Text - {mood_id}", False,
                                  "Guidance text is empty or too short")
                    all_passed = False
                    continue
                
                self.log_result(f"Guidance API - {mood_id}", True,
                              f"Complete guidance with authentic Bhagavad Gita verse")
                
            except requests.exceptions.RequestException as e:
                self.log_result(f"Guidance API Connection - {mood_id}", False, f"Connection error: {str(e)}")
                all_passed = False
            except Exception as e:
                self.log_result(f"Guidance API - {mood_id}", False, f"Unexpected error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_response_times(self):
        """Test API response times"""
        print("\n=== Testing Response Times ===")
        
        import time
        
        # Test emotions API response time
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/emotions", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            if response_time > 5.0:  # 5 seconds threshold
                self.log_result("Emotions API Response Time", False,
                              f"Response time {response_time:.2f}s exceeds 5s threshold")
            else:
                self.log_result("Emotions API Response Time", True,
                              f"Response time {response_time:.2f}s is acceptable")
                
        except Exception as e:
            self.log_result("Response Time Test", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting SHLOKA Backend API Tests - Enhanced Emotions Feature")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 70)
        
        # Run tests
        emotions_passed = self.test_emotions_api()
        moods_passed = self.test_moods_api_for_new_emotions()
        guidance_passed = self.test_guidance_api_for_new_emotions()
        self.test_response_times()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        # Overall result
        critical_apis_passed = emotions_passed and moods_passed and guidance_passed
        
        if critical_apis_passed:
            print("\n🎉 SUCCESS: All critical APIs are working correctly!")
            print("✅ Enhanced emotions feature is fully functional")
            return True
        else:
            print("\n⚠️  ISSUES FOUND: Some critical APIs have problems")
            return False

if __name__ == "__main__":
    tester = SHLOKAAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)