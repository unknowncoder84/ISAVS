"""
Multi-Shot Enrollment Engine
Captures multiple frames and creates robust centroid embeddings
UPDATED: Uses DeepFace library with VGG-Face model for accurate embeddings
"""
import numpy as np
from typing import List, Optional, Tuple
import cv2

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️ DeepFace not available, using fallback")

from app.services.preprocess import get_preprocessor


class EnrollmentEngine:
    """
    Production-grade enrollment with:
    - Multi-shot capture (5-10 frames)
    - Centroid embedding (average of multiple shots)
    - Quality validation
    - face_recognition library (dlib deep learning)
    """
    
    def __init__(self):
        self.preprocessor = get_preprocessor()
        self.min_shots = 3  # Minimum successful captures
        self.max_shots = 10  # Maximum captures to attempt
    
    def enroll_multi_shot(
        self, 
        images: List[np.ndarray]
    ) -> Tuple[Optional[np.ndarray], List[str]]:
        """
        Process multiple images and create centroid embedding.
        
        Args:
            images: List of face images (different angles/expressions)
        
        Returns:
            (centroid_embedding, quality_reports)
        """
        embeddings = []
        quality_reports = []
        
        for idx, image in enumerate(images):
            # Quality check
            is_good, reason = self.preprocessor.quality_check(image)
            quality_reports.append(f"Frame {idx+1}: {reason}")
            
            if not is_good:
                print(f"⚠️ Frame {idx+1} rejected: {reason}")
                continue
            
            # Preprocess
            preprocessed = self.preprocessor.preprocess(image)
            if preprocessed is None:
                quality_reports.append(f"Frame {idx+1}: Preprocessing failed")
                continue
            
            # Extract embedding
            embedding = self._extract_embedding_robust(preprocessed)
            if embedding is not None:
                embeddings.append(embedding)
                quality_reports.append(f"Frame {idx+1}: ✓ Success")
        
        # Check if we have enough good shots
        if len(embeddings) < self.min_shots:
            print(f"❌ Insufficient quality frames: {len(embeddings)}/{self.min_shots}")
            return None, quality_reports
        
        # Calculate centroid (mean embedding)
        centroid = self._calculate_centroid(embeddings)
        
        quality_reports.append(f"✓ Centroid created from {len(embeddings)} frames")
        
        return centroid, quality_reports
    
    def enroll_single_with_validation(
        self, 
        image: np.ndarray
    ) -> Tuple[Optional[np.ndarray], str]:
        """
        Enroll from single image with strict validation.
        Use this for backward compatibility.
        """
        # Quality check
        is_good, reason = self.preprocessor.quality_check(image)
        if not is_good:
            return None, f"Quality check failed: {reason}"
        
        # Preprocess
        preprocessed = self.preprocessor.preprocess(image)
        if preprocessed is None:
            return None, "Face preprocessing failed"
        
        # Extract embedding
        embedding = self._extract_embedding_robust(preprocessed)
        if embedding is None:
            return None, "Embedding extraction failed - no face detected"
        
        return embedding, "Success"
    
    def _extract_embedding_robust(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract facial embedding using DeepFace with VGG-Face model.
        This is MUCH more accurate than HOG features.
        VGG-Face is a deep learning model trained on millions of faces.
        """
        if not DEEPFACE_AVAILABLE:
            print("⚠️ DeepFace not available, using fallback")
            return self._extract_embedding_fallback(image)
        
        try:
            # Convert to RGB if needed
            if len(image.shape) == 2:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            else:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Use DeepFace to extract embedding
            # VGG-Face model produces 2622-dimensional embeddings
            # enforce_detection=False allows processing even if face detection is uncertain
            embedding_objs = DeepFace.represent(
                img_path=rgb_image,
                model_name="VGG-Face",
                enforce_detection=True,
                detector_backend="opencv",
                align=True
            )
            
            if not embedding_objs or len(embedding_objs) == 0:
                print("⚠️ No face detected by DeepFace")
                return None
            
            # Get first face embedding
            embedding = np.array(embedding_objs[0]["embedding"], dtype=np.float64)
            
            # Normalize to unit vector
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
            
        except Exception as e:
            print(f"DeepFace embedding extraction error: {e}")
            import traceback
            print(traceback.format_exc())
            return self._extract_embedding_fallback(image)
    
    def _extract_embedding_fallback(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Fallback method using HOG features.
        Only used if face_recognition library is not available.
        """
        try:
            from skimage.feature import hog
            
            # Ensure image is the right size
            if image.shape[:2] != (224, 224):
                image = cv2.resize(image, (224, 224))
            
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Extract HOG features
            hog_features = hog(
                gray,
                orientations=9,
                pixels_per_cell=(8, 8),
                cells_per_block=(2, 2),
                block_norm='L2-Hys',
                feature_vector=True
            )
            
            # Reduce to 128 dimensions
            if len(hog_features) > 128:
                indices = np.linspace(0, len(hog_features)-1, 128, dtype=int)
                embedding = hog_features[indices]
            else:
                embedding = np.pad(hog_features, (0, max(0, 128 - len(hog_features))), 'constant')[:128]
            
            # Normalize
            embedding = embedding.astype(np.float64)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
            
        except Exception as e:
            print(f"Fallback embedding error: {e}")
            return None
    
    def _calculate_centroid(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """
        Calculate centroid (mean) of multiple embeddings.
        This creates a robust "master signature" that averages out variations.
        """
        # Stack embeddings
        embedding_matrix = np.vstack(embeddings)
        
        # Calculate mean
        centroid = np.mean(embedding_matrix, axis=0)
        
        # Re-normalize
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm
        
        return centroid
    
    def validate_embedding_quality(
        self, 
        embeddings: List[np.ndarray]
    ) -> Tuple[bool, str]:
        """
        Validate that embeddings are consistent (not too much variation).
        High variation indicates poor quality captures.
        """
        if len(embeddings) < 2:
            return True, "Single embedding, no variance check"
        
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = self._cosine_similarity(embeddings[i], embeddings[j])
                similarities.append(sim)
        
        avg_similarity = np.mean(similarities)
        min_similarity = np.min(similarities)
        
        # Check consistency
        if avg_similarity < 0.7:
            return False, f"Low consistency (avg: {avg_similarity:.2f}). Captures too different."
        
        if min_similarity < 0.5:
            return False, f"Outlier detected (min: {min_similarity:.2f}). Re-capture needed."
        
        return True, f"Good consistency (avg: {avg_similarity:.2f})"
    
    @staticmethod
    def _cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Singleton instance
_enrollment_engine: Optional[EnrollmentEngine] = None


def get_enrollment_engine() -> EnrollmentEngine:
    """Get or create enrollment engine instance."""
    global _enrollment_engine
    if _enrollment_engine is None:
        _enrollment_engine = EnrollmentEngine()
    return _enrollment_engine
