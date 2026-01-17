# ISAVS 2026 - Hugging Face / InsightFace Migration Plan

## Executive Summary
Migrate from DeepFace to InsightFace for professional-grade face recognition with emotion-based liveness detection.

## Current State
- **Model**: DeepFace with Facenet
- **Embedding**: 128-dimensional
- **Threshold**: 0.6 cosine similarity
- **Liveness**: Blink detection (MediaPipe)

## Target State
- **Model**: InsightFace buffalo_l
- **Embedding**: 512-dimensional (more accurate)
- **Threshold**: 0.4 cosine similarity (adjusted for 512-d)
- **Liveness**: Smile detection (emotion recognition)
- **UI**: Green smiley feedback on face detection

## Migration Steps

### Phase 1: Backend - Model Upgrade ✅ READY TO IMPLEMENT

#### 1.1 Install InsightFace
```bash
pip install insightface onnxruntime
```

#### 1.2 Create New AI Service (Backward Compatible)
**File**: `backend/app/services/insightface_service.py`

Features:
- 512-dimensional embeddings (buffalo_l model)
- Emotion detection for liveness
- Fallback to DeepFace if InsightFace fails
- Strict dimension validation: `assert embedding.shape == (512,)`

#### 1.3 Update Database Schema
**Migration**: Add support for both 128-d and 512-d embeddings
```sql
ALTER TABLE students ADD COLUMN embedding_dimension INTEGER DEFAULT 128;
ALTER TABLE students ADD COLUMN embedding_model VARCHAR(50) DEFAULT 'facenet';
```

#### 1.4 Update Configuration
**File**: `backend/.env`
```env
# AI Model Selection
AI_MODEL=insightface  # Options: insightface, deepface
EMBEDDING_DIMENSION=512
FACE_SIMILARITY_THRESHOLD=0.4  # Lower for 512-d embeddings

# Liveness Detection
LIVENESS_METHOD=emotion  # Options: emotion, blink
REQUIRE_SMILE=true
SMILE_CONFIDENCE_THRESHOLD=0.7
```

### Phase 2: Emotion-Based Liveness ✅ READY TO IMPLEMENT

#### 2.1 Emotion Detection Service
**File**: `backend/app/services/emotion_service.py`

Features:
- Detect 7 emotions: Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral
- Require "Happy" emotion for attendance
- Confidence threshold: 0.7
- Fallback to blink detection if emotion fails

#### 2.2 Update Verification Pipeline
**File**: `backend/app/services/verification_pipeline.py`

Changes:
- Add emotion check before face verification
- Return emotion confidence in response
- Log emotion data for analytics

### Phase 3: Frontend - UI Enhancements ✅ READY TO IMPLEMENT

#### 3.1 Face Detection Feedback
**File**: `frontend/src/components/WebcamCapture.tsx`

Features:
- Green smiley icon when face detected
- Pulsing animation on successful match (>0.4 similarity)
- Red frown icon if no face detected
- Yellow neutral face during processing

#### 3.2 Smile-to-Verify UI
**File**: `frontend/src/components/KioskView.tsx`

Features:
- "Please smile for verification" prompt
- Real-time emotion feedback
- Green checkmark when smile detected
- Countdown timer (30 seconds)
- Geofence status indicator

#### 3.3 Emotion Visualization
**Component**: `EmotionFeedback.tsx`

Features:
- Display detected emotion
- Confidence bar
- Animated emoji transitions
- Accessibility-friendly colors

### Phase 4: Integration & Testing

#### 4.1 Backward Compatibility
- Support both 128-d (DeepFace) and 512-d (InsightFace) embeddings
- Auto-detect embedding dimension from database
- Gradual migration: new enrollments use InsightFace, old ones keep DeepFace

#### 4.2 Property-Based Tests
**Files**: 
- `backend/tests/test_property_insightface.py`
- `backend/tests/test_property_emotion.py`

Tests:
- Embedding dimension validation (512-d)
- Emotion detection accuracy
- Smile-to-verify workflow
- Geofence + emotion combination

#### 4.3 Performance Benchmarks
- InsightFace vs DeepFace speed comparison
- Emotion detection latency
- End-to-end verification time

## Technical Specifications

### InsightFace Model Details
- **Model**: buffalo_l (Large variant)
- **Embedding**: 512-dimensional
- **Accuracy**: 99.8% on LFW dataset
- **Speed**: ~50ms per face (GPU), ~200ms (CPU)
- **Size**: ~100MB download

### Emotion Detection
- **Model**: InsightFace emotion recognition
- **Emotions**: 7 classes (Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral)
- **Threshold**: 0.7 confidence for "Happy"
- **Fallback**: Blink detection if emotion fails

### Cosine Similarity Thresholds
- **128-d (DeepFace)**: 0.6 threshold
- **512-d (InsightFace)**: 0.4 threshold (more discriminative)

## Implementation Timeline

### Week 1: Backend Migration
- Day 1-2: Install InsightFace, create service
- Day 3-4: Update database schema, add migration
- Day 5: Emotion detection service
- Day 6-7: Integration testing

### Week 2: Frontend Enhancement
- Day 1-2: Face detection feedback UI
- Day 3-4: Smile-to-verify component
- Day 5: Emotion visualization
- Day 6-7: Integration testing

### Week 3: Testing & Deployment
- Day 1-3: Property-based tests
- Day 4-5: Performance benchmarks
- Day 6: Staging deployment
- Day 7: Production rollout

## Rollback Plan

If issues arise:
1. Set `AI_MODEL=deepface` in .env
2. System automatically falls back to DeepFace
3. No data loss (both embeddings stored)
4. Gradual re-migration when ready

## Success Metrics

- **Accuracy**: >99% face recognition accuracy
- **Speed**: <500ms end-to-end verification
- **Liveness**: >95% smile detection accuracy
- **User Experience**: <3 seconds from smile to attendance marked
- **False Positives**: <0.1% (proxy attempts)

## Security Considerations

- Emotion detection prevents photo/video spoofing
- Geofence ensures physical presence
- OTP prevents credential sharing
- 4-factor authentication (Face + ID + OTP + Location + Emotion)

## Next Steps

1. **Approve Migration Plan**
2. **Install InsightFace**: `pip install insightface onnxruntime`
3. **Implement Backend Service** (2-3 hours)
4. **Update Frontend UI** (2-3 hours)
5. **Test & Deploy** (1-2 hours)

**Total Estimated Time**: 1-2 days for full migration

---

**Ready to proceed?** I can start implementing the InsightFace service and emotion detection immediately.
