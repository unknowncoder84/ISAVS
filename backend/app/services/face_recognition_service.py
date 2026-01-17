"""
Face Recognition Service
Handles face detection, embedding extraction, and similarity comparison.
Uses DeepFace with VGG-Face model for accurate face recognition.
"""
import base64
import io
import os
from typing import Optional, List, Tuple
import numpy as np
import cv2

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️ DeepFace not available, using fallback method")

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import StudentORM
from app.models.domain import StudentMatch, FaceVerificationResult
from app.core.config import settings


class FaceRecognitionService:
    """Service for face recognition operations using DeepFace."""
    
    def __init__(self, similarity_threshold: float = None):
        self.similarity_threshold = similarity_threshold or settings.FACE_SIMILARITY_THRESHOLD
        
        # Load OpenCV's face detector as backup
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # DeepFace model (will be loaded on first use)
        self.model_name = "VGG-Face"  # Fast and accurate
        self.detector_backend = "opencv"  # Fast detection
    
    def decode_base64_image(self, base64_string: str) -> Optional[np.ndarray]:
        """Decode base64 image string to numpy array."""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            image_bytes = base64.b64decode(base64_string)
            nparr = np.frombuffer(image_bytes, np.uint8)
            
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            print(f"Error decoding image: {e}")
            return None
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect all faces in image and return bounding boxes.
        Returns list of (x, y, w, h) tuples.
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            return faces.tolist() if len(faces) > 0 else []
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def extract_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract facial embedding from image using DeepFace.
        Returns 128-dimensional feature vector or None if no face detected.
        """
        if not DEEPFACE_AVAILABLE:
            print("⚠️ DeepFace not available, using fallback")
            return self._extract_embedding_fallback(image)
        
        try:
            # DeepFace expects RGB image
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract embedding using DeepFace
            embedding_objs = DeepFace.represent(
                img_path=rgb_image,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                enforce_detection=True
            )
            
            if not embedding_objs or len(embedding_objs) == 0:
                print("No face detected by DeepFace")
                return None
            
            # Get first face embedding
            embedding = np.array(embedding_objs[0]["embedding"], dtype=np.float64)
            
            # Normalize to 128 dimensions if needed
            if len(embedding) != 128:
                # Resize to 128 dimensions
                if len(embedding) > 128:
                    embedding = embedding[:128]
                else:
                    # Pad with zeros
                    embedding = np.pad(embedding, (0, 128 - len(embedding)), 'constant')
            
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
            
        except ValueError as e:
            # No face detected
            print(f"No face detected: {e}")
            return None
        except Exception as e:
            print(f"Error extracting embedding with DeepFace: {e}")
            # Try fallback method
            return self._extract_embedding_fallback(image)
    
    def _extract_embedding_fallback(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Fallback method using simple histogram features.
        Used when DeepFace is not available or fails.
        """
        try:
            # Detect faces
            faces = self.detect_faces(image)
            
            if len(faces) == 0:
                print("No face detected in fallback method")
                return None
            
            # Use first face
            x, y, w, h = faces[0]
            face_roi = image[y:y+h, x:x+w]
            
            # Resize to standard size
            face_roi = cv2.resize(face_roi, (128, 128))
            
            # Convert to grayscale
            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Use histogram as embedding
            hist = cv2.calcHist([gray_face], [0], None, [128], [0, 256])
            embedding = hist.flatten().astype(np.float64)
            
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
            
        except Exception as e:
            print(f"Error in fallback embedding: {e}")
            return None
    
    def extract_embedding_from_base64(self, base64_image: str) -> Optional[np.ndarray]:
        """Extract embedding from base64 encoded image."""
        image = self.decode_base64_image(base64_image)
        if image is None:
            return None
        return self.extract_embedding(image)
    
    def extract_centroid_embedding(self, frames: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        Extract embeddings from multiple frames and compute mean centroid.
        This is the 2026 standard for enrollment - captures 10 frames and averages.
        
        Args:
            frames: List of image frames (typically 10 frames)
        
        Returns:
            Centroid embedding (mean of all valid embeddings) or None if insufficient frames
        """
        embeddings = []
        
        for i, frame in enumerate(frames):
            embedding = self.extract_embedding(frame)
            if embedding is not None:
                embeddings.append(embedding)
                print(f"✓ Frame {i+1}/{len(frames)}: Embedding extracted")
            else:
                print(f"✗ Frame {i+1}/{len(frames)}: No face detected")
        
        # Require at least 5 valid frames out of 10
        min_required_frames = max(5, len(frames) // 2)
        
        if len(embeddings) < min_required_frames:
            print(f"⚠️ Insufficient valid frames: {len(embeddings)}/{len(frames)} (need {min_required_frames})")
            return None
        
        # Compute centroid (mean) of all embeddings
        centroid = np.mean(embeddings, axis=0)
        
        # Normalize the centroid
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm
        
        print(f"✓ Centroid computed from {len(embeddings)} frames")
        
        return centroid
    
    def extract_centroid_from_base64_frames(self, base64_frames: List[str]) -> Optional[np.ndarray]:
        """
        Extract centroid embedding from list of base64 encoded frames.
        Convenience method for API endpoints.
        """
        frames = []
        for base64_frame in base64_frames:
            image = self.decode_base64_image(base64_frame)
            if image is not None:
                frames.append(image)
        
        if len(frames) == 0:
            return None
        
        return self.extract_centroid_embedding(frames)
    
    @staticmethod
    def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        Returns value between -1 and 1 (1 = identical, 0 = orthogonal).
        """
        embedding1 = np.array(embedding1, dtype=np.float64)
        embedding2 = np.array(embedding2, dtype=np.float64)
        
        # Handle zero vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        dot_product = np.dot(embedding1, embedding2)
        similarity = dot_product / (norm1 * norm2)
        
        # Clamp to valid range due to floating point errors
        return float(np.clip(similarity, -1.0, 1.0))
    
    def compare_embeddings(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray,
        threshold: float = None
    ) -> Tuple[bool, float]:
        """
        Compare two embeddings and determine if they match.
        Returns (is_match, similarity_score).
        """
        threshold = threshold or self.similarity_threshold
        similarity = self.cosine_similarity(embedding1, embedding2)
        is_match = similarity >= threshold
        return is_match, similarity
    
    async def find_matching_student(
        self,
        embedding: np.ndarray,
        db: AsyncSession,
        threshold: float = None
    ) -> Optional[StudentMatch]:
        """
        Find student with matching facial embedding in database.
        Returns best match above threshold, or None if no match.
        """
        threshold = threshold or self.similarity_threshold
        
        # Query all students with embeddings
        result = await db.execute(
            select(StudentORM).where(StudentORM.facial_embedding.isnot(None))
        )
        students = result.scalars().all()
        
        best_match: Optional[StudentMatch] = None
        best_similarity = threshold
        
        for student in students:
            stored_embedding = np.array(student.facial_embedding, dtype=np.float64)
            similarity = self.cosine_similarity(embedding, stored_embedding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = StudentMatch(
                    student_id=student.id,
                    student_name=student.name,
                    student_id_card_number=student.student_id_card_number,
                    similarity=similarity
                )
        
        return best_match
    
    async def verify_student_face(
        self,
        base64_image: str,
        student_id: int,
        db: AsyncSession,
        liveness_passed: bool = True
    ) -> FaceVerificationResult:
        """
        Verify that the face in image matches the specified student.
        """
        # Extract embedding from image
        embedding = self.extract_embedding_from_base64(base64_image)
        
        if embedding is None:
            return FaceVerificationResult(
                verified=False,
                confidence=0.0,
                student_id=None,
                liveness_passed=liveness_passed,
                message="No face detected in image"
            )
        
        # Get student from database
        result = await db.execute(
            select(StudentORM).where(StudentORM.id == student_id)
        )
        student = result.scalar_one_or_none()
        
        if student is None:
            return FaceVerificationResult(
                verified=False,
                confidence=0.0,
                student_id=None,
                liveness_passed=liveness_passed,
                message="Student not found"
            )
        
        # Compare embeddings
        stored_embedding = np.array(student.facial_embedding, dtype=np.float64)
        is_match, similarity = self.compare_embeddings(embedding, stored_embedding)
        
        return FaceVerificationResult(
            verified=is_match,
            confidence=similarity,
            student_id=student.id if is_match else None,
            liveness_passed=liveness_passed,
            message="Face verified" if is_match else f"Face similarity {similarity:.2f} below threshold"
        )


# Singleton instance
_face_service: Optional[FaceRecognitionService] = None


def get_face_recognition_service() -> FaceRecognitionService:
    """Get or create face recognition service instance."""
    global _face_service
    if _face_service is None:
        _face_service = FaceRecognitionService()
    return _face_service
