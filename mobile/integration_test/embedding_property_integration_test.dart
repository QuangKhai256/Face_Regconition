import 'dart:io';
import 'dart:math';
import 'dart:ui' as ui;
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:faceid_mobile/services/embedding_service.dart';
import 'package:image/image.dart' as img;

// Feature: mobile-embedded-backend, Property 8: Embedding extraction success
// Feature: mobile-embedded-backend, Property 9: Embedding dimension consistency
// Validates: Requirements 5.3, 5.4

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  late EmbeddingService embeddingService;
  late Directory tempDir;

  setUp(() async {
    embeddingService = EmbeddingService();
    
    // Create a temporary directory for test images
    tempDir = await Directory.systemTemp.createTemp('embedding_test_');
    
    // Load the model
    await embeddingService.loadModel();
  });

  tearDown(() async {
    // Clean up
    await embeddingService.dispose();
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  group('Property 8: Embedding extraction success', () {
    testWidgets('should successfully extract embedding from any valid face image - iteration test', (WidgetTester tester) async {
      // Run multiple iterations to test the property
      const iterations = 100;
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Generate a random test image with a face-like region
        // Create an image with random dimensions
        final width = 200 + random.nextInt(600); // 200-800 pixels
        final height = 200 + random.nextInt(600); // 200-800 pixels
        
        final image = img.Image(width: width, height: height);
        
        // Fill with random pixel values to simulate a face image
        for (int y = 0; y < height; y++) {
          for (int x = 0; x < width; x++) {
            final r = random.nextInt(256);
            final g = random.nextInt(256);
            final b = random.nextInt(256);
            image.setPixelRgba(x, y, r, g, b, 255);
          }
        }
        
        // Save the test image
        final testImageFile = File('${tempDir.path}/test_face_$i.jpg');
        await testImageFile.writeAsBytes(img.encodeJpg(image));
        
        // Create a random face bounding box within the image
        final faceWidth = 50 + random.nextInt(width - 100);
        final faceHeight = 50 + random.nextInt(height - 100);
        final faceLeft = random.nextInt(width - faceWidth);
        final faceTop = random.nextInt(height - faceHeight);
        
        final faceBox = ui.Rect.fromLTWH(
          faceLeft.toDouble(),
          faceTop.toDouble(),
          faceWidth.toDouble(),
          faceHeight.toDouble(),
        );
        
        // Property: Extraction should succeed and return non-null embedding
        List<double>? embedding;
        try {
          embedding = await embeddingService.extractEmbedding(testImageFile, faceBox);
        } catch (e) {
          fail('Iteration $i: Embedding extraction should not throw exception: $e');
        }
        
        expect(embedding, isNotNull,
            reason: 'Iteration $i: Embedding should not be null');
        expect(embedding, isNotEmpty,
            reason: 'Iteration $i: Embedding should not be empty');
        
        // Clean up
        await testImageFile.delete();
      }
    });
  });

  group('Property 9: Embedding dimension consistency', () {
    testWidgets('should always return 128-dimensional embedding - iteration test', (WidgetTester tester) async {
      // Run multiple iterations to test the property
      const iterations = 100;
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Generate a random test image
        final width = 200 + random.nextInt(600);
        final height = 200 + random.nextInt(600);
        
        final image = img.Image(width: width, height: height);
        
        // Fill with random pixel values
        for (int y = 0; y < height; y++) {
          for (int x = 0; x < width; x++) {
            final r = random.nextInt(256);
            final g = random.nextInt(256);
            final b = random.nextInt(256);
            image.setPixelRgba(x, y, r, g, b, 255);
          }
        }
        
        // Save the test image
        final testImageFile = File('${tempDir.path}/test_dim_$i.jpg');
        await testImageFile.writeAsBytes(img.encodeJpg(image));
        
        // Create a random face bounding box
        final faceWidth = 50 + random.nextInt(width - 100);
        final faceHeight = 50 + random.nextInt(height - 100);
        final faceLeft = random.nextInt(width - faceWidth);
        final faceTop = random.nextInt(height - faceHeight);
        
        final faceBox = ui.Rect.fromLTWH(
          faceLeft.toDouble(),
          faceTop.toDouble(),
          faceWidth.toDouble(),
          faceHeight.toDouble(),
        );
        
        // Extract embedding
        final embedding = await embeddingService.extractEmbedding(testImageFile, faceBox);
        
        // Property: Embedding dimension should always be exactly 128
        expect(embedding.length, equals(128),
            reason: 'Iteration $i: Embedding dimension should be exactly 128');
        
        // Additional property: All values should be finite numbers
        for (int j = 0; j < embedding.length; j++) {
          expect(embedding[j].isFinite, isTrue,
              reason: 'Iteration $i: Embedding value at index $j should be finite');
        }
        
        // Clean up
        await testImageFile.delete();
      }
    });
    
    testWidgets('should return L2 normalized embeddings - iteration test', (WidgetTester tester) async {
      // Run multiple iterations to test L2 normalization property
      const iterations = 50;
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Generate a test image
        final width = 300;
        final height = 300;
        
        final image = img.Image(width: width, height: height);
        
        // Fill with random pixel values
        for (int y = 0; y < height; y++) {
          for (int x = 0; x < width; x++) {
            final r = random.nextInt(256);
            final g = random.nextInt(256);
            final b = random.nextInt(256);
            image.setPixelRgba(x, y, r, g, b, 255);
          }
        }
        
        // Save the test image
        final testImageFile = File('${tempDir.path}/test_norm_$i.jpg');
        await testImageFile.writeAsBytes(img.encodeJpg(image));
        
        // Create a face bounding box
        final faceBox = ui.Rect.fromLTWH(50, 50, 200, 200);
        
        // Extract embedding
        final embedding = await embeddingService.extractEmbedding(testImageFile, faceBox);
        
        // Property: L2 norm should be approximately 1.0 (unit vector)
        double sumSquares = 0.0;
        for (final value in embedding) {
          sumSquares += value * value;
        }
        final norm = sqrt(sumSquares);
        
        expect(norm, closeTo(1.0, 1e-6),
            reason: 'Iteration $i: L2 norm should be approximately 1.0 (normalized)');
        
        // Clean up
        await testImageFile.delete();
      }
    });
  });
}
