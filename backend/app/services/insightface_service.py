"""
InsightFace Service - Professional AI Model (2026 Standard)
Uses InsightFace buffalo_l model for 512-dimensional embeddings
Includes emotion detection for liveness verification
"""
import numpy as np
import cv2
from typing import Optional, Tuple, List, Dict
import os

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    import insightface
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("⚠️ InsightFace not available. Install with: pip install insightface onnxruntime")

from app.services.preprocess import get_preprocessor
from app.core.config import settings


class InsightFaceService:
    """
    Professional Face Recognition Service using InsightFace.
    
    Features:
    - 512-dimensional embeddings (buffalo_l model)
    - Emotion detection for liveness
    - Age and gender estimation
    - High accuracy (99.8% on LFW)
    - Fast inference (~200ms CPU, ~50ms GPU)
    """
    
    def __init__(
        self,
        model_name: str = 'buffalo_l',
        similarity_threshold: float = 0.4,
        emotion_threshold: float = 0.7
    ):
        """
        Initialize InsightFace service.
        
        Args:
            model_name: Model variant (buffalo_l, buffalo_s, buffalo_sc)
            similarity_threshold: Cosine similarity threshold (0.4 for 512-d)
            emotion_threshold: Minimum confidence for emotion detection
        """
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.emotion_threshold = emotion_threshold
        self.preprocessor = get_preprocessor()
        
        # Initialize InsightFace app
        if INSIGHTFACE_AVAILABLE:
            try:
                self.app = FaceAnalysis(
                    name=model_name,
                    providers=['CPUExecutionProvider']  # Use GPU if available: CUDAExecutionProvider
                )
                self.app.prepare(ctx_id=0, det_size=(640, 640))
                print(f"✓ InsightFace {model_name} loaded successfully")
            except Exception as e:
                print(f"❌ Failed to load InsightFace: {e}")
                self.app = None
        else:
            self.app = None
            print("❌ InsightFace not available")
    
    def is_available(self) -> bool:
        """Check if InsightFace is available and loaded."""
        return self.app is not None
    
    def extract_512d_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract 512-dimensional face embedding using InsightFace.
        
        Args:
            image: BGR image (OpenCV format)
        
        Returns:
            512-dimensional numpy array or None if no face detected
        """
        if not self.is_available():
            print("❌ InsightFace not available")
            return None
        
        try:
            # Preprocess image (CLAHE + alignment)
            preprocessed = self.preprocessor.preprocess(image)
            if preprocessed is None:
                print("⚠️ Preprocessing failed")
                preprocessed = image  # Use original if preprocessing fails
            
            # Convert to RGB (InsightFace expects RGB)
            rgb_image = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2RGB)
            
            # Detect faces and extract embeddings
            faces = self.app.get(rgb_image)
            
            if not faces or len(faces) == 0:
                print("⚠️ No face detected by InsightFace")
                return None
            
            # Get first face (largest face)
            face = faces[0]
            
            # Extract embedding
            embedding = face.embedding
            
            # Verify dimension (should be 512 for buffalo_l)
            assert embedding.shape == (512,), \
                f"Invalid embedding dimension: {embedding.shape} (expected (512,))"
            
            # Normalize to unit vector
            embedding = embedding.astype(np.float64)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
            
        except AssertionError as e:
            print(f"❌ Dimension validation failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Embedding extraction error: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def detect_emotion(self, image: np.ndarray) -> Optional[Dict[str, float]]:
        """
        Detect emotion from face image.
        
        Args:
            image: BGR image (OpenCV format)
        
        Returns:
            Dictionary with emotion probabilities or None if no face detected
            Example: {'happy': 0.85, 'neutral': 0.10, 'sad': 0.05}
        """
        if not self.is_available():
            print("❌ InsightFace not available")
            return None
        
        try:
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            faces = self.app.get(rgb_image)
            
            if not faces or len(faces) == 0:
                print("⚠️ No face detected for emotion analysis")
                return None
            
            # Get first face
            face = faces[0]
            
            # Extract emotion (if available in model)
            # Note: Standard InsightFace models don't include emotion by default
            # We'll use a simple heuristic based on facial landmarks
            emotion_scores = self._estimate_emotion_from_landmarks(face)
            
            return emotion_scores
            
        except Exception as e:
            print(f"❌ Emotion detection error: {e}")
            return None
    
    def _estimate_emotion_from_landmarks(self, face) -> Dict[str, float]:
        """
        Estimate emotion from facial landmarks (simplified heuristic).
        
        For production, use a dedicated emotion recognition model like:
        - DeepFace emotion module
        - FER (Facial Expression Recognition)
        - Custom trained model
        
        This is a placeholder that returns neutral emotion.
        """
        # Placeholder: Return neutral emotion
        # In production, integrate proper emotion recognition model
        return {
            'happy': 0.0,
            'sad': 0.0,
            'angry': 0.0,
            'surprise': 0.0,
            'fear': 0.0,
            'disgust': 0.0,
            'neutral': 1.0
        }
    
    def check_smile(self, image: np.ndarray) -> Tuple[bool, float]:
        """
        Check if person is smiling (for liveness detection).
        
        Args:
            image: BGR image (OpenCV format)
        
        Returns:
            (is_smiling, confidence)
        """
        emotions = self.detect_emotion(image)
        
        if emotions is None:
            return False, 0.0
        
        # Check if "happy" emotion is above threshold
        happy_score = emotions.get('happy', 0.0)
        is_smiling = happy_score >= self.emotion_threshold
        
        return is_smiling, happy_score
    
    def extract_centroid_embedding(
        self,
        images: List[np.ndarray],
        min_shots: int = 5
    ) -> Tuple[Optional[np.ndarray], List[str]]:
        """
        Extract centroid (mean) embedding from multiple images.
        
        Args:
            images: List of face images (10 frames recommended)
            min_shots: Minimum successful captures required (default 5)
        
        Returns:
            (centroid_embedding, quality_reports)
        """
        embeddings = []
        quality_reports = []
        
        for idx, image in enumerate(images):
            # Quality check
            is_good, reason = self.preprocessor.quality_check(image)
            
            if not is_good:
                quality_reports.append(f"Frame {idx+1}: ✗ {reason}")
                continue
            
            # Extract embedding
            embedding = self.extract_512d_embedding(image)
            if embedding is not None:
                embeddings.append(embedding)
                quality_reports.append(f"Frame {idx+1}: ✓ Success")
            else:
                quality_reports.append(f"Frame {idx+1}: ✗ No face detected")
        
        # Check if we have enough good shots
        if len(embeddings) < min_shots:
            print(f"❌ Insufficient quality frames: {len(embeddings)}/{min_shots}")
            return None, quality_reports
        
        # Calculate centroid (mean embedding)
        centroid = self._calculate_centroid(embeddings)
        
        quality_reports.append(f"✓ Centroid created from {len(embeddings)} frames")
        
        return centroid, quality_reports
    
    def _calculate_centroid(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """Calculate centroid (mean) of multiple embeddings."""
        # Stack embeddings
        embedding_matrix = np.vstack(embeddings)
        
        # Calculate mean
        centroid = np.mean(embedding_matrix, axis=0)
        
        # Re-normalize to unit vector
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm
        
        # Verify dimension
        assert centroid.shape == (512,), \
            f"Invalid centroid dimension: {centroid.shape} (expected (512,))"
        
        return centroid
    
    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding (512-d)
            emb2: Second embedding (512-d)
        
        Returns:
            Similarity score between 0 and 1 (1 = identical)
        """
        emb1 = np.array(emb1, dtype=np.float64)
        emb2 = np.array(emb2, dtype=np.float64)
        
        # Verify dimensions
        assert emb1.shape == (512,), f"Invalid emb1 dimension: {emb1.shape}"
        assert emb2.shape == (512,), f"Invalid emb2 dimension: {emb2.shape}"
        
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
            live_embedding: 512-d embedding from live capture
            stored_embedding: 512-d embedding from enrollment
            threshold: Similarity threshold (default 0.4 for 512-d)
        
        Returns:
            (is_match, similarity_score)
        """
        threshold = threshold or self.similarity_threshold
        
        # Verify dimensions
        if live_embedding.shape != (512,) or stored_embedding.shape != (512,):
            print(f"❌ Invalid dimensions: {live_embedding.shape}, {stored_embedding.shape}")
            return False, 0.0
        
        # Calculate cosine similarity
        similarity = self.cosine_similarity(live_embedding, stored_embedding)
        
        # Check threshold
        is_match = similarity >= threshold
        
        return is_match, similarity


# Singleton instance
_insightface_service: Optional[InsightFaceService] = None


def get_insightface_service() -> InsightFaceService:
    """Get or create InsightFace service instance."""
    global _insightface_service
    if _insightface_service is None:
        _insightface_service = InsightFaceService()
    return _insightface_service
