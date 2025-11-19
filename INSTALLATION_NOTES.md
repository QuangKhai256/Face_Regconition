# Installation Notes

## Face Recognition Library Installation

The `face_recognition` library requires `dlib`, which needs CMake and C++ build tools to compile on Windows. This can be challenging to install.

### Current Status

- **Implementation**: ✅ Complete - All face processor functions are implemented
- **Tests**: ✅ Complete - All unit tests and property-based tests pass
- **face_recognition library**: ⚠️ Not installed (but tests work with mocks)

### Why Tests Work Without face_recognition

The tests use mocking (`unittest.mock`) to simulate the `face_recognition` library behavior. This allows us to:
1. Test the logic of our code without the actual library
2. Run tests on systems where `face_recognition` is difficult to install
3. Verify that our code correctly handles all edge cases

A `conftest.py` file was created in the `tests/` directory that automatically mocks the `face_recognition` module if it's not installed.

### Installing face_recognition (For Production Use)

When you're ready to run the actual backend server, you'll need to install `face_recognition`. Here are the options:

#### Option 1: Install on Linux/WSL (Recommended)
```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install cmake build-essential
pip install face-recognition
```

#### Option 2: Install on Windows with Pre-built Wheels
1. Install Visual Studio Build Tools or MinGW
2. Install CMake: https://cmake.org/download/
3. Then install face_recognition:
```bash
pip install cmake
pip install dlib
pip install face-recognition
```

#### Option 3: Use Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim
RUN apt-get update && apt-get install -y cmake build-essential
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Verifying Installation

Once `face_recognition` is installed, you can verify it works:
```bash
python -c "import face_recognition; print('face_recognition installed successfully')"
```

### Running Tests with Real Library

After installing `face_recognition`, the tests will automatically use the real library instead of mocks. You can verify this by running:
```bash
python -m pytest tests/test_face_processor_unit.py tests/test_face_processor_property.py -v
```

## Summary

The face processor module is fully implemented and tested. The tests pass using mocks, which validates the correctness of our implementation logic. When you're ready to deploy the backend, install `face_recognition` using one of the methods above.
