# Integration Tests for TensorFlow Lite

## Overview

These integration tests validate TensorFlow Lite functionality that requires native libraries only available on mobile platforms (Android/iOS).

## Running Integration Tests

### Prerequisites
- An Android emulator running OR a physical Android/iOS device connected
- Flutter SDK installed

### Run on Android Emulator

1. Start your Android emulator:
```bash
flutter emulators --launch <emulator_name>
```

2. Verify device is connected:
```bash
flutter devices
```

3. Run the integration tests:
```bash
# Run all integration tests
flutter test integration_test/ -d <device_id>

# Or run specific test files
flutter test integration_test/embedding_property_integration_test.dart -d <device_id>
flutter test integration_test/training_property_integration_test.dart -d <device_id>
flutter test integration_test/e2e_workflow_integration_test.dart -d <device_id>
```

Example:
```bash
flutter test integration_test/e2e_workflow_integration_test.dart -d emulator-5554
```

### Run on Physical Device

1. Connect your device via USB and enable USB debugging

2. Verify device is connected:
```bash
flutter devices
```

3. Run the integration tests:
```bash
# Run all integration tests
flutter test integration_test/ -d <device_id>

# Or run specific test files
flutter test integration_test/e2e_workflow_integration_test.dart -d <device_id>
```

## Why Integration Tests?

TensorFlow Lite requires native libraries (`libtensorflowlite_c`) that are only available when running on actual mobile devices or emulators. Regular unit tests run in the Flutter VM on the host machine (Windows/Mac/Linux) and cannot load these native libraries.

The unit test version at `test/property/embedding_property_test.dart` will automatically skip on desktop platforms and direct you to run these integration tests instead.

## Test Coverage

### embedding_property_integration_test.dart

#### Property 8: Embedding Extraction Success
- Validates that embedding extraction succeeds for any valid face image
- Runs 100 iterations with randomly generated test images
- **Validates Requirements**: 5.3

#### Property 9: Embedding Dimension Consistency
- Validates that embeddings always have exactly 128 dimensions
- Validates that all embedding values are finite numbers
- Validates that embeddings are L2 normalized (unit length)
- Runs 100-150 iterations with randomly generated test images
- **Validates Requirements**: 5.4

### training_property_integration_test.dart

#### Property 10: Training Reads All Images
- Validates that training process reads all images in training directory
- Tests with varying numbers of training images (1-10)
- **Validates Requirements**: 6.1, 6.3

#### Property 11: Mean Embedding Calculation
- Validates correct arithmetic mean calculation of embeddings
- Tests dimension consistency of mean embeddings
- **Validates Requirements**: 6.4

#### Property 13: Model Trained Status
- Validates model is marked as trained after successful training
- Validates verification is enabled after training
- **Validates Requirements**: 6.7

### e2e_workflow_integration_test.dart

#### End-to-End Collection Workflow
- Tests complete image collection workflow
- Tests multiple image collection
- Tests delete all images functionality
- **Validates Requirements**: 1.1, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 3.8, 4.1, 4.3, 4.4, 4.5

#### End-to-End Training Workflow
- Tests complete training workflow from collection to model trained
- Tests training failure with no images
- Tests retraining with new images
- **Validates Requirements**: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7

#### End-to-End Verification Workflow
- Tests complete verification workflow
- Tests verification failure when model not trained
- Tests threshold changes and consistency
- **Validates Requirements**: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 8.1, 8.2, 8.3, 8.5

#### Complete Workflow (collect → train → verify)
- Tests full end-to-end workflow from collection through verification
- Validates all phases work together correctly
- **Validates Requirements**: All requirements

#### Error Scenario Tests
- Tests missing training images handling
- Tests verification without training
- Tests threshold persistence
- Tests environment warnings (dark images, small faces)
- **Validates Requirements**: 3.2, 3.3, 3.7, 6.2, 7.2, 8.3, 12.1, 12.2, 12.3, 12.4

## Expected Results

All tests should pass when run on a mobile device or emulator with the MobileFaceNet TFLite model properly loaded.

## Troubleshooting

### "Failed to load model" Error
- Ensure `assets/models/mobilefacenet.tflite` exists
- Verify the model file is listed in `pubspec.yaml` under `flutter: assets:`
- Run `flutter pub get` to ensure assets are properly bundled

### Test Timeout
- Integration tests may take longer than unit tests (2-5 minutes)
- Increase timeout if needed: `--timeout=5m`

### Device Not Found
- Ensure emulator is running or device is connected
- Check `flutter devices` output
- Try `flutter doctor` to diagnose connection issues
