# Implementation Plan

- [x] 1. Setup project structure and dependencies









  - Add required Flutter packages to pubspec.yaml (camera, google_mlkit_face_detection, tflite_flutter, path_provider, shared_preferences, image, permission_handler)
  - Download MobileFaceNet TFLite model and add to assets/models/
  - Configure Android permissions in AndroidManifest.xml
  - Configure iOS permissions in Info.plist
  - Create directory structure: lib/services/, lib/screens/, lib/models/, lib/utils/
  - _Requirements: All requirements depend on this setup_

- [x] 2. Implement Storage Service





  - Create StorageService class with methods for managing directories and files
  - Implement getTrainingImagesDir() to get app documents directory
  - Implement saveTrainingImage() with timestamp filename format
  - Implement loadTrainingImages() to read all training images
  - Implement deleteAllTrainingImages() for cleanup
  - Implement saveMeanEmbedding() and loadMeanEmbedding() using JSON file
  - Implement saveThreshold() and loadThreshold() using SharedPreferences
  - _Requirements: 4.1, 4.2, 6.5, 8.3_

- [x] 2.1 Write property test for storage round trips


  - **Property 1: Image save/load round trip**
  - **Property 12: Mean embedding persistence round trip**
  - **Property 17: Threshold persistence round trip**
  - **Validates: Requirements 1.5, 6.5, 8.3**

- [x] 2.2 Write property test for filename format


  - **Property 6: Training image filename format**
  - **Validates: Requirements 4.2**

- [x] 2.3 Write property test for image counter


  - **Property 7: Image counter consistency**
  - **Validates: Requirements 4.3**

- [x] 3. Implement Camera Service





  - Create CameraService class to manage camera controller
  - Implement initialize() to setup camera with appropriate resolution
  - Implement captureImage() to capture frame from camera
  - Implement dispose() to release camera resources
  - Add error handling for camera permission denied and camera not available
  - _Requirements: 1.1, 1.3, 10.1_

- [x] 3.1 Write unit tests for camera service


  - Test camera initialization
  - Test image capture
  - Test resource cleanup
  - _Requirements: 1.1, 1.3_

- [x] 4. Implement Face Detection Service using ML Kit





  - Create FaceDetectionService class
  - Implement detectFaces() using ML Kit Face Detection
  - Implement detectSingleFace() that validates exactly one face
  - Implement getFaceBoundingBox() to extract face coordinates
  - Add error handling for no face and multiple faces cases
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 4.1 Write property test for face detection


  - **Property 2: Face detection returns result**
  - **Property 3: Single face bounding box validity**
  - **Validates: Requirements 2.1, 2.4**

- [x] 4.2 Write unit tests for face detection edge cases


  - Test with image containing no faces
  - Test with image containing multiple faces
  - Test with image containing exactly one face
  - _Requirements: 2.2, 2.3, 2.4_

- [x] 5. Implement Environment Check Service





  - Create EnvironmentService class
  - Implement analyzeEnvironment() that takes image and face box
  - Implement _calculateBrightness() using grayscale mean
  - Implement _calculateBlurScore() using Laplacian variance
  - Implement _calculateFaceSizeRatio() from face box and image size
  - Generate warnings based on thresholds (brightness < 60 or > 200, blur < 100, face ratio < 0.10)
  - Return EnvironmentInfo with all metrics and warnings
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 5.1 Write property test for environment metrics


  - **Property 4: Environment metrics calculation**
  - **Property 5: Environment threshold consistency**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**

- [x] 5.2 Write unit tests for environment calculations


  - Test brightness calculation with known images
  - Test blur score calculation with sharp and blurry images
  - Test face size ratio calculation
  - Test warning generation for each threshold
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 6. Implement Embedding Service with TensorFlow Lite





  - Create EmbeddingService class
  - Implement loadModel() to load MobileFaceNet TFLite model from assets
  - Implement _preprocessImage() to resize face to 112x112 and normalize
  - Implement _runInference() to run TFLite model and get 128-d embedding
  - Implement extractEmbedding() that takes image file and face box
  - Add L2 normalization to embedding output
  - Implement dispose() to release model resources
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 6.1 Write property test for embedding extraction





  - **Property 8: Embedding extraction success**
  - **Property 9: Embedding dimension consistency**
  - **Validates: Requirements 5.3, 5.4**

- [x] 6.2 Write unit tests for embedding service


  - Test model loading
  - Test image preprocessing
  - Test embedding dimension (128)
  - Test L2 normalization
  - _Requirements: 5.3, 5.4_

- [x] 7. Implement Training Service








  - Create TrainingService class
  - Implement trainModel() that orchestrates training workflow
  - Implement _loadTrainingImages() using StorageService
  - Extract embeddings from all valid training images
  - Implement _calculateMeanEmbedding() to compute mean across all embeddings
  - Implement _saveMeanEmbedding() using StorageService
  - Return TrainingResult with num_images and num_embeddings
  - Handle case when no training images exist
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.7_

- [x] 7.1 Write property test for training



  - **Property 10: Training reads all images**
  - **Property 11: Mean embedding calculation**
  - **Property 13: Model trained status**
  - **Validates: Requirements 6.1, 6.3, 6.4, 6.7**

- [x] 7.2 Write unit tests for training service


  - Test with no training images
  - Test with valid training images
  - Test mean calculation correctness
  - Test model status after training
  - _Requirements: 6.2, 6.4, 6.7_

- [x] 8. Implement Verification Service





  - Create VerificationService class
  - Implement loadMeanEmbedding() using StorageService
  - Implement verify() that takes image file, face box, and threshold
  - Implement _calculateEuclideanDistance() between two embeddings
  - Compare distance with threshold to determine isMatch
  - Return VerificationResult with isMatch, distance, threshold, message
  - Handle case when model not trained
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 8.1 Write property test for verification


  - **Property 14: Euclidean distance calculation**
  - **Property 15: Threshold comparison consistency**
  - **Validates: Requirements 7.4, 7.5, 7.6**

- [x] 8.2 Write unit tests for verification service


  - Test with model not trained
  - Test distance calculation
  - Test threshold comparison (match and no match cases)
  - _Requirements: 7.2, 7.4, 7.5, 7.6_

- [x] 9. Implement threshold management





  - Add threshold validation to ensure range [0.3, 1.0]
  - Integrate threshold save/load in VerificationScreen
  - Set default threshold to 0.6
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 9.1 Write property test for threshold


  - **Property 16: Threshold range validation**
  - **Validates: Requirements 8.2**

- [x] 10. Implement image resizing utility














  - Create ImageUtils class
  - Implement resizeImage() to resize images larger than 1920x1080
  - Maintain aspect ratio during resize
  - _Requirements: 11.2_

- [x] 10.1 Write property test for image resize




  - **Property 18: Image resize constraint**
  - **Validates: Requirements 11.2**

- [x] 11. Create data models




  - Create FaceDetectionResult model
  - Create EnvironmentInfo model with all metrics and warnings
  - Create TrainingResult model
  - Create VerificationResult model
  - Add toJson/fromJson methods for serialization
  - _Requirements: All requirements use these models_

- [x] 12. Implement Collection Screen UI











  - Create CollectionScreen widget with camera preview
  - Add camera initialization in initState
  - Add capture button that calls CameraService.captureImage()
  - After capture, call FaceDetectionService.detectSingleFace()
  - If single face detected, call EnvironmentService.analyzeEnvironment()
  - If environment acceptable, call StorageService.saveTrainingImage()
  - Display image counter showing total training images
  - Display environment warnings if any
  - Add delete all button that calls StorageService.deleteAllTrainingImages()
  - Handle all error cases with user-friendly messages
  - _Requirements: 1.1, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 3.8, 4.1, 4.3, 4.4, 4.5, 9.2_

- [ ] 13. Implement Training Screen UI
  - Create TrainingScreen widget
  - Display current number of training images
  - Display model trained status
  - Add train button that calls TrainingService.trainModel()
  - Show loading indicator during training
  - Display training result (num_images, num_embeddings)
  - Handle error case when no training images exist
  - Update model status after successful training
  - _Requirements: 6.1, 6.2, 6.6, 6.7, 9.3_

- [ ] 14. Implement Verification Screen UI
  - Create VerificationScreen widget with camera preview
  - Add threshold slider (0.3 to 1.0) with current value display
  - Save threshold changes to SharedPreferences
  - Add verify button that captures image
  - Call FaceDetectionService.detectSingleFace()
  - Call EnvironmentService.analyzeEnvironment()
  - Call VerificationService.verify() with threshold
  - Display result: "Khớp ✓" (green) or "Không khớp ✗" (red)
  - Display distance, threshold, and environment warnings
  - Draw bounding box on image with color based on result
  - Handle error case when model not trained
  - _Requirements: 7.1, 7.2, 7.5, 7.6, 7.7, 7.8, 8.1, 8.2, 8.3, 8.5, 9.4_

- [ ] 15. Implement main app structure
  - Create main.dart with MaterialApp
  - Implement bottom navigation with 3 tabs: Thu thập, Huấn luyện, Nhận diện
  - Add navigation between screens
  - Configure app theme
  - _Requirements: 9.1_

- [ ] 16. Implement permission handling
  - Request camera permission on app start
  - Request storage permission if needed (Android < 10)
  - Show permission rationale dialogs
  - Handle permission denied cases
  - Provide link to app settings if permission permanently denied
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 17. Add loading indicators and error handling
  - Add CircularProgressIndicator for all async operations
  - Disable buttons during processing
  - Show SnackBar or Dialog for errors
  - Display environment warnings with icon
  - Add try-catch blocks for all service calls
  - _Requirements: 9.5, 9.6, 9.7, 12.1, 12.2, 12.3, 12.4_

- [ ] 18. Optimize performance
  - Cache TFLite model in memory after first load
  - Resize images before processing
  - Release camera when switching tabs
  - Dispose services properly in dispose() methods
  - _Requirements: 11.1, 11.2, 11.5_

- [ ] 19. Final testing and polish
  - Test complete workflow: collect → train → verify
  - Test on real Android device
  - Test camera functionality
  - Test with different lighting conditions
  - Test with different face angles
  - Verify all error messages are clear
  - Verify UI is responsive and smooth
  - _Requirements: All requirements_

- [ ] 19.1 Write integration tests
  - Test end-to-end collection workflow
  - Test end-to-end training workflow
  - Test end-to-end verification workflow
  - Test error scenarios
  - _Requirements: All requirements_

- [ ] 20. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
