"""
Pytest configuration and fixtures.
"""

import sys
from unittest.mock import MagicMock

# Create mock for face_recognition module if it's not installed
# This allows tests to run even without the actual library
try:
    import face_recognition
except ModuleNotFoundError:
    # Create a mock module
    mock_face_recognition = MagicMock()
    sys.modules['face_recognition'] = mock_face_recognition
