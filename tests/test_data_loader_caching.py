"""
Property-based tests for data loader caching behavior.
"""

import os
import shutil
import time
from unittest.mock import patch, MagicMock
import pytest
from hypothesis import given, strategies as st, settings

from backend.data_loader import load_known_face_encodings, get_known_faces_cache


class TestDataLoaderCaching:
    """Property-based tests for caching behavior."""
    
    @pytest.fixture
    def temp_myface_dir(self):
        """Create a temporary myface directory for testing."""
        # Save original myface if it exists
        original_exists = os.path.exists("myface")
        if original_exists:
            shutil.move("myface", "myface_backup")
        
        # Create temp directory with a dummy file
        os.makedirs("myface", exist_ok=True)
        
        yield "myface"
        
        # Cleanup
        if os.path.exists("myface"):
            shutil.rmtree("myface")
        
        # Restore original
        if original_exists:
            shutil.move("myface_backup", "myface")
    
    @settings(max_examples=10, deadline=None)
    @given(num_calls=st.integers(min_value=2, max_value=10))
    def test_property_face_embeddings_cached(self, temp_myface_dir, num_calls):
        """
        **Feature: face-recognition-backend, Property 2: Face embeddings are cached**
        **Validates: Requirements 1.4, 9.1, 9.2**
        
        For any sequence of calls to get training data, after the first call loads
        the data, all subsequent calls should return the cached data without
        reloading from disk.
        """
        # Clear cache before test
        get_known_faces_cache.cache_clear()
        
        # Mock load_known_face_encodings to track calls
        with patch('backend.data_loader.load_known_face_encodings') as mock_load:
            # Setup mock return value
            mock_encodings = [MagicMock()]
            mock_files = ['test.jpg']
            mock_load.return_value = (mock_encodings, mock_files)
            
            # Call get_known_faces_cache multiple times
            results = []
            for i in range(num_calls):
                result = get_known_faces_cache()
                results.append(result)
            
            # Verify load_known_face_encodings was called only once (first call)
            assert mock_load.call_count == 1, \
                f"Expected load_known_face_encodings to be called once, but was called {mock_load.call_count} times"
            
            # Verify all calls returned the same cached result
            for i in range(1, num_calls):
                assert results[i] is results[0], \
                    f"Call {i} did not return cached result (different object)"
    
    def test_cache_returns_same_object(self, temp_myface_dir):
        """
        Test that cache returns the exact same object (not a copy).
        **Validates: Requirements 9.1, 9.2**
        """
        # Clear cache
        get_known_faces_cache.cache_clear()
        
        with patch('backend.data_loader.load_known_face_encodings') as mock_load:
            mock_encodings = [MagicMock()]
            mock_files = ['test.jpg']
            mock_load.return_value = (mock_encodings, mock_files)
            
            # First call
            result1 = get_known_faces_cache()
            
            # Second call
            result2 = get_known_faces_cache()
            
            # Should be the exact same object (identity check)
            assert result1 is result2, "Cache should return the same object instance"
            assert id(result1) == id(result2), "Cache should return the same object ID"
    
    def test_cache_improves_performance(self, temp_myface_dir):
        """
        Test that caching improves performance by avoiding disk I/O.
        **Validates: Requirements 9.1, 9.2, 9.3**
        """
        # Clear cache
        get_known_faces_cache.cache_clear()
        
        with patch('backend.data_loader.load_known_face_encodings') as mock_load:
            # Simulate slow disk I/O
            def slow_load():
                time.sleep(0.1)  # 100ms delay
                return ([MagicMock()], ['test.jpg'])
            
            mock_load.side_effect = slow_load
            
            # First call - should be slow
            start1 = time.time()
            get_known_faces_cache()
            duration1 = time.time() - start1
            
            # Second call - should be fast (cached)
            start2 = time.time()
            get_known_faces_cache()
            duration2 = time.time() - start2
            
            # Cached call should be significantly faster
            assert duration2 < duration1 / 2, \
                f"Cached call ({duration2:.4f}s) should be much faster than first call ({duration1:.4f}s)"
