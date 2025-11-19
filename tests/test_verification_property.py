"""
Property-based tests for verification module.
Tests universal properties for model loading and embedding comparison.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings
import math

from backend.verification import compare_embeddings, load_trained_model


# Feature: face-recognition-complete, Property 12: Euclidean distance calculation
@given(
    embedding1=st.lists(
        st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        min_size=128,
        max_size=128
    ),
    embedding2=st.lists(
        st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        min_size=128,
        max_size=128
    ),
    threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_euclidean_distance_calculation(embedding1, embedding2, threshold):
    """
    Property 12: Euclidean distance calculation
    
    For any two 128-d embeddings, the calculated distance should equal 
    the square root of the sum of squared differences between corresponding dimensions.
    
    Validates: Requirements 3.5
    """
    # Convert to numpy arrays
    emb1 = np.array(embedding1, dtype=np.float64)
    emb2 = np.array(embedding2, dtype=np.float64)
    
    # Call the function
    is_match, distance = compare_embeddings(emb1, emb2, threshold)
    
    # Calculate expected distance manually
    # distance = sqrt(sum((emb1[i] - emb2[i])^2))
    squared_diffs = [(emb1[i] - emb2[i]) ** 2 for i in range(128)]
    expected_distance = math.sqrt(sum(squared_diffs))
    
    # Verify the distance matches (within floating point precision)
    assert abs(distance - expected_distance) < 1e-6, (
        f"Distance calculation incorrect: got {distance}, expected {expected_distance}"
    )



# Feature: face-recognition-complete, Property 13: Threshold comparison consistency
@given(
    embedding1=st.lists(
        st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        min_size=128,
        max_size=128
    ),
    embedding2=st.lists(
        st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        min_size=128,
        max_size=128
    ),
    threshold=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_threshold_comparison_consistency(embedding1, embedding2, threshold):
    """
    Property 13: Threshold comparison consistency
    
    For any calculated distance and threshold value, is_match should be true 
    if and only if distance <= threshold.
    
    Validates: Requirements 3.6, 3.7
    """
    # Convert to numpy arrays
    emb1 = np.array(embedding1, dtype=np.float64)
    emb2 = np.array(embedding2, dtype=np.float64)
    
    # Call the function
    is_match, distance = compare_embeddings(emb1, emb2, threshold)
    
    # Verify threshold comparison logic
    if distance <= threshold:
        assert is_match is True, (
            f"is_match should be True when distance ({distance}) <= threshold ({threshold})"
        )
    else:
        assert is_match is False, (
            f"is_match should be False when distance ({distance}) > threshold ({threshold})"
        )
