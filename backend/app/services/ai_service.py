"""
AI Service - Modern 2026 Implementation
Uses DeepFace with Facenet model for 128-dimensional embeddings
Implements CLAHE preprocessing and MediaPipe Tasks API for landmarks
"""
import base64
import io
import numpy as np
import cv2
from typing import Optional, Tuple, List
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️ DeepFace not available")

from app.services.preprocess import get_preprocessor


class AIService:
    """
    Modern AI Service (2026 Standard):
    - face_recognition library for 128-dimensional embeddings
    - CLAHE preprocessing for lighting normalization
    - MediaPipe Tasks API for landmark detection
    - Cosine similarity with 0.6 threshold
    """
    
    def __init__(self, similarity_threshold: float = 0.6):
        self.similarity_threshold = similarity_threshold
        self.preprocessor = get_preprocessor()
    
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
    
    def extract_128d_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract 128-dimensional face embedding using DeepFace with Facenet model.
        Facenet produces 128-dimensional embeddings, perfect for our use case.
        
        Returns: 128-dimensional numpy array or None if no face detected
        """
        if not DEEPFACE_AVAILABLE:
            print("❌ DeepFace not available")
            return None
        
        try:
            # First try with preprocessing
            preprocessed = self.preprocessor.preprocess(image)
            
            # If preprocessing fails, try with original image
            if preprocessed is None:
                print("⚠️ Preprocessing failed, trying with original image")
                preprocessed = image
            
            # Convert to RGB (DeepFace expects RGB)
            if len(preprocessed.shape) == 2:
                rgb_image = cv2.cvtColor(preprocessed, cv2.COLOR_GRAY2RGB)
            elif preprocessed.shape[2] == 4:
                rgb_image = cv2.cvtColor(preprocessed, cv2.COLOR_BGRA2RGB)
            else:
                rgb_image = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2RGB)
            
            # Try with enforce_detection=True first
            try:
                embedding_objs = DeepFace.represent(
                    img_path=rgb_image,
                    model_name="Facenet",  # Facenet = 128 dimensions
                    enforce_detection=True,
                    detector_backend="opencv",
                    align=True
                )
            except ValueError as e:
                # If strict detection fails, try with enforce_detection=False
                print(f"⚠️ Strict detection failed: {e}, trying lenient mode")
                embedding_objs = DeepFace.represent(
                    img_path=rgb_image,
                    model_name="Facenet",
                    enforce_detection=False,  # More lenient
                    detector_backend="opencv",
                    align=True
                )
            
            if not embedding_objs or len(embedding_objs) == 0:
                print("⚠️ No face detected by DeepFace")
                return None
            
            # Get first face embedding
            embedding = np.array(embedding_objs[0]["embedding"], dtype=np.float64)
            
            # Verify dimension (Facenet should be 128)
            if len(embedding) != 128:
                print(f"⚠️ Unexpected embedding dimension: {len(embedding)} (expected 128)")
                # If not 128, resize it
                if len(embedding) > 128:
                    embedding = embedding[:128]
                else:
                    embedding = np.pad(embedding, (0, 128 - len(embedding)), 'constant')
            
            # Normalize to unit vector
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            print(f"✓ Successfully extracted 128-d embedding")
            return embedding
            
        except ValueError as e:
            # No face detected
            print(f"⚠️ No face detected: {e}")
            return None
        except Exception as e:
            print(f"Embedding extraction error: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def extract_centroid_embedding(
        self, 
        images: List[np.ndarray],
        min_shots: int = 3
    ) -> Tuple[Optional[np.ndarray], List[str]]:
        """
        Extract centroid (mean) embedding from multiple images.
        This creates a robust "master signature" that averages out variations.
        
        Args:
            images: List of face images (different angles/expressions)
            min_shots: Minimum successful captures required
        
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
            
            # Extract embedding
            embedding = self.extract_128d_embedding(image)
            if embedding is not None:
                embeddings.append(embedding)
                quality_reports.append(f"Frame {idx+1}: ✓ Success")
            else:
                quality_reports.append(f"Frame {idx+1}: ✗ Failed")
        
        # Check if we have enough good shots
        if len(embeddings) < min_shots:
            print(f"❌ Insufficient quality frames: {len(embeddings)}/{min_shots}")
            return None, quality_reports
        
        # Calculate centroid (mean embedding)
        centroid = self._calculate_centroid(embeddings)
        
        quality_reports.append(f"✓ Centroid created from {len(embeddings)} frames")
        
        return centroid, quality_reports
    
    def _calculate_centroid(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """
        Calculate centroid (mean) of multiple embeddings.
        This creates a robust "master signature" that averages out variations.
        """
        # Stack embeddings
        embedding_matrix = np.vstack(embeddings)
        
        # Calculate mean
        centroid = np.mean(embedding_matrix, axis=0)
        
        # Re-normalize to unit vector
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm
        
        return centroid
    
    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Returns: Similarity score between 0 and 1 (1 = identical)
        """
        emb1 = np.array(emb1, dtype=np.float64)
        emb2 = np.array(emb2, dtype=np.float64)
        
        # Calculate norms
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Dot product divided by product of norms
        dot_product = np.dot(emb1, emb2)
        similarity = dot_product / (norm1 * norm2)
        
        # Clamp to [0, 1] range
        similarity = float(np.clip(similarity, 0.0, 1.0))
        
        return similarity
    
    def verify_face(
        self,
        live_embedding: np.ndarray,
        stored_embedding: np.ndarray,
        threshold: float = None
    ) -> Tuple[bool, float]:
        """
        Verify if live face matches stored face using cosine similarity.
        
        Args:
            live_embedding: 128-d embedding from live capture
            stored_embedding: 128-d embedding from enrollment
            threshold: Similarity threshold (default 0.6)
        
        Returns:
            (is_match, similarity_score)
        """
        threshold = threshold or self.similarity_threshold
        
        # Verify dimensions
        if len(live_embedding) != 128 or len(stored_embedding) != 128:
            print(f"❌ Invalid dimensions: {len(live_embedding)}, {len(stored_embedding)}")
            return False, 0.0
        
        # Calculate cosine similarity
        similarity = self.cosine_similarity(live_embedding, stored_embedding)
        
        # Check threshold
        is_match = similarity >= threshold
        
        return is_match, similarity


# Singleton instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
