#!/usr/bin/env python3
"""
SHLOKA Backend API Testing Suite
Comprehensive testing for the "guidance not found" error fix

This test suite validates:
1. All 11 emotions API
2. All 33 moods APIs (3 per emotion)
3. All 33 guidance APIs (1 per mood)
4. Complete user journey testing
5. Error handling validation
6. Focus on the 6 newly fixed moods
"""

import requests
import json
import time
from typing import Dict, List, Any

# Backend URL from frontend .env
BACKEND_URL = "https://emotion-guide-fix.preview.emergentagent.com/api"

# Expected emotion IDs
EXPECTED_EMOTIONS = [
    "fear", "anger", "grief", "confusion", "detachment", 
    "joy", "doubt", "pride", "desire", "envy", "despair"
]

# The 6 newly fixed moods that were causing "guidance not found" errors
NEWLY_FIXED_MOODS = [
    "anger_world",
    "confusion_choice", 
    "confusion_meaning",
    "detachment_emptiness",
    "grief_change",
    "grief_health"
]

class SHLOKATestSuite:
    def __init__(self):
        self.test_results = {
            "emotions": {"passed": 0, "failed": 0, "details": []},
            "moods": {"passed": 0, "failed": 0, "details": []},
            "guidance": {"passed": 0, "failed": 0, "details": []},
            "user_journey": {"passed": 0, "failed": 0, "details": []},
            "error_handling": {"passed": 0, "failed": 0, "details": []},
            "newly_fixed": {"passed": 0, "failed": 0, "details": []}
        }
        self.all_emotions = []
        self.all_moods = {}
        self.all_guidance = {}
        
    def log_result(self, category: str, test_name: str, passed: bool, details: str):
        """Log test result"""
        if passed:
            self.test_results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results[category]["failed"] += 1
            status = "❌ FAIL"
            
        self.test_results[category]["details"].append(f"{status}: {test_name} - {details}")
        print(f"{status}: {test_name} - {details}")
        
    def test_emotions_api(self):
        """Test GET /api/emotions - Should return 11 emotions"""
        print("\n🧪 TESTING EMOTIONS API")
        print("=" * 50)
        
        try:
            response = requests.get(f"{BACKEND_URL}/emotions", timeout=10)
            
            if response.status_code != 200:
                self.log_result("emotions", "Emotions API Status", False, 
                              f"Expected 200, got {response.status_code}")
                return
                
            emotions = response.json()
            self.all_emotions = emotions
            
            # Test count
            if len(emotions) == 11:
                self.log_result("emotions", "Emotion Count", True, 
                              f"Correct count: {len(emotions)} emotions")
            else:
                self.log_result("emotions", "Emotion Count", False, 
                              f"Expected 11, got {len(emotions)}")
                
            # Test structure and IDs
            found_ids = []
            for emotion in emotions:
                emotion_id = emotion.get("_id")
                found_ids.append(emotion_id)
                
                # Check required fields
                required_fields = ["_id", "name_english", "name_sanskrit", "description", "icon"]
                missing_fields = [field for field in required_fields if field not in emotion]
                
                if not missing_fields:
                    self.log_result("emotions", f"Emotion {emotion_id} Structure", True, 
                                  "All required fields present")
                else:
                    self.log_result("emotions", f"Emotion {emotion_id} Structure", False, 
                                  f"Missing fields: {missing_fields}")
                    
            # Check all expected emotion IDs are present
            missing_emotions = set(EXPECTED_EMOTIONS) - set(found_ids)
            extra_emotions = set(found_ids) - set(EXPECTED_EMOTIONS)
            
            if not missing_emotions and not extra_emotions:
                self.log_result("emotions", "Emotion IDs Match", True, 
                              "All expected emotion IDs present")
            else:
                details = []
                if missing_emotions:
                    details.append(f"Missing: {missing_emotions}")
                if extra_emotions:
                    details.append(f"Extra: {extra_emotions}")
                self.log_result("emotions", "Emotion IDs Match", False, "; ".join(details))
                
        except Exception as e:
            self.log_result("emotions", "Emotions API Request", False, f"Exception: {str(e)}")
            
    def test_moods_apis(self):
        """Test GET /api/moods/{emotion_id} for all 11 emotions"""
        print("\n🧪 TESTING MOODS APIs")
        print("=" * 50)
        
        if not self.all_emotions:
            self.log_result("moods", "Moods Test Setup", False, "No emotions data available")
            return
            
        total_moods = 0
        
        for emotion in self.all_emotions:
            emotion_id = emotion.get("_id")
            
            try:
                response = requests.get(f"{BACKEND_URL}/moods/{emotion_id}", timeout=10)
                
                if response.status_code != 200:
                    self.log_result("moods", f"Moods API {emotion_id}", False, 
                                  f"Expected 200, got {response.status_code}")
                    continue
                    
                moods = response.json()
                self.all_moods[emotion_id] = moods
                total_moods += len(moods)
                
                # Each emotion should have exactly 3 moods
                if len(moods) == 3:
                    self.log_result("moods", f"Moods Count {emotion_id}", True, 
                                  f"Correct count: 3 moods")
                else:
                    self.log_result("moods", f"Moods Count {emotion_id}", False, 
                                  f"Expected 3, got {len(moods)}")
                    
                # Test mood structure and emotion_id linkage
                for mood in moods:
                    mood_id = mood.get("_id")
                    
                    # Check required fields
                    required_fields = ["_id", "emotion_id", "name", "description"]
                    missing_fields = [field for field in required_fields if field not in mood]
                    
                    if not missing_fields:
                        self.log_result("moods", f"Mood {mood_id} Structure", True, 
                                      "All required fields present")
                    else:
                        self.log_result("moods", f"Mood {mood_id} Structure", False, 
                                      f"Missing fields: {missing_fields}")
                        
                    # Check emotion_id linkage
                    if mood.get("emotion_id") == emotion_id:
                        self.log_result("moods", f"Mood {mood_id} Linkage", True, 
                                      f"Correctly linked to {emotion_id}")
                    else:
                        self.log_result("moods", f"Mood {mood_id} Linkage", False, 
                                      f"Expected {emotion_id}, got {mood.get('emotion_id')}")
                        
            except Exception as e:
                self.log_result("moods", f"Moods API {emotion_id}", False, f"Exception: {str(e)}")
                
        # Test total mood count (should be 33)
        if total_moods == 33:
            self.log_result("moods", "Total Moods Count", True, f"Correct total: {total_moods} moods")
        else:
            self.log_result("moods", "Total Moods Count", False, f"Expected 33, got {total_moods}")
            
    def test_guidance_apis(self):
        """Test GET /api/guidance/{mood_id} for all 33 moods"""
        print("\n🧪 TESTING GUIDANCE APIs")
        print("=" * 50)
        
        if not self.all_moods:
            self.log_result("guidance", "Guidance Test Setup", False, "No moods data available")
            return
            
        total_guidance = 0
        
        for emotion_id, moods in self.all_moods.items():
            for mood in moods:
                mood_id = mood.get("_id")
                
                try:
                    response = requests.get(f"{BACKEND_URL}/guidance/{mood_id}", timeout=10)
                    
                    if response.status_code != 200:
                        self.log_result("guidance", f"Guidance API {mood_id}", False, 
                                      f"Expected 200, got {response.status_code}")
                        continue
                        
                    guidance = response.json()
                    self.all_guidance[mood_id] = guidance
                    total_guidance += 1
                    
                    # Check required fields
                    required_fields = ["_id", "mood_id", "title", "verse_reference", 
                                     "sanskrit_verse", "english_translation", "guidance_text"]
                    missing_fields = [field for field in required_fields if field not in guidance]
                    
                    if not missing_fields:
                        self.log_result("guidance", f"Guidance {mood_id} Structure", True, 
                                      "All required fields present")
                    else:
                        self.log_result("guidance", f"Guidance {mood_id} Structure", False, 
                                      f"Missing fields: {missing_fields}")
                        
                    # Check mood_id linkage
                    if guidance.get("mood_id") == mood_id:
                        self.log_result("guidance", f"Guidance {mood_id} Linkage", True, 
                                      f"Correctly linked to {mood_id}")
                    else:
                        self.log_result("guidance", f"Guidance {mood_id} Linkage", False, 
                                      f"Expected {mood_id}, got {guidance.get('mood_id')}")
                        
                    # Verify authentic Bhagavad Gita verse reference
                    verse_ref = guidance.get("verse_reference", "")
                    if "Bhagavad Gita" in verse_ref and any(char.isdigit() for char in verse_ref):
                        self.log_result("guidance", f"Guidance {mood_id} Verse Reference", True, 
                                      f"Valid reference: {verse_ref}")
                    else:
                        self.log_result("guidance", f"Guidance {mood_id} Verse Reference", False, 
                                      f"Invalid reference: {verse_ref}")
                        
                except Exception as e:
                    self.log_result("guidance", f"Guidance API {mood_id}", False, f"Exception: {str(e)}")
                    
        # Test total guidance count (should be 33)
        if total_guidance == 33:
            self.log_result("guidance", "Total Guidance Count", True, f"Correct total: {total_guidance} guidance entries")
        else:
            self.log_result("guidance", "Total Guidance Count", False, f"Expected 33, got {total_guidance}")
            
    def test_newly_fixed_moods(self):
        """Test the 6 newly fixed moods that were causing 'guidance not found' errors"""
        print("\n🧪 TESTING NEWLY FIXED MOODS")
        print("=" * 50)
        
        for mood_id in NEWLY_FIXED_MOODS:
            try:
                response = requests.get(f"{BACKEND_URL}/guidance/{mood_id}", timeout=10)
                
                if response.status_code == 200:
                    guidance = response.json()
                    self.log_result("newly_fixed", f"Fixed Mood {mood_id}", True, 
                                  f"Guidance found: {guidance.get('title', 'No title')}")
                else:
                    self.log_result("newly_fixed", f"Fixed Mood {mood_id}", False, 
                                  f"Still getting {response.status_code} error")
                    
            except Exception as e:
                self.log_result("newly_fixed", f"Fixed Mood {mood_id}", False, f"Exception: {str(e)}")
                
    def test_user_journey(self):
        """Test complete user journey: emotion → moods → guidance"""
        print("\n🧪 TESTING USER JOURNEY")
        print("=" * 50)
        
        # Test 3 random emotions for complete journey
        test_emotions = ["fear", "joy", "anger"]
        
        for emotion_id in test_emotions:
            try:
                # Step 1: Get emotion (already tested, but verify it exists)
                emotion_found = any(e.get("_id") == emotion_id for e in self.all_emotions)
                if not emotion_found:
                    self.log_result("user_journey", f"Journey {emotion_id} - Emotion", False, 
                                  "Emotion not found")
                    continue
                    
                # Step 2: Get moods for emotion
                moods_response = requests.get(f"{BACKEND_URL}/moods/{emotion_id}", timeout=10)
                if moods_response.status_code != 200:
                    self.log_result("user_journey", f"Journey {emotion_id} - Moods", False, 
                                  f"Moods API failed: {moods_response.status_code}")
                    continue
                    
                moods = moods_response.json()
                
                # Step 3: Get guidance for each mood
                journey_success = True
                for mood in moods:
                    mood_id = mood.get("_id")
                    guidance_response = requests.get(f"{BACKEND_URL}/guidance/{mood_id}", timeout=10)
                    
                    if guidance_response.status_code != 200:
                        self.log_result("user_journey", f"Journey {emotion_id} - Guidance {mood_id}", False, 
                                      f"Guidance API failed: {guidance_response.status_code}")
                        journey_success = False
                        
                if journey_success:
                    self.log_result("user_journey", f"Complete Journey {emotion_id}", True, 
                                  f"Full journey successful: {len(moods)} moods → guidance")
                    
            except Exception as e:
                self.log_result("user_journey", f"Journey {emotion_id}", False, f"Exception: {str(e)}")
                
    def test_error_handling(self):
        """Test error handling for invalid IDs"""
        print("\n🧪 TESTING ERROR HANDLING")
        print("=" * 50)
        
        # Test invalid emotion_id
        try:
            response = requests.get(f"{BACKEND_URL}/moods/invalid_emotion", timeout=10)
            if response.status_code == 404:
                self.log_result("error_handling", "Invalid Emotion ID", True, 
                              "Correctly returns 404 for invalid emotion")
            else:
                self.log_result("error_handling", "Invalid Emotion ID", False, 
                              f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("error_handling", "Invalid Emotion ID", False, f"Exception: {str(e)}")
            
        # Test invalid mood_id
        try:
            response = requests.get(f"{BACKEND_URL}/guidance/invalid_mood", timeout=10)
            if response.status_code == 404:
                self.log_result("error_handling", "Invalid Mood ID", True, 
                              "Correctly returns 404 for invalid mood")
            else:
                self.log_result("error_handling", "Invalid Mood ID", False, 
                              f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("error_handling", "Invalid Mood ID", False, f"Exception: {str(e)}")
            
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 STARTING SHLOKA BACKEND API TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        self.test_emotions_api()
        self.test_moods_apis()
        self.test_guidance_apis()
        self.test_newly_fixed_moods()
        self.test_user_journey()
        self.test_error_handling()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🏁 SHLOKA BACKEND TESTING SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅" if failed == 0 else "❌"
            print(f"{status} {category.upper()}: {passed} passed, {failed} failed")
            
        print(f"\n🎯 OVERALL RESULT: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 ALL TESTS PASSED! The 'guidance not found' error has been successfully fixed!")
            print("✅ All 11 emotions working")
            print("✅ All 33 moods working") 
            print("✅ All 33 guidance entries working")
            print("✅ All 6 newly fixed moods working")
            print("✅ Complete user journey working")
        else:
            print("⚠️  SOME TESTS FAILED - Issues need attention:")
            for category, results in self.test_results.items():
                if results["failed"] > 0:
                    print(f"\n❌ {category.upper()} FAILURES:")
                    for detail in results["details"]:
                        if "❌ FAIL" in detail:
                            print(f"   {detail}")

if __name__ == "__main__":
    # Run the comprehensive test suite
    test_suite = SHLOKATestSuite()
    test_suite.run_all_tests()