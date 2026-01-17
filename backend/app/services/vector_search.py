"""
FAISS Vector Search for Fast Face Matching
Scales to 10,000+ students with <100ms search time
"""
import numpy as np
import faiss
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import pickle
import os


@dataclass
class SearchResult:
    """Result from vector search."""
    student_id: int
    student_name: str
    similarity: float
    distance: float


class VectorSearchEngine:
    """
    FAISS-based vector search for fast face matching.
    
    Features:
    - Sub-100ms search even with 10,000+ faces
    - Automatic index building and updating
    - Persistent storage
    """
    
    def __init__(self, dimension: int = 2622):  # Changed to 2622 for DeepFace VGG-Face
        self.dimension = dimension
        self.index: Optional[faiss.Index] = None
        self.student_map: Dict[int, Tuple[int, str]] = {}  # index_id -> (student_id, name)
        self.index_path = "faiss_index.bin"
        self.map_path = "student_map.pkl"
        
        # Initialize index
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index with optimal settings."""
        # Use IndexFlatIP for cosine similarity (Inner Product after L2 normalization)
        # This is fastest for <10k vectors
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # For larger datasets (>10k), use IVF index:
        # quantizer = faiss.IndexFlatIP(self.dimension)
        # self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
    
    def add_embedding(
        self,
        student_id: int,
        student_name: str,
        embedding: np.ndarray
    ):
        """
        Add a student embedding to the index.
        
        Args:
            student_id: Unique student ID
            student_name: Student name
            embedding: Face embedding (must be L2 normalized)
        """
        # Ensure embedding is normalized
        embedding = self._normalize(embedding)
        
        # Reshape for FAISS (needs 2D array)
        embedding_2d = embedding.reshape(1, -1).astype('float32')
        
        # Add to index
        index_id = self.index.ntotal
        self.index.add(embedding_2d)
        
        # Store mapping
        self.student_map[index_id] = (student_id, student_name)
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5
    ) -> List[SearchResult]:
        """
        Search for k most similar faces.
        
        Args:
            query_embedding: Query face embedding
            k: Number of results to return
        
        Returns:
            List of SearchResult ordered by similarity (highest first)
        """
        if self.index.ntotal == 0:
            return []
        
        # Normalize query
        query_embedding = self._normalize(query_embedding)
        query_2d = query_embedding.reshape(1, -1).astype('float32')
        
        # Search (returns distances and indices)
        # For IndexFlatIP, distance is actually dot product (higher = more similar)
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_2d, k)
        
        # Convert to results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            
            student_id, student_name = self.student_map.get(idx, (None, None))
            if student_id is None:
                continue
            
            # Convert dot product to similarity [0, 1]
            # Since vectors are normalized, dot product is cosine similarity
            similarity = float((dist + 1) / 2)  # Convert from [-1, 1] to [0, 1]
            
            results.append(SearchResult(
                student_id=student_id,
                student_name=student_name,
                similarity=similarity,
                distance=float(dist)
            ))
        
        return results
    
    def find_best_match(
        self,
        query_embedding: np.ndarray,
        threshold: float = 0.60
    ) -> Optional[SearchResult]:
        """
        Find single best match above threshold.
        
        Args:
            query_embedding: Query face embedding
            threshold: Minimum similarity threshold
        
        Returns:
            Best match or None if no match above threshold
        """
        results = self.search(query_embedding, k=1)
        
        if not results:
            return None
        
        best = results[0]
        if best.similarity >= threshold:
            return best
        
        return None
    
    def check_duplicate(
        self,
        embedding: np.ndarray,
        threshold: float = 0.90
    ) -> Tuple[bool, Optional[SearchResult]]:
        """
        Check if embedding is duplicate of existing student.
        
        Args:
            embedding: New student embedding
            threshold: Duplicate detection threshold (default 0.90)
        
        Returns:
            (is_duplicate, duplicate_info)
        """
        result = self.find_best_match(embedding, threshold)
        
        if result:
            return True, result
        
        return False, None
    
    def remove_student(self, student_id: int):
        """
        Remove student from index.
        Note: FAISS doesn't support deletion, so we rebuild index.
        """
        # Collect all embeddings except the one to remove
        embeddings_to_keep = []
        students_to_keep = []
        
        for idx in range(self.index.ntotal):
            sid, sname = self.student_map.get(idx, (None, None))
            if sid and sid != student_id:
                # Get embedding from index
                embedding = self.index.reconstruct(idx)
                embeddings_to_keep.append(embedding)
                students_to_keep.append((sid, sname))
        
        # Rebuild index
        self._initialize_index()
        self.student_map.clear()
        
        for (sid, sname), embedding in zip(students_to_keep, embeddings_to_keep):
            self.add_embedding(sid, sname, embedding)
    
    def save(self):
        """Save index and mappings to disk."""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save student mapping
            with open(self.map_path, 'wb') as f:
                pickle.dump(self.student_map, f)
            
            print(f"✓ Vector index saved ({self.index.ntotal} students)")
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def load(self):
        """Load index and mappings from disk."""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.map_path):
                # Load FAISS index
                self.index = faiss.read_index(self.index_path)
                
                # Load student mapping
                with open(self.map_path, 'rb') as f:
                    self.student_map = pickle.load(f)
                
                print(f"✓ Vector index loaded ({self.index.ntotal} students)")
                return True
        except Exception as e:
            print(f"Error loading index: {e}")
        
        return False
    
    def rebuild_from_database(self, students: List[Tuple[int, str, np.ndarray]]):
        """
        Rebuild entire index from database.
        Use this on startup or after major changes.
        
        Args:
            students: List of (student_id, name, embedding) tuples
        """
        self._initialize_index()
        self.student_map.clear()
        
        for student_id, name, embedding in students:
            self.add_embedding(student_id, name, embedding)
        
        print(f"✓ Index rebuilt with {len(students)} students")
    
    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            "total_students": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__ if self.index else None
        }
    
    @staticmethod
    def _normalize(embedding: np.ndarray) -> np.ndarray:
        """L2 normalize embedding."""
        embedding = np.array(embedding, dtype=np.float32)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding


# Singleton instance
_vector_search: Optional[VectorSearchEngine] = None


def get_vector_search() -> VectorSearchEngine:
    """Get or create vector search engine instance."""
    global _vector_search
    if _vector_search is None:
        _vector_search = VectorSearchEngine()
        # Try to load existing index
        _vector_search.load()
    return _vector_search
