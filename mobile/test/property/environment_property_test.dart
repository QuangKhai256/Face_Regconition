import 'dart:io';
import 'dart:math';
import 'dart:ui' as ui;
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import '../../lib/services/environment_service.dart';

void main() {
  late EnvironmentService environmentService;
  late Directory tempDir;

  setUpAll(() async {
    TestWidgetsFlutterBinding.ensureInitialized();
    environmentService = EnvironmentService();
    
    // Create temp directory for test images in system temp
    tempDir = Directory.systemTemp.createTempSync('environment_test_');
  });

  tearDownAll(() async {
    // Clean up temp directory
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  group('Property Tests for Environment Service', () {
    // Feature: mobile-embedded-backend, Property 4: Environment metrics calculation
    // For any image with a detected face, brightness should be in range [0, 255],
    // blur score should be non-negative, and face size ratio should be in range [0.0, 1.0]
    test('Property 4: Environment metrics calculation - all metrics in valid ranges', () async {
      final random = Random(42);
      const iterations = 20; // Reduced for performance
      
      for (int i = 0; i < iterations; i++) {
        // Generate random image dimensions
        final width = 100 + random.nextInt(900); // 100-999
        final height = 100 + random.nextInt(900); // 100-999
        
        // Create random image
        final image = img.Image(width: width, height: height);
        
        // Fill with random pixels
        for (int y = 0; y < height; y++) {
          for (int x = 0; x < width; x++) {
            final r = random.nextInt(256);
            final g = random.nextInt(256);
            final b = random.nextInt(256);
            image.setPixelRgba(x, y, r, g, b, 255);
          }
        }
        
        // Save to temp file
        final imageFile = File('${tempDir.path}/test_image_$i.jpg');
        await imageFile.writeAsBytes(img.encodeJpg(image));
        
        // Generate random face bounding box within image bounds
        final faceWidth = 10 + random.nextInt(width - 20);
        final faceHeight = 10 + random.nextInt(height - 20);
        final faceLeft = random.nextInt(width - faceWidth);
        final faceTop = random.nextInt(height - faceHeight);
        
        final faceBoundingBox = ui.Rect.fromLTWH(
          faceLeft.toDouble(),
          faceTop.toDouble(),
          faceWidth.toDouble(),
          faceHeight.toDouble(),
        );
        
        // Analyze environment
        final result = await environmentService.analyzeEnvironment(
          imageFile,
          faceBoundingBox,
        );
        
        // Property 4: Check that all metrics are in valid ranges
        expect(
          result.brightness,
          inInclusiveRange(0.0, 255.0),
          reason: 'Brightness should be in range [0, 255] for iteration $i',
        );
        
        expect(
          result.blurScore,
          greaterThanOrEqualTo(0.0),
          reason: 'Blur score should be non-negative for iteration $i',
        );
        
        expect(
          result.faceSizeRatio,
          inInclusiveRange(0.0, 1.0),
          reason: 'Face size ratio should be in range [0.0, 1.0] for iteration $i',
        );
        
        // Clean up
        await imageFile.delete();
      }
    });

    // Feature: mobile-embedded-backend, Property 5: Environment threshold consistency
    // For any calculated environment metrics, the warning flags should be set correctly:
    // isTooDark iff brightness < 60, isTooBright iff brightness > 200,
    // isTooBlurry iff blurScore < 100, isFaceTooSmall iff faceSizeRatio < 0.10
    test('Property 5: Environment threshold consistency - warning flags match thresholds', () async {
      final random = Random(43);
      const iterations = 20; // Reduced for performance
      
      for (int i = 0; i < iterations; i++) {
        // Generate image with controlled brightness
        final width = 200;
        final height = 200;
        final image = img.Image(width: width, height: height);
        
        // Create image with specific brightness characteristics
        // We'll vary the pixel values to create different brightness levels
        final baseValue = random.nextInt(256);
        for (int y = 0; y < height; y++) {
          for (int x = 0; x < width; x++) {
            // Add some variation but keep around base value
            final variation = random.nextInt(20) - 10;
            final value = (baseValue + variation).clamp(0, 255);
            image.setPixelRgba(x, y, value, value, value, 255);
          }
        }
        
        // Save to temp file
        final imageFile = File('${tempDir.path}/threshold_test_$i.jpg');
        await imageFile.writeAsBytes(img.encodeJpg(image));
        
        // Generate face bounding box with varying sizes
        final faceWidthRatio = 0.05 + random.nextDouble() * 0.4; // 5% to 45%
        final faceHeightRatio = 0.05 + random.nextDouble() * 0.4;
        final faceWidth = (width * faceWidthRatio).toInt();
        final faceHeight = (height * faceHeightRatio).toInt();
        final faceLeft = random.nextInt(width - faceWidth);
        final faceTop = random.nextInt(height - faceHeight);
        
        final faceBoundingBox = ui.Rect.fromLTWH(
          faceLeft.toDouble(),
          faceTop.toDouble(),
          faceWidth.toDouble(),
          faceHeight.toDouble(),
        );
        
        // Analyze environment
        final result = await environmentService.analyzeEnvironment(
          imageFile,
          faceBoundingBox,
        );
        
        // Property 5: Check threshold consistency
        expect(
          result.isTooDark,
          equals(result.brightness < 60),
          reason: 'isTooDark should be true iff brightness < 60 (iteration $i: brightness=${result.brightness})',
        );
        
        expect(
          result.isTooBright,
          equals(result.brightness > 200),
          reason: 'isTooBright should be true iff brightness > 200 (iteration $i: brightness=${result.brightness})',
        );
        
        expect(
          result.isTooBlurry,
          equals(result.blurScore < 100),
          reason: 'isTooBlurry should be true iff blurScore < 100 (iteration $i: blurScore=${result.blurScore})',
        );
        
        expect(
          result.isFaceTooSmall,
          equals(result.faceSizeRatio < 0.10),
          reason: 'isFaceTooSmall should be true iff faceSizeRatio < 0.10 (iteration $i: ratio=${result.faceSizeRatio})',
        );
        
        // Verify warnings list consistency
        if (result.isTooDark) {
          expect(
            result.warnings,
            contains('Ảnh quá tối, vui lòng tăng ánh sáng'),
            reason: 'Warning should be present when isTooDark is true (iteration $i)',
          );
        }
        
        if (result.isTooBright) {
          expect(
            result.warnings,
            contains('Ảnh quá sáng, vui lòng giảm ánh sáng'),
            reason: 'Warning should be present when isTooBright is true (iteration $i)',
          );
        }
        
        if (result.isTooBlurry) {
          expect(
            result.warnings,
            contains('Ảnh bị mờ, vui lòng giữ máy chắc hơn'),
            reason: 'Warning should be present when isTooBlurry is true (iteration $i)',
          );
        }
        
        if (result.isFaceTooSmall) {
          expect(
            result.warnings,
            contains('Khuôn mặt quá nhỏ, vui lòng đến gần hơn'),
            reason: 'Warning should be present when isFaceTooSmall is true (iteration $i)',
          );
        }
        
        // Clean up
        await imageFile.delete();
      }
    });
  });
}
