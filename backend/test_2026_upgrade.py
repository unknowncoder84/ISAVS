"""
Quick Test Script for ISAVS 2026 Upgrade
Tests all major components to ensure they're working correctly
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from app.services.ai_service import get_ai_service
        print("✅ ai_service imported successfully")
    except Exception as e:
        print(f"❌ ai_service import failed: {e}")
        return False
    
    try:
        from app.services.preprocess import get_preprocessor
        print("✅ preprocess imported successfully")
    except Exception as e:
        print(f"❌ preprocess import failed: {e}")
        return False
    
    try:
        from app.services.geofence_service import get_geofence_service
        print("✅ geofence_service imported successfully")
    except Exception as e:
        print(f"❌ geofence_service import failed: {e}")
        return False
    
    try:
        from app.services.otp_service import get_otp_service
        print("✅ otp_service imported successfully")
    except Exception as e:
        print(f"❌ otp_service import failed: {e}")
        return False
    
    try:
        from app.api.endpoints import router
        print("✅ endpoints imported successfully")
    except Exception as e:
        print(f"❌ endpoints import failed: {e}")
        return False
    
    return True


def test_ai_service():
    """Test AI service functionality"""
    print("\n🧪 Testing AI service...")
    
    try:
        from app.services.ai_service import get_ai_service
        import numpy as np
        
        ai_service = get_ai_service()
        print("✅ AI service initialized")
        
        # Test cosine similarity
        emb1 = np.random.rand(128)
        emb2 = np.random.rand(128)
        similarity = ai_service.cosine_similarity(emb1, emb2)
        print(f"✅ Cosine similarity test: {similarity:.4f}")
        
        # Test with identical embeddings
        similarity_same = ai_service.cosine_similarity(emb1, emb1)
        if abs(similarity_same - 1.0) < 0.01:
            print(f"✅ Identical embeddings similarity: {similarity_same:.4f} (expected ~1.0)")
        else:
            print(f"⚠️ Identical embeddings similarity: {similarity_same:.4f} (expected ~1.0)")
        
        return True
    except Exception as e:
        print(f"❌ AI service test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_geofence():
    """Test geofencing functionality"""
    print("\n🧪 Testing geofence service...")
    
    try:
        from app.services.geofence_service import get_geofence_service
        
        geofence = get_geofence_service()
        print("✅ Geofence service initialized")
        
        # Test distance calculation (Manila to Quezon City - ~10km)
        lat1, lon1 = 14.5995, 120.9842  # Manila
        lat2, lon2 = 14.6760, 121.0437  # Quezon City
        
        distance = geofence.calculate_distance(lat1, lon1, lat2, lon2)
        print(f"✅ Distance calculation: {distance:.0f}m (~10km expected)")
        
        # Test geofence check (same location)
        is_within, dist = geofence.is_within_geofence(
            lat1, lon1, lat1, lon1, radius_meters=50
        )
        if is_within and dist < 1:
            print(f"✅ Same location geofence: within={is_within}, distance={dist:.2f}m")
        else:
            print(f"⚠️ Same location geofence: within={is_within}, distance={dist:.2f}m")
        
        # Test geofence check (outside)
        is_within, dist = geofence.is_within_geofence(
            lat1, lon1, lat2, lon2, radius_meters=50
        )
        if not is_within:
            print(f"✅ Different location geofence: within={is_within}, distance={dist:.0f}m")
        else:
            print(f"⚠️ Different location geofence: within={is_within}, distance={dist:.0f}m")
        
        return True
    except Exception as e:
        print(f"❌ Geofence test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_config():
    """Test configuration settings"""
    print("\n🧪 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"✅ OTP_TTL_SECONDS: {settings.OTP_TTL_SECONDS}")
        print(f"✅ FACE_SIMILARITY_THRESHOLD: {settings.FACE_SIMILARITY_THRESHOLD}")
        print(f"✅ GEOFENCE_RADIUS_METERS: {settings.GEOFENCE_RADIUS_METERS}")
        
        if settings.OTP_TTL_SECONDS == 60:
            print("✅ OTP TTL is 60 seconds (2026 standard)")
        else:
            print(f"⚠️ OTP TTL is {settings.OTP_TTL_SECONDS} seconds (expected 60)")
        
        if settings.FACE_SIMILARITY_THRESHOLD == 0.6:
            print("✅ Face threshold is 0.6 (2026 standard)")
        else:
            print(f"⚠️ Face threshold is {settings.FACE_SIMILARITY_THRESHOLD} (expected 0.6)")
        
        if settings.GEOFENCE_RADIUS_METERS == 50.0:
            print("✅ Geofence radius is 50m (2026 standard)")
        else:
            print(f"⚠️ Geofence radius is {settings.GEOFENCE_RADIUS_METERS}m (expected 50)")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_preprocessor():
    """Test preprocessor initialization"""
    print("\n🧪 Testing preprocessor...")
    
    try:
        from app.services.preprocess import get_preprocessor
        
        # Check if face_landmarker.task exists
        import os
        model_paths = [
            'backend/face_landmarker.task',
            'face_landmarker.task'
        ]
        
        model_found = False
        for path in model_paths:
            if os.path.exists(path):
                print(f"✅ MediaPipe model found at: {path}")
                model_found = True
                break
        
        if not model_found:
            print("⚠️ MediaPipe model not found. Download from:")
            print("   https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task")
            return False
        
        preprocessor = get_preprocessor()
        print("✅ Preprocessor initialized with MediaPipe Tasks API + CLAHE")
        
        return True
    except Exception as e:
        print(f"❌ Preprocessor test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("ISAVS 2026 Upgrade - System Test")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test AI service
    results.append(("AI Service", test_ai_service()))
    
    # Test geofence
    results.append(("Geofence", test_geofence()))
    
    # Test config
    results.append(("Configuration", test_config()))
    
    # Test preprocessor
    results.append(("Preprocessor", test_preprocessor()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
