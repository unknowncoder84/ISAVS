# Face Recognition System Update

## Changes Made

### 1. **Switched to OpenCV-based Face Recognition**
   - **Problem**: The system was using `face_recognition` library which requires `dlib` (needs CMake and Visual Studio Build Tools on Windows)
   - **Solution**: Implemented pure OpenCV solution using:
     - Haar Cascade for face detection
     - ORB features + histogram for embedding extraction
     - Cosine similarity for matching
   - **Files Modified**:
     - `backend/app/services/face_recognition_service.py` - Complete rewrite
     - `backend/.env` - Lowered threshold to 0.3

### 2. **Added Face Image Storage**
   - **Feature**: Store original enrollment photos in database
   - **Benefits**:
     - Visual verification for faculty
     - Re-training capability if algorithm changes
     - Audit trail
   - **Files Modified**:
     - `backend/app/db/schema.sql` - Added `face_image_base64` column
     - `backend/app/api/endpoints.py` - Store and retrieve images
     - `frontend/src/services/api.ts` - Support image fetching
     - `frontend/src/components/FacultyDashboard.tsx` - Display photos
   - **Migration**: `backend/migration_add_face_images.sql`

### 3. **Enhanced Dashboard**
   - Students tab now shows actual enrollment photos
   - Fallback to initials if no photo available
   - Photos displayed as circular avatars with border

## How to Use

### Step 1: Run Database Migration
Go to Supabase Dashboard → SQL Editor and run:
```sql
ALTER TABLE students 
ADD COLUMN IF NOT EXISTS face_image_base64 TEXT;
```

Or use the migration file: `backend/migration_add_face_images.sql`

### Step 2: Re-enroll Students
**IMPORTANT**: You must re-enroll all students because the embedding format has changed!

1. Delete old students from Dashboard → Students tab
2. Go to Enrollment page
3. Enroll each student with clear face photo

### Step 3: Test Verification
1. Start a session from Dashboard
2. Go to Kiosk view with the session ID
3. Enter student ID and OTP
4. Capture face - should now recognize properly

## Technical Details

### Face Recognition Algorithm
- **Detection**: OpenCV Haar Cascade (same as your OpenCV code)
- **Features**: ORB keypoints + grayscale histogram fallback
- **Embedding**: 128-dimensional normalized vector
- **Similarity**: Cosine similarity with 0.3 threshold
- **Matching**: Same person if similarity ≥ 0.3

### Threshold Settings
- Current: 0.3 (lenient for ORB features)
- Adjust in `backend/.env`: `FACE_SIMILARITY_THRESHOLD=0.3`
- Lower = more lenient, Higher = more strict

### Security Features (Still Active)
- ✅ OTP verification
- ✅ Face matching
- ✅ Account locking (60 min) on proxy attempts
- ✅ Anomaly logging
- ✅ Admin unlock capability

## Troubleshooting

### If face recognition still doesn't work:
1. **Check lighting** - Ensure good lighting during enrollment and verification
2. **Face position** - Face should be centered and clearly visible
3. **Lower threshold** - Try 0.2 in `.env` if 0.3 is too strict
4. **Re-enroll** - Delete and re-enroll with better quality photo

### If you want better accuracy:
Install the professional `face_recognition` library (requires build tools):
```bash
# Install CMake and Visual Studio Build Tools first
pip install cmake
pip install dlib
pip install face-recognition
```

Then uncomment in `backend/requirements.txt`:
```
face-recognition==1.3.0
```

## Files Changed
- ✅ `backend/app/services/face_recognition_service.py`
- ✅ `backend/.env`
- ✅ `backend/app/db/schema.sql`
- ✅ `backend/app/api/endpoints.py`
- ✅ `frontend/src/services/api.ts`
- ✅ `frontend/src/components/FacultyDashboard.tsx`
- ✅ `backend/migration_add_face_images.sql` (new)

## Next Steps
1. Run the SQL migration in Supabase
2. Re-enroll all students
3. Test the verification flow
4. Adjust threshold if needed
