# Testing Guide for Mobile Face Recognition App

## Overview

This guide provides comprehensive instructions for testing the complete face recognition workflow on a real Android device.

## Prerequisites

### Required Hardware
- Android device (Android 7.0 or higher recommended)
- USB cable for device connection
- Good lighting conditions for testing

### Required Software
- Flutter SDK installed
- Android Studio (for device drivers)
- USB debugging enabled on device

## Setup

### 1. Enable USB Debugging on Android Device

1. Go to **Settings** → **About Phone**
2. Tap **Build Number** 7 times to enable Developer Options
3. Go to **Settings** → **Developer Options**
4. Enable **USB Debugging**
5. Connect device via USB and accept the debugging prompt

### 2. Verify Device Connection

```bash
flutter devices
```

You should see your device listed. Note the device ID (e.g., `ABC123456789`).

### 3. Build and Install the App

```bash
cd mobile
flutter run -d <device_id>
```

Or build an APK:

```bash
flutter build apk --release
```

Then install the APK on your device.

## Manual Testing Workflow

### Phase 1: Collection Workflow Testing

#### Test 1.1: Camera Access and Preview
**Requirements**: 1.1, 1.2, 10.1

1. Open the app
2. Navigate to **Thu thập** (Collection) tab
3. **Verify**: Camera preview displays correctly
4. **Verify**: Real-time video feed is visible
5. **Verify**: Camera permission was requested and granted

**Expected Result**: ✓ Camera preview shows live feed

#### Test 1.2: Single Image Capture
**Requirements**: 1.3, 1.4, 2.1, 2.4

1. Position your face in the camera preview
2. Tap the capture button
3. **Verify**: Image is captured
4. **Verify**: Face detection runs automatically
5. **Verify**: Bounding box appears around detected face
6. **Verify**: Image counter increments

**Expected Result**: ✓ Image saved, counter shows 1

#### Test 1.3: Face Detection Validation
**Requirements**: 2.2, 2.3

**Test Case A: No Face**
1. Point camera at a wall or object without faces
2. Tap capture
3. **Verify**: Error message "Không phát hiện khuôn mặt"

**Test Case B: Multiple Faces**
1. Point camera at multiple people
2. Tap capture
3. **Verify**: Error message "Phát hiện nhiều khuôn mặt, vui lòng chỉ một người"

**Expected Result**: ✓ Appropriate error messages displayed

#### Test 1.4: Environment Quality Checks
**Requirements**: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8

**Test Case A: Too Dark**
1. Cover camera or test in very dark room
2. Capture image
3. **Verify**: Warning "Ảnh quá tối, vui lòng tăng ánh sáng"

**Test Case B: Too Bright**
1. Point camera directly at bright light
2. Capture image
3. **Verify**: Warning "Ảnh quá sáng, vui lòng giảm ánh sáng"

**Test Case C: Too Blurry**
1. Move camera rapidly while capturing
2. **Verify**: Warning "Ảnh bị mờ, vui lòng giữ máy chắc hơn"

**Test Case D: Face Too Small**
1. Stand far from camera
2. Capture image
3. **Verify**: Warning "Khuôn mặt quá nhỏ, vui lòng đến gần hơn"

**Expected Result**: ✓ Appropriate warnings displayed for each condition

#### Test 1.5: Multiple Image Collection
**Requirements**: 4.1, 4.2, 4.3, 4.4

1. Capture 5-10 images with slight variations:
   - Different angles (left, right, center)
   - Different expressions (neutral, smile)
   - Different distances (near, far)
2. **Verify**: Counter increments for each image
3. **Verify**: All images saved with timestamp format `user_YYYYMMDD_HHMMSS.jpg`

**Expected Result**: ✓ Counter shows correct number (5-10)

#### Test 1.6: Delete All Images
**Requirements**: 4.5

1. After collecting images, tap "Xóa tất cả" button
2. Confirm deletion
3. **Verify**: Counter resets to 0
4. **Verify**: All training images deleted

**Expected Result**: ✓ Counter shows 0

### Phase 2: Training Workflow Testing

#### Test 2.1: Training Without Images
**Requirements**: 6.2

1. Ensure no training images exist (delete all if needed)
2. Navigate to **Huấn luyện** (Training) tab
3. Tap "Huấn luyện" button
4. **Verify**: Error message "Chưa có dữ liệu, vui lòng thu thập ảnh trước"

**Expected Result**: ✓ Appropriate error message displayed

#### Test 2.2: Successful Training
**Requirements**: 6.1, 6.3, 6.4, 6.5, 6.6, 6.7

1. Collect 5-10 training images (see Phase 1)
2. Navigate to **Huấn luyện** tab
3. **Verify**: Display shows correct number of images
4. Tap "Huấn luyện" button
5. **Verify**: Loading indicator appears
6. **Verify**: Training completes within reasonable time (< 30 seconds)
7. **Verify**: Success message shows number of images and embeddings
8. **Verify**: Model status changes to "Đã huấn luyện"

**Expected Result**: ✓ Training successful, model ready for verification

#### Test 2.3: Retraining
**Requirements**: 6.1, 6.4, 6.5

1. After initial training, collect 2-3 more images
2. Tap "Huấn luyện" button again
3. **Verify**: Training completes with updated image count
4. **Verify**: Model status remains "Đã huấn luyện"

**Expected Result**: ✓ Retraining successful with new images

### Phase 3: Verification Workflow Testing

#### Test 3.1: Verification Without Training
**Requirements**: 7.2

1. Delete all training images and ensure no model trained
2. Navigate to **Nhận diện** (Verification) tab
3. Tap "Nhận diện" button
4. **Verify**: Error message "Chưa huấn luyện mô hình, vui lòng huấn luyện trước"

**Expected Result**: ✓ Appropriate error message displayed

#### Test 3.2: Threshold Configuration
**Requirements**: 8.1, 8.2, 8.3, 8.4, 8.5

1. Navigate to **Nhận diện** tab
2. **Verify**: Threshold slider visible (range 0.3 - 1.0)
3. Adjust slider to different values
4. **Verify**: Current value displays next to slider
5. Close and reopen app
6. **Verify**: Threshold value persists

**Expected Result**: ✓ Threshold configurable and persistent

#### Test 3.3: Successful Match Verification
**Requirements**: 7.1, 7.3, 7.4, 7.5, 7.7, 7.8

1. Ensure model is trained with your face
2. Set threshold to 0.6
3. Position your face in camera
4. Tap "Nhận diện" button
5. **Verify**: Face detected and bounding box drawn
6. **Verify**: Result shows "Khớp ✓" in green
7. **Verify**: Distance value displayed
8. **Verify**: Distance <= threshold
9. **Verify**: Bounding box is green

**Expected Result**: ✓ Successful match with green indicator

#### Test 3.4: Failed Match Verification
**Requirements**: 7.6, 7.8

1. Have someone else's face in camera (or use a photo)
2. Tap "Nhận diện" button
3. **Verify**: Result shows "Không khớp ✗" in red
4. **Verify**: Distance > threshold
5. **Verify**: Bounding box is red

**Expected Result**: ✓ Failed match with red indicator

#### Test 3.5: Threshold Sensitivity
**Requirements**: 7.5, 7.6, 8.1

1. Verify with your face at threshold 0.3 (strict)
2. **Verify**: Result and distance
3. Change threshold to 1.0 (lenient)
4. Verify again
5. **Verify**: Result may change based on distance
6. Test with different threshold values

**Expected Result**: ✓ Threshold affects match decision correctly

### Phase 4: Complete End-to-End Workflow

#### Test 4.1: Full Workflow (Collect → Train → Verify)
**Requirements**: All requirements

1. **Collection Phase**:
   - Delete all existing data
   - Collect 7-10 images of your face
   - Verify counter shows correct count
   - Test with different angles and lighting

2. **Training Phase**:
   - Navigate to Training tab
   - Verify image count displayed
   - Train model
   - Verify success message
   - Verify model status "Đã huấn luyện"

3. **Verification Phase**:
   - Navigate to Verification tab
   - Set threshold to 0.6
   - Verify your face → should match
   - Have someone else verify → should not match
   - Test with different lighting conditions
   - Test with different angles

**Expected Result**: ✓ Complete workflow successful

### Phase 5: Error Handling and Edge Cases

#### Test 5.1: Permission Handling
**Requirements**: 10.1, 10.2, 10.3, 10.4, 10.5

1. Uninstall and reinstall app
2. Open app
3. **Verify**: Camera permission requested
4. Deny permission
5. **Verify**: Appropriate error message
6. **Verify**: Link to settings provided
7. Grant permission from settings
8. **Verify**: App works correctly

**Expected Result**: ✓ Permissions handled gracefully

#### Test 5.2: Storage Full Scenario
**Requirements**: 12.3

1. Fill device storage (if possible)
2. Attempt to save training image
3. **Verify**: Appropriate error message

**Expected Result**: ✓ Storage error handled gracefully

#### Test 5.3: App Lifecycle
**Requirements**: 12.5

1. Start collection workflow
2. Press home button (background app)
3. Return to app
4. **Verify**: App state preserved
5. Complete workflow

**Expected Result**: ✓ App state preserved across lifecycle events

#### Test 5.4: Camera Resource Management
**Requirements**: 11.5

1. Open app on Collection tab
2. Switch to Training tab
3. **Verify**: Camera released
4. Switch back to Collection tab
5. **Verify**: Camera reinitializes

**Expected Result**: ✓ Camera resources managed correctly

### Phase 6: Performance Testing

#### Test 6.1: Model Loading Performance
**Requirements**: 11.1

1. Close app completely
2. Open app
3. Navigate to Collection tab
4. **Verify**: App loads within 3 seconds
5. **Verify**: Camera preview starts quickly

**Expected Result**: ✓ Fast app startup

#### Test 6.2: Embedding Extraction Performance
**Requirements**: 11.3

1. Capture an image
2. **Verify**: Face detection completes within 1 second
3. **Verify**: Environment check completes quickly
4. **Verify**: No noticeable lag

**Expected Result**: ✓ Fast image processing

#### Test 6.3: Training Performance
**Requirements**: 11.4

1. Collect 10 training images
2. Start training
3. **Verify**: Training completes within 15 seconds
4. **Verify**: UI remains responsive

**Expected Result**: ✓ Reasonable training time

#### Test 6.4: Verification Performance
**Requirements**: 11.3

1. Perform verification
2. **Verify**: Result displayed within 2 seconds
3. **Verify**: UI remains responsive

**Expected Result**: ✓ Fast verification

### Phase 7: UI/UX Testing

#### Test 7.1: Navigation
**Requirements**: 9.1

1. Test bottom navigation between all 3 tabs
2. **Verify**: Smooth transitions
3. **Verify**: Tab states preserved

**Expected Result**: ✓ Smooth navigation

#### Test 7.2: Loading Indicators
**Requirements**: 9.5

1. Perform operations that take time (training, verification)
2. **Verify**: Loading indicators displayed
3. **Verify**: Buttons disabled during processing

**Expected Result**: ✓ Clear loading states

#### Test 7.3: Error Messages
**Requirements**: 9.6, 12.1, 12.2, 12.4

1. Trigger various error conditions
2. **Verify**: Error messages are clear and in Vietnamese
3. **Verify**: Messages provide actionable guidance

**Expected Result**: ✓ User-friendly error messages

#### Test 7.4: Warning Display
**Requirements**: 9.7

1. Capture images with quality issues
2. **Verify**: Warnings displayed with icons
3. **Verify**: Multiple warnings can be shown
4. **Verify**: Warnings are clear and helpful

**Expected Result**: ✓ Clear warning display

## Automated Integration Tests

For automated testing, run the integration test suite on a connected device:

```bash
# Run all integration tests
flutter test integration_test/ -d <device_id>

# Run specific test suites
flutter test integration_test/e2e_workflow_integration_test.dart -d <device_id>
flutter test integration_test/embedding_property_integration_test.dart -d <device_id>
flutter test integration_test/training_property_integration_test.dart -d <device_id>
```

See `integration_test/README.md` for detailed information about automated tests.

## Test Scenarios with Different Conditions

### Lighting Conditions
- ✓ Bright indoor lighting
- ✓ Dim indoor lighting
- ✓ Outdoor daylight
- ✓ Backlit conditions
- ✓ Direct sunlight

### Face Angles
- ✓ Front-facing (0°)
- ✓ Slight left turn (15-30°)
- ✓ Slight right turn (15-30°)
- ✓ Looking up slightly
- ✓ Looking down slightly

### Distances
- ✓ Close (30-50 cm)
- ✓ Medium (50-100 cm)
- ✓ Far (100-150 cm)

### Expressions
- ✓ Neutral
- ✓ Smiling
- ✓ Serious
- ✓ With glasses
- ✓ Without glasses

## Troubleshooting

### Camera Not Working
- Check camera permissions in device settings
- Restart the app
- Check if other apps can use camera

### Face Detection Fails
- Ensure good lighting
- Position face clearly in frame
- Remove obstructions (hands, hair)
- Try different angles

### Training Fails
- Ensure at least 1 training image exists
- Check device storage space
- Restart app and try again

### Verification Always Fails
- Ensure model is trained
- Try adjusting threshold
- Collect more training images
- Ensure good lighting during verification

### App Crashes
- Check device logs: `flutter logs`
- Ensure device meets minimum requirements
- Try reinstalling the app

## Test Checklist

Use this checklist to track testing progress:

### Collection
- [ ] Camera preview works
- [ ] Image capture works
- [ ] Face detection works
- [ ] No face error handled
- [ ] Multiple faces error handled
- [ ] Environment warnings work
- [ ] Image counter accurate
- [ ] Delete all works

### Training
- [ ] No images error handled
- [ ] Training succeeds
- [ ] Model status updates
- [ ] Retraining works

### Verification
- [ ] No model error handled
- [ ] Threshold configurable
- [ ] Threshold persists
- [ ] Match detection works
- [ ] No match detection works
- [ ] Results display correctly

### Performance
- [ ] App loads quickly
- [ ] Processing is fast
- [ ] UI remains responsive
- [ ] No memory leaks

### Error Handling
- [ ] Permissions handled
- [ ] Errors display clearly
- [ ] App doesn't crash
- [ ] State preserved

## Reporting Issues

When reporting issues, include:
1. Device model and Android version
2. Steps to reproduce
3. Expected vs actual behavior
4. Screenshots or screen recordings
5. Relevant log output

## Success Criteria

The app is ready for release when:
- ✓ All manual tests pass
- ✓ All integration tests pass
- ✓ No critical bugs
- ✓ Performance is acceptable
- ✓ UI is responsive and smooth
- ✓ Error messages are clear
- ✓ Complete workflow works end-to-end
