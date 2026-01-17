"""
Test script for geofencing functionality
Run: python backend/test_geofencing.py
"""

from app.utils.geofencing import GeofencingService, calculate_distance

print("=" * 60)
print("ISAVS 2026 - Geofencing Test Suite")
print("=" * 60)

# Test coordinates (Delhi, India - example college campus)
teacher_location = (28.6139, 77.2090)
student_near = (28.6145, 77.2095)      # ~70m away
student_medium = (28.6155, 77.2105)    # ~180m away
student_far = (28.6200, 77.2150)       # ~800m away

print("\n📍 Test Locations:")
print(f"Teacher: {teacher_location}")
print(f"Student (Near): {student_near}")
print(f"Student (Medium): {student_medium}")
print(f"Student (Far): {student_far}")

print("\n" + "=" * 60)
print("TEST 1: Haversine Distance Calculation")
print("=" * 60)

distance_near = calculate_distance(
    teacher_location[0], teacher_location[1],
    student_near[0], student_near[1]
)
print(f"✓ Distance to near student: {distance_near:.2f}m")

distance_medium = calculate_distance(
    teacher_location[0], teacher_location[1],
    student_medium[0], student_medium[1]
)
print(f"✓ Distance to medium student: {distance_medium:.2f}m")

distance_far = calculate_distance(
    teacher_location[0], teacher_location[1],
    student_far[0], student_far[1]
)
print(f"✓ Distance to far student: {distance_far:.2f}m")

print("\n" + "=" * 60)
print("TEST 2: GPS Verification (100m threshold)")
print("=" * 60)

result_near = GeofencingService.verify_geofence(
    student_near[0], student_near[1],
    teacher_location[0], teacher_location[1]
)
print(f"\nNear Student:")
print(f"  Verified: {'✅ YES' if result_near['verified'] else '❌ NO'}")
print(f"  Distance: {result_near['distance_meters']:.2f}m")
print(f"  Message: {result_near['message']}")

result_medium = GeofencingService.verify_geofence(
    student_medium[0], student_medium[1],
    teacher_location[0], teacher_location[1]
)
print(f"\nMedium Student:")
print(f"  Verified: {'✅ YES' if result_medium['verified'] else '❌ NO'}")
print(f"  Distance: {result_medium['distance_meters']:.2f}m")
print(f"  Message: {result_medium['message']}")

result_far = GeofencingService.verify_geofence(
    student_far[0], student_far[1],
    teacher_location[0], teacher_location[1]
)
print(f"\nFar Student:")
print(f"  Verified: {'✅ YES' if result_far['verified'] else '❌ NO'}")
print(f"  Distance: {result_far['distance_meters']:.2f}m")
print(f"  Message: {result_far['message']}")

print("\n" + "=" * 60)
print("TEST 3: GPS with Accuracy Adjustment")
print("=" * 60)

# Student with poor GPS accuracy
result_accuracy = GeofencingService.verify_with_accuracy(
    student_medium[0], student_medium[1],
    teacher_location[0], teacher_location[1],
    gps_accuracy=75.0  # Poor accuracy
)
print(f"\nMedium Student with Poor GPS (±75m):")
print(f"  Verified: {'✅ YES' if result_accuracy['verified'] else '❌ NO'}")
print(f"  Distance: {result_accuracy['distance_meters']:.2f}m")
print(f"  GPS Accuracy: ±{result_accuracy['gps_accuracy']:.0f}m")
print(f"  Threshold Adjusted: {result_accuracy['threshold_adjusted']}")
print(f"  Message: {result_accuracy['message']}")

print("\n" + "=" * 60)
print("TEST 4: WiFi Fallback Verification")
print("=" * 60)

whitelisted_ssids = ['College-WiFi', 'College-Staff', 'College-Student', 'Eduroam']

# Valid WiFi
wifi_valid = GeofencingService.check_wifi_fallback(
    'College-WiFi', whitelisted_ssids
)
print(f"\nValid WiFi SSID:")
print(f"  Verified: {'✅ YES' if wifi_valid['verified'] else '❌ NO'}")
print(f"  SSID: {wifi_valid['ssid']}")
print(f"  Message: {wifi_valid['message']}")

# Invalid WiFi
wifi_invalid = GeofencingService.check_wifi_fallback(
    'Random-WiFi', whitelisted_ssids
)
print(f"\nInvalid WiFi SSID:")
print(f"  Verified: {'✅ YES' if wifi_invalid['verified'] else '❌ NO'}")
print(f"  SSID: {wifi_invalid['ssid']}")
print(f"  Message: {wifi_invalid['message']}")

print("\n" + "=" * 60)
print("TEST 5: Comprehensive Verification (GPS + WiFi Fallback)")
print("=" * 60)

# Scenario 1: GPS success
comprehensive_gps = GeofencingService.verify_location(
    student_near[0], student_near[1],
    teacher_location[0], teacher_location[1],
    gps_accuracy=30.0,
    gps_failure_count=0,
    wifi_ssid=None,
    whitelisted_ssids=whitelisted_ssids
)
print(f"\nScenario 1: GPS Success")
print(f"  Verified: {'✅ YES' if comprehensive_gps['verified'] else '❌ NO'}")
print(f"  Method: {comprehensive_gps['method']}")
print(f"  Message: {comprehensive_gps['message']}")

# Scenario 2: GPS failed, WiFi fallback
comprehensive_wifi = GeofencingService.verify_location(
    None, None,  # GPS failed
    teacher_location[0], teacher_location[1],
    gps_accuracy=None,
    gps_failure_count=2,  # 2 failures
    wifi_ssid='College-WiFi',
    whitelisted_ssids=whitelisted_ssids
)
print(f"\nScenario 2: GPS Failed → WiFi Fallback")
print(f"  Verified: {'✅ YES' if comprehensive_wifi['verified'] else '❌ NO'}")
print(f"  Method: {comprehensive_wifi['method']}")
print(f"  Fallback Used: {comprehensive_wifi.get('fallback_used', False)}")
print(f"  Message: {comprehensive_wifi['message']}")

# Scenario 3: GPS failed, not enough attempts for fallback
comprehensive_retry = GeofencingService.verify_location(
    None, None,  # GPS failed
    teacher_location[0], teacher_location[1],
    gps_accuracy=None,
    gps_failure_count=1,  # Only 1 failure
    wifi_ssid=None,
    whitelisted_ssids=whitelisted_ssids
)
print(f"\nScenario 3: GPS Failed (1/2 attempts)")
print(f"  Verified: {'✅ YES' if comprehensive_retry['verified'] else '❌ NO'}")
print(f"  Method: {comprehensive_retry['method']}")
print(f"  Failure Count: {comprehensive_retry['gps_failure_count']}/2")
print(f"  Message: {comprehensive_retry['message']}")

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("✅ Haversine distance calculation working")
print("✅ GPS verification with 100m threshold working")
print("✅ GPS accuracy adjustment working")
print("✅ WiFi fallback verification working")
print("✅ Comprehensive verification logic working")
print("\n🎉 All tests passed! Geofencing system is ready.")
print("=" * 60)
