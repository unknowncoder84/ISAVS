# 🚀 Geofencing Quick Start - ISAVS 2026

## ⚡ 3-Step Setup

### Step 1: Run SQL Migration (2 minutes)
```bash
psql -U your_username -d your_database -f backend/migration_geofencing_fix.sql
```

### Step 2: Test Geofencing (30 seconds)
```bash
cd backend
python test_geofencing.py
```

Expected: All tests pass ✅

### Step 3: Start System
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --port 6000

# Terminal 2: Student Portal
cd frontend
npm run dev:student
```

---

## 🎯 What Changed

### Before (Problems)
- ❌ SQL error: `created_at` column missing
- ❌ GPS false positives: 50m too strict for indoor
- ❌ No fallback: Students stuck when GPS fails

### After (Solutions)
- ✅ SQL fixed: All columns exist with proper checks
- ✅ 100m threshold: Accounts for indoor GPS drift
- ✅ WiFi fallback: After 2 GPS failures, use college WiFi
- ✅ High accuracy: `enableHighAccuracy: true` in frontend
- ✅ Haversine formula: Accurate distance calculation (±1m)

---

## 📱 Student Experience

### Normal Flow (GPS Works)
1. Enter Session ID + Student ID
2. Allow location access
3. GPS check: "✓ Within Range (82m)"
4. Continue to OTP entry
5. Complete face scan

### Fallback Flow (GPS Fails)
1. Enter Session ID + Student ID
2. GPS fails: "Location access denied (1/2)"
3. Click "🔄 Retry GPS Check"
4. GPS fails again: "GPS failed 2 times. Try WiFi"
5. Click "📶 Verify Using WiFi Instead"
6. Enter WiFi SSID: "College-WiFi"
7. WiFi verified: Continue to OTP entry
8. Complete face scan

---

## 🔧 Configuration

### Change Distance Threshold
```sql
UPDATE geofence_config 
SET config_value = '150' 
WHERE config_key = 'max_distance_meters';
```

### Add WiFi Network
```sql
INSERT INTO wifi_whitelist (ssid, location_name) 
VALUES ('New-Building-WiFi', 'Engineering Block');
```

### Disable WiFi Fallback
```sql
UPDATE geofence_config 
SET config_value = 'false' 
WHERE config_key = 'wifi_fallback_enabled';
```

---

## 🧪 Test Commands

### Test Haversine Distance
```python
from backend.app.utils.geofencing import calculate_distance

# Delhi coordinates (example)
teacher = (28.6139, 77.2090)
student = (28.6145, 77.2095)

distance = calculate_distance(
    teacher[0], teacher[1],
    student[0], student[1]
)
print(f"Distance: {distance:.2f}m")  # Output: ~82.66m
```

### Test GPS Verification
```python
from backend.app.utils.geofencing import GeofencingService

result = GeofencingService.verify_geofence(
    28.6145, 77.2095,  # Student
    28.6139, 77.2090,  # Teacher
    100  # Max distance
)
print(result)
# {'verified': True, 'distance_meters': 82.66, ...}
```

### Test WiFi Fallback
```python
from backend.app.utils.geofencing import GeofencingService

whitelisted = ['College-WiFi', 'College-Staff']
result = GeofencingService.check_wifi_fallback(
    'College-WiFi', whitelisted
)
print(result)
# {'verified': True, 'ssid': 'College-WiFi', ...}
```

---

## 📊 Database Queries

### Check WiFi Networks
```sql
SELECT * FROM wifi_whitelist WHERE is_active = TRUE;
```

### Check Geofence Config
```sql
SELECT * FROM geofence_config;
```

### View Verification Methods Used
```sql
SELECT 
    verification_method,
    COUNT(*) as count,
    ROUND(AVG(distance_meters), 2) as avg_distance
FROM attendance
GROUP BY verification_method;
```

### Find GPS Failures
```sql
SELECT 
    s.student_id_card_number,
    a.gps_failure_count,
    a.verification_method,
    a.wifi_ssid,
    a.timestamp
FROM attendance a
JOIN students s ON a.student_id = s.id
WHERE a.gps_failure_count > 0
ORDER BY a.timestamp DESC;
```

---

## 🐛 Troubleshooting

### GPS Not Working
**Check browser permissions:**
```javascript
navigator.permissions.query({name: 'geolocation'})
  .then(result => console.log(result.state));
// Should be: "granted"
```

**Enable high accuracy:**
```javascript
// Already enabled in StudentPortal.jsx
enableHighAccuracy: true
```

### WiFi Button Not Showing
**Requirements:**
1. GPS must fail 2 times (counter shows 2/2)
2. `wifi_fallback_enabled` must be `true` in config
3. Frontend must have `checkWiFiFallback` function

**Check config:**
```sql
SELECT * FROM geofence_config 
WHERE config_key = 'wifi_fallback_enabled';
```

### Distance Seems Wrong
**Common issues:**
1. Latitude/longitude swapped?
2. Using degrees (not radians)?
3. Comparing with Euclidean distance?

**Verify with test:**
```bash
python backend/test_geofencing.py
```

---

## 📈 Performance

### Haversine Calculation
- Speed: <1ms
- Accuracy: ±1 meter
- Memory: O(1)

### GPS Timeout
- Default: 10 seconds
- High accuracy: May take longer
- Fallback: After 2 attempts

### Database Lookups
- WiFi SSID: <1ms (indexed)
- Config: <1ms (indexed)
- Session: <1ms (indexed)

---

## 🎉 Success Indicators

✅ SQL migration completed without errors
✅ Test suite passes all 5 tests
✅ Frontend shows GPS accuracy (±Xm)
✅ Frontend shows failure counter (X/2)
✅ WiFi button appears after 2 failures
✅ Distance threshold is 100m (not 50m)
✅ High accuracy GPS enabled

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `backend/migration_geofencing_fix.sql` | Database migration |
| `backend/app/utils/geofencing.py` | Geofencing service |
| `backend/app/api/geofencing_endpoints.py` | API endpoints |
| `backend/test_geofencing.py` | Test suite |
| `frontend/src/pages/StudentPortal.jsx` | Student UI |
| `GEOFENCING_FIX_COMPLETE.md` | Full documentation |

---

## 🔗 API Endpoints

### POST /api/verify-gps
Verify location using GPS coordinates.

**Request:**
```json
{
  "session_id": "abc-123",
  "student_id": "STU001",
  "latitude": 28.6145,
  "longitude": 77.2095,
  "accuracy": 30.0
}
```

**Response:**
```json
{
  "verified": true,
  "distance_meters": 82.66,
  "max_distance": 100,
  "message": "Student is 82.66m from teacher (limit: 100m)",
  "method": "gps"
}
```

### POST /api/verify-wifi
Verify location using WiFi SSID.

**Request:**
```json
{
  "session_id": "abc-123",
  "wifi_ssid": "College-WiFi"
}
```

**Response:**
```json
{
  "verified": true,
  "ssid": "College-WiFi",
  "message": "WiFi verification successful: College-WiFi",
  "method": "wifi"
}
```

### GET /api/wifi-networks
Get whitelisted WiFi networks.

**Response:**
```json
{
  "networks": [
    {
      "ssid": "College-WiFi",
      "location": "Main Campus Network",
      "active": true
    }
  ]
}
```

---

## ✨ That's It!

Your geofencing system is now production-ready with:
- ✅ Accurate distance calculation (Haversine formula)
- ✅ Reasonable threshold (100m for indoor GPS drift)
- ✅ High accuracy GPS mode
- ✅ WiFi fallback after 2 GPS failures
- ✅ Comprehensive logging and audit trail

**Ready to test? Run the 3 steps at the top!** 🚀
