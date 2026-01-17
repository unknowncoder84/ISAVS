"""
Advanced Matcher with Dynamic Thresholding
Handles cosine similarity, soft-matching, and deduplication
"""
import numpy as np
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class MatchResult:
    """Result of a face matching operation."""
    is_match: bool
    similarity: float
    confidence_level: str  # "high", "medium", "low", "soft"
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    requires_review: bool = False
    message: str = ""


class FaceMatcher:
    """
    Production-grade face matcher with:
    - Cosine similarity (better than Euclidean)
    - Dynamic thresholding
    - Soft-match logic with OTP validation
    - Deduplication detection
    """
    
    def __init__(
        self,
        strict_threshold: float = 0.70,  # High confidence match
        normal_threshold: float = 0.60,  # Standard match
        soft_threshold: float = 0.50,    # Soft match (requires OTP)
        duplicate_threshold: float = 0.90  # Deduplication threshold
    ):
        self.strict_threshold = strict_threshold
        self.normal_threshold = normal_threshold
        self.soft_threshold = soft_threshold
        self.duplicate_threshold = duplicate_threshold
    
    def match(
        self,
        query_embedding: np.ndarray,
        stored_embedding: np.ndarray,
        otp_verified: bool = False
    ) -> MatchResult:
        """
        Match query embedding against stored embedding.
        
        Args:
            query_embedding: Face embedding from verification
            stored_embedding: Stored embedding from enrollment
            otp_verified: Whether OTP was verified (enables soft-match)
        
        Returns:
            MatchResult with detailed matching information
        """
        # Calculate cosine similarity
        similarity = self.cosine_similarity(query_embedding, stored_embedding)
        
        # Determine match level
        if similarity >= self.strict_threshold:
            return MatchResult(
                is_match=True,
                similarity=similarity,
                confidence_level="high",
                requires_review=False,
                message=f"High confidence match ({similarity:.3f})"
            )
        
        elif similarity >= self.normal_threshold:
            return MatchResult(
                is_match=True,
                similarity=similarity,
                confidence_level="medium",
                requires_review=False,
                message=f"Standard match ({similarity:.3f})"
            )
        
        elif similarity >= self.soft_threshold and otp_verified:
            # Soft match: Face similarity is borderline but OTP is correct
            # Allow but flag for review
            return MatchResult(
                is_match=True,
                similarity=similarity,
                confidence_level="soft",
                requires_review=True,
                message=f"Soft match with OTP verification ({similarity:.3f}). Flagged for review."
            )
        
        else:
            return MatchResult(
                is_match=False,
                similarity=similarity,
                confidence_level="low",
                requires_review=False,
                message=f"No match ({similarity:.3f} below threshold)"
            )
    
    def find_best_match(
        self,
        query_embedding: np.ndarray,
        database_embeddings: List[Tuple[int, str, np.ndarray]],
        otp_verified: bool = False
    ) -> Optional[MatchResult]:
        """
        Find best match from database of embeddings.
        
        Args:
            query_embedding: Face embedding to match
            database_embeddings: List of (student_id, name, embedding) tuples
            otp_verified: Whether OTP was verified
        
        Returns:
            Best MatchResult or None if no match found
        """
        if not database_embeddings:
            return None
        
        best_match = None
        best_similarity = -1.0
        
        for student_id, name, stored_embedding in database_embeddings:
            similarity = self.cosine_similarity(query_embedding, stored_embedding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                match_result = self.match(query_embedding, stored_embedding, otp_verified)
                match_result.student_id = student_id
                match_result.student_name = name
                best_match = match_result
        
        return best_match if best_match and best_match.is_match else None
    
    def check_duplicate(
        self,
        new_embedding: np.ndarray,
        database_embeddings: List[Tuple[int, str, np.ndarray]]
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Check if new enrollment is a duplicate of existing student.
        
        Args:
            new_embedding: Embedding from new enrollment
            database_embeddings: Existing student embeddings
        
        Returns:
            (is_duplicate, duplicate_info)
        """
        for student_id, name, stored_embedding in database_embeddings:
            similarity = self.cosine_similarity(new_embedding, stored_embedding)
            
            if similarity >= self.duplicate_threshold:
                return True, {
                    "student_id": student_id,
                    "student_name": name,
                    "similarity": similarity,
                    "message": f"Identity already exists: {name} (similarity: {similarity:.3f})"
                }
        
        return False, None
    
    @staticmethod
    def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Cosine similarity is better than Euclidean distance because:
        - Invariant to magnitude (only cares about direction)
        - Range [0, 1] is easier to interpret
        - More robust to lighting variations
        
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
        
        # Clamp to [0, 1] range (handle floating point errors)
        # Convert from [-1, 1] to [0, 1]
        similarity = (similarity + 1) / 2
        similarity = float(np.clip(similarity, 0.0, 1.0))
        
        return similarity
    
    def adaptive_threshold(
        self,
        similarity: float,
        context: Dict
    ) -> Tuple[bool, str]:
        """
        Adaptive thresholding based on context.
        
        Context can include:
        - time_of_day: Lower threshold in poor lighting conditions
        - attempt_count: Slightly lower threshold after multiple failures
        - otp_verified: Enable soft-match
        """
        base_threshold = self.normal_threshold
        
        # Adjust for time of day (if provided)
        if "time_of_day" in context:
            hour = context["time_of_day"]
            if hour < 7 or hour > 19:  # Early morning or evening
                base_threshold -= 0.05
        
        # Adjust for multiple failed attempts
        if "attempt_count" in context and context["attempt_count"] > 2:
            base_threshold -= 0.03
        
        # Check if match
        is_match = similarity >= base_threshold
        reason = f"Adaptive threshold: {base_threshold:.2f} (similarity: {similarity:.2f})"
        
        return is_match, reason
    
    def calculate_confidence_score(self, similarity: float) -> int:
        """
        Convert similarity to confidence percentage (0-100).
        """
        # Map similarity [0.5, 1.0] to confidence [0, 100]
        if similarity < 0.5:
            return 0
        
        confidence = int((similarity - 0.5) * 200)
        return min(100, max(0, confidence))


# Singleton instance
_matcher: Optional[FaceMatcher] = None


def get_matcher() -> FaceMatcher:
    """Get or create matcher instance."""
    global _matcher
    if _matcher is None:
        # Get thresholds from settings
        normal_threshold = getattr(settings, 'FACE_SIMILARITY_THRESHOLD', 0.60)
        _matcher = FaceMatcher(
            strict_threshold=min(0.70, normal_threshold + 0.10),
            normal_threshold=normal_threshold,
            soft_threshold=max(0.50, normal_threshold - 0.10),
            duplicate_threshold=0.90
        )
    return _matcher
