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

3. Run the integration test:
```bash
flutter test integration_test/embedding_property_integration_test.dart -d <device_id>
```

Example:
```bash
flutter test integration_test/embedding_property_integration_test.dart -d emulator-5554
```

### Run on Physical Device

1. Connect your device via USB and enable USB debugging

2. Verify device is connected:
```bash
flutter devices
```

3. Run the integration test:
```bash
flutter test integration_test/embedding_property_integration_test.dart -d <device_id>
```

## Why Integration Tests?

TensorFlow Lite requires native libraries (`libtensorflowlite_c`) that are only available when running on actual mobile devices or emulators. Regular unit tests run in the Flutter VM on the host machine (Windows/Mac/Linux) and cannot load these native libraries.

The unit test version at `test/property/embedding_property_test.dart` will automatically skip on desktop platforms and direct you to run these integration tests instead.

## Test Coverage

### Property 8: Embedding Extraction Success
- Validates that embedding extraction succeeds for any valid face image
- Runs 100 iterations with randomly generated test images
- **Validates Requirements**: 5.3

### Property 9: Embedding Dimension Consistency
- Validates that embeddings always have exactly 128 dimensions
- Validates that all embedding values are finite numbers
- Validates that embeddings are L2 normalized (unit length)
- Runs 100-150 iterations with randomly generated test images
- **Validates Requirements**: 5.4

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
