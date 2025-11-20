import 'dart:io';
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
    tempDir = Directory.systemTemp.createTempSync('env_unit_test_');
  });

  tearDownAll(() async {
    // Clean up temp directory
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  group('Environment Service Unit Tests', () {
    test('brightness calculation with dark image', () async {
      // Create a dark image (low brightness)
      final width = 100;
      final height = 100;
      final image = img.Image(width: width, height: height);
      
      // Fill with dark pixels (value around 30)
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          image.setPixelRgba(x, y, 30, 30, 30, 255);
        }
      }
      
      final imageFile = File('${tempDir.path}/dark_image.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      final faceBoundingBox = ui.Rect.fromLTWH(10, 10, 50, 50);
      
      final result = await environmentService.analyzeEnvironment(
        imageFile,
        faceBoundingBox,
      );
      
      // Should be dark (< 60)
      expect(result.brightness, lessThan(60));
      expect(result.isTooDark, isTrue);
      expect(result.warnings, contains('Ảnh quá tối, vui lòng tăng ánh sáng'));
      
      await imageFile.delete();
    });

    test('brightness calculation with bright image', () async {
      // Create a bright image (high brightness)
      final width = 100;
      final height = 100;
      final image = img.Image(width: width, height: height);
      
      // Fill with bright pixels (value around 220)
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          image.setPixelRgba(x, y, 220, 220, 220, 255);
        }
      }
      
      final imageFile = File('${tempDir.path}/bright_image.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      final faceBoundingBox = ui.Rect.fromLTWH(10, 10, 50, 50);
      
      final result = await environmentService.analyzeEnvironment(
        imageFile,
        faceBoundingBox,
      );
      
      // Should be bright (> 200)
      expect(result.brightness, greaterThan(200));
      expect(result.isTooBright, isTrue);
      expect(result.warnings, contains('Ảnh quá sáng, vui lòng giảm ánh sáng'));
      
      await imageFile.delete();
    });

    test('brightness calculation with normal image', () async {
      // Create a normal brightness image
      final width = 100;
      final height = 100;
      final image = img.Image(width: width, height: height);
      
      // Fill with medium brightness pixels (value around 120)
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          image.setPixelRgba(x, y, 120, 120, 120, 255);
        }
      }
      
      final imageFile = File('${tempDir.path}/normal_image.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      final faceBoundingBox = ui.Rect.fromLTWH(10, 10, 50, 50);
      
      final result = await environmentService.analyzeEnvironment(
        imageFile,
        faceBoundingBox,
      );
      
      // Should be in acceptable range
      expect(result.brightness, greaterThanOrEqualTo(60));
      expect(result.brightness, lessThanOrEqualTo(200));
      expect(result.isTooDark, isFalse);
      expect(result.isTooBright, isFalse);
      
      await imageFile.delete();
    });

    test('blur score calculation with sharp image', () async {
      // Create a sharp image with clear edges
      final width = 100;
      final height = 100;
      final image = img.Image(width: width, height: height);
      
      // Create a checkerboard pattern (sharp edges)
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          final isBlack = (x ~/ 10 + y ~/ 10) % 2 == 0;
          final value = isBlack ? 0 : 255;
          image.setPixelRgba(x, y, value, value, value, 255);
        }
      }
      
      final imageFile = File('${tempDir.path}/sharp_image.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      final faceBoundingBox = ui.Rect.fromLTWH(10, 10, 50, 50);
      
      final result = await environmentService.analyzeEnvironment(
        imageFile,
        faceBoundingBox,
      );
      
      // Sharp image should have high blur score (> 100)
      expect(result.blurScore, greaterThan(100));
      expect(result.isTooBlurry, isFalse);
      
      await imageFile.delete();
    });

    test('blur score calculation with blurry image', () async {
      // Create a uniform image (no edges, very blurry)
      final width = 100;
      final height = 100;
      final image = img.Image(width: width, height: height);
      
      // Fill with uniform color (no variation = maximum blur)
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          image.setPixelRgba(x, y, 128, 128, 128, 255);
        }
      }
      
      final imageFile = File('${tempDir.path}/blurry_image.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      final faceBoundingBox = ui.Rect.fromLTWH(10, 10, 50, 50);
      
      final result = await environmentService.analyzeEnvironment(
        imageFile,
        faceBoundingBox,
      );
      
      // Uniform image should have very low blur score (< 100)
      expect(result.blurScore, lessThan(100));
      expect(result.isTooBlurry, isTrue);
      expect(result.warnings, contains('Ảnh bị mờ, vui lòng giữ máy chắc hơn'));
      
      await imageFile.delete();
    });

    test('face size ratio calculation with small face', () async {
      // Create a simple image
      final width = 200;
      final height = 200;
      final image = img.Image(width: width, height: height);
      
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          image.setPixelRgba(x, y, 128, 128, 128, 255);
        }
      }
      
      final imageFile = File('${tempDir.path}/small_face_image.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      // Small face (10x10 = 100 pixels out of 40000 = 0.0025 ratio)
      final faceBoundingBox = ui.Rect.fromLTWH(50, 50, 10, 10);
      
      final result = await environmentService.analyzeEnvironment(
        imageFile,
        faceBoundingBox,
      );
      
      // Face ratio should be small (< 0.10)
      expect(result.faceSizeRatio, lessThan(0.10));
      expect(result.isFaceTooSmall, isTrue);
      expect(result.warnings, contains('Khuôn mặt quá nhỏ, vui lòng đến gần hơn'));
      
      await imageFile.delete();
    });

    test('face size ratio calculation with large face', () async {
      // Create a simple image
      final width = 200;
      final height = 200;
      final image = img.Image(width: width, height: height);
      
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          image.setPixelRgba(x, y, 128, 128, 128, 255);
        }
      }
      
      final imageFile = File('${tempDir.path}/large_face_image.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      // Large face (100x100 = 10000 pixels out of 40000 = 0.25 ratio)
      final faceBoundingBox = ui.Rect.fromLTWH(50, 50, 100, 100);
      
      final result = await environmentService.analyzeEnvironment(
        imageFile,
        faceBoundingBox,
      );
      
      // Face ratio should be acceptable (>= 0.10)
      expect(result.faceSizeRatio, greaterThanOrEqualTo(0.10));
      expect(result.isFaceTooSmall, isFalse);
      
      await imageFile.delete();
    });

    test('warning generation for multiple issues', () async {
      // Create an image with multiple issues
      final width = 200;
      final height = 200;
      final image = img.Image(width: width, height: height);
      
      // Dark and uniform (blurry)
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          image.setPixelRgba(x, y, 30, 30, 30, 255);
        }
      }
      
      final imageFile = File('${tempDir.path}/multiple_issues_image.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      // Small face
      final faceBoundingBox = ui.Rect.fromLTWH(50, 50, 10, 10);
      
      final result = await environmentService.analyzeEnvironment(
        imageFile,
        faceBoundingBox,
      );
      
      // Should have multiple warnings
      expect(result.warnings.length, greaterThan(1));
      expect(result.hasWarnings, isTrue);
      expect(result.isAcceptable, isFalse);
      
      await imageFile.delete();
    });

    test('no warnings for good quality image', () async {
      // Create a good quality image
      final width = 200;
      final height = 200;
      final image = img.Image(width: width, height: height);
      
      // Create a pattern with good brightness and sharpness
      for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
          final isBlack = (x ~/ 20 + y ~/ 20) % 2 == 0;
          final value = isBlack ? 80 : 160; // Good brightness range
          image.setPixelRgba(x, y, value, value, value, 255);
        }
      }
      
      final imageFile = File('${tempDir.path}/good_quality_image.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      // Large enough face
      final faceBoundingBox = ui.Rect.fromLTWH(50, 50, 80, 80);
      
      final result = await environmentService.analyzeEnvironment(
        imageFile,
        faceBoundingBox,
      );
      
      // Should have no critical warnings
      expect(result.isTooDark, isFalse);
      expect(result.isTooBlurry, isFalse);
      expect(result.isFaceTooSmall, isFalse);
      expect(result.isAcceptable, isTrue);
      
      await imageFile.delete();
    });
  });
}
