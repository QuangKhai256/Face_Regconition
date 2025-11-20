import 'dart:io';
import 'dart:math';
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:faceid_mobile/utils/image_utils.dart';

// Feature: mobile-embedded-backend, Property 18: Image resize constraint
// Validates: Requirements 11.2

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  
  late Directory tempDir;

  setUp(() async {
    // Create a temporary directory for testing
    tempDir = await Directory.systemTemp.createTemp('image_resize_test_');
  });

  tearDown(() async {
    // Clean up temp directory with retry logic for Windows file locking
    if (await tempDir.exists()) {
      try {
        await tempDir.delete(recursive: true);
      } catch (e) {
        // On Windows, files might be locked briefly, wait and retry
        await Future.delayed(Duration(milliseconds: 100));
        try {
          await tempDir.delete(recursive: true);
        } catch (e) {
          // If still fails, just log it - temp files will be cleaned up eventually
          print('Warning: Could not delete temp directory: $e');
        }
      }
    }
  });

  group('Property 18: Image resize constraint', () {
    test('should constrain images larger than 1920x1080 while maintaining aspect ratio - iteration test', () async {
      // Run multiple iterations to test the property
      const iterations = 30; // Reduced for performance
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Generate random dimensions that exceed at least one constraint
        // Ensure at least one dimension is larger than the max
        final exceedsWidth = random.nextBool();
        final exceedsHeight = random.nextBool() || !exceedsWidth; // At least one must exceed
        
        final originalWidth = exceedsWidth 
            ? 1921 + random.nextInt(300) // 1921 to 2220 (smaller range for speed)
            : 100 + random.nextInt(1821);  // 100 to 1920
            
        final originalHeight = exceedsHeight
            ? 1081 + random.nextInt(300) // 1081 to 1380 (smaller range for speed)
            : 100 + random.nextInt(981);   // 100 to 1080
        
        // Create a test image with the generated dimensions
        final testImage = img.Image(width: originalWidth, height: originalHeight);
        
        // Fill with a solid color (much faster than random per-pixel)
        final r = random.nextInt(256);
        final g = random.nextInt(256);
        final b = random.nextInt(256);
        img.fill(testImage, color: img.ColorRgb8(r, g, b));
        
        // Save the test image to a file
        final testImageFile = File('${tempDir.path}/test_image_$i.jpg');
        await testImageFile.writeAsBytes(img.encodeJpg(testImage, quality: 85));
        
        // Get original dimensions for verification
        final originalDimensions = await ImageUtils.getImageDimensions(testImageFile);
        expect(originalDimensions.width, equals(originalWidth));
        expect(originalDimensions.height, equals(originalHeight));
        
        // Resize the image
        final resizedFile = await ImageUtils.resizeImage(testImageFile);
        
        // Get resized dimensions
        final resizedDimensions = await ImageUtils.getImageDimensions(resizedFile);
        
        // Property 1: Both dimensions should be <= their respective maximums
        expect(resizedDimensions.width, lessThanOrEqualTo(ImageUtils.maxWidth),
            reason: 'Iteration $i: Width should be <= ${ImageUtils.maxWidth}, got ${resizedDimensions.width}');
        expect(resizedDimensions.height, lessThanOrEqualTo(ImageUtils.maxHeight),
            reason: 'Iteration $i: Height should be <= ${ImageUtils.maxHeight}, got ${resizedDimensions.height}');
        
        // Property 2: Aspect ratio should be maintained (within rounding tolerance)
        final originalAspectRatio = originalWidth / originalHeight;
        final resizedAspectRatio = resizedDimensions.width / resizedDimensions.height;
        
        // Use a relative tolerance based on the aspect ratio magnitude
        // For very wide/tall images, absolute differences can be larger
        final tolerance = max(0.02, originalAspectRatio * 0.002);
        
        expect(resizedAspectRatio, closeTo(originalAspectRatio, tolerance),
            reason: 'Iteration $i: Aspect ratio should be maintained. '
                'Original: $originalAspectRatio, Resized: $resizedAspectRatio');
        
        // Property 3: At least one dimension should be at its maximum
        // (unless the original was already smaller)
        if (originalWidth > ImageUtils.maxWidth || originalHeight > ImageUtils.maxHeight) {
          final atMaxWidth = resizedDimensions.width == ImageUtils.maxWidth;
          final atMaxHeight = resizedDimensions.height == ImageUtils.maxHeight;
          
          expect(atMaxWidth || atMaxHeight, isTrue,
              reason: 'Iteration $i: At least one dimension should be at maximum. '
                  'Width: ${resizedDimensions.width}/${ImageUtils.maxWidth}, '
                  'Height: ${resizedDimensions.height}/${ImageUtils.maxHeight}');
        }
        
        // Clean up immediately after each iteration
        try {
          if (await testImageFile.exists()) {
            await testImageFile.delete();
          }
        } catch (e) {
          // Ignore cleanup errors
        }
      }
    }, timeout: Timeout(Duration(seconds: 60)));
    
    test('should not resize images already within constraints - iteration test', () async {
      // Run multiple iterations to test the property
      const iterations = 20; // Reduced for performance
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Generate random dimensions within constraints
        final originalWidth = 100 + random.nextInt(1821);  // 100 to 1920
        final originalHeight = 100 + random.nextInt(981);  // 100 to 1080
        
        // Create a test image with the generated dimensions
        final testImage = img.Image(width: originalWidth, height: originalHeight);
        
        // Fill with a solid color (much faster)
        final r = random.nextInt(256);
        final g = random.nextInt(256);
        final b = random.nextInt(256);
        img.fill(testImage, color: img.ColorRgb8(r, g, b));
        
        // Save the test image to a file
        final testImageFile = File('${tempDir.path}/test_small_image_$i.jpg');
        final originalBytes = img.encodeJpg(testImage, quality: 85);
        await testImageFile.writeAsBytes(originalBytes);
        
        // Resize the image (should return original)
        final resizedFile = await ImageUtils.resizeImage(testImageFile);
        
        // Property: Should return the same file
        expect(resizedFile.path, equals(testImageFile.path),
            reason: 'Iteration $i: Should return the same file path');
        
        // Get resized dimensions
        final resizedDimensions = await ImageUtils.getImageDimensions(resizedFile);
        
        // Property: Dimensions should remain unchanged
        expect(resizedDimensions.width, equals(originalWidth),
            reason: 'Iteration $i: Width should remain unchanged');
        expect(resizedDimensions.height, equals(originalHeight),
            reason: 'Iteration $i: Height should remain unchanged');
        
        // Clean up immediately after each iteration
        try {
          if (await testImageFile.exists()) {
            await testImageFile.delete();
          }
        } catch (e) {
          // Ignore cleanup errors
        }
      }
    }, timeout: Timeout(Duration(seconds: 45)));
    
    test('should handle edge case: exactly at maximum dimensions', () async {
      // Test image exactly at 1920x1080
      final testImage = img.Image(width: 1920, height: 1080);
      
      // Fill with a solid color
      img.fill(testImage, color: img.ColorRgb8(128, 128, 128));
      
      final testImageFile = File('${tempDir.path}/test_exact_size.jpg');
      await testImageFile.writeAsBytes(img.encodeJpg(testImage));
      
      // Resize (should not change)
      final resizedFile = await ImageUtils.resizeImage(testImageFile);
      final resizedDimensions = await ImageUtils.getImageDimensions(resizedFile);
      
      // Property: Should remain at exactly 1920x1080
      expect(resizedDimensions.width, equals(1920));
      expect(resizedDimensions.height, equals(1080));
      
      await testImageFile.delete();
    });
    
    test('should handle edge case: one dimension at max, other below', () async {
      final random = Random();
      
      // Test 1: Width at max, height below
      final testImage1 = img.Image(width: 1920, height: 500);
      img.fill(testImage1, color: img.ColorRgb8(100, 100, 100));
      
      final testImageFile1 = File('${tempDir.path}/test_width_max.jpg');
      await testImageFile1.writeAsBytes(img.encodeJpg(testImage1));
      
      final resizedFile1 = await ImageUtils.resizeImage(testImageFile1);
      final resizedDimensions1 = await ImageUtils.getImageDimensions(resizedFile1);
      
      expect(resizedDimensions1.width, equals(1920));
      expect(resizedDimensions1.height, equals(500));
      
      await testImageFile1.delete();
      
      // Test 2: Height at max, width below
      final testImage2 = img.Image(width: 800, height: 1080);
      img.fill(testImage2, color: img.ColorRgb8(150, 150, 150));
      
      final testImageFile2 = File('${tempDir.path}/test_height_max.jpg');
      await testImageFile2.writeAsBytes(img.encodeJpg(testImage2));
      
      final resizedFile2 = await ImageUtils.resizeImage(testImageFile2);
      final resizedDimensions2 = await ImageUtils.getImageDimensions(resizedFile2);
      
      expect(resizedDimensions2.width, equals(800));
      expect(resizedDimensions2.height, equals(1080));
      
      await testImageFile2.delete();
    });
  });
}
