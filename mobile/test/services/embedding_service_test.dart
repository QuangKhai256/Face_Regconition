import 'dart:io';
import 'dart:math';
import 'dart:ui' as ui;
import 'package:flutter_test/flutter_test.dart';
import 'package:faceid_mobile/services/embedding_service.dart';
import 'package:image/image.dart' as img;

/// Unit tests for EmbeddingService
/// Tests model loading, preprocessing, embedding extraction, and L2 normalization
/// Requirements: 5.3, 5.4
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  
  late EmbeddingService embeddingService;
  late Directory tempDir;

  setUp(() async {
    embeddingService = EmbeddingService();
    tempDir = await Directory.systemTemp.createTemp('embedding_unit_test_');
  });

  tearDown(() async {
    await embeddingService.dispose();
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  group('Model Loading', () {
    test('should successfully load model from assets', () async {
      // Act
      await embeddingService.loadModel();
      
      // Assert
      expect(embeddingService.isModelLoaded, isTrue);
    });

    test('should not reload model if already loaded', () async {
      // Arrange
      await embeddingService.loadModel();
      expect(embeddingService.isModelLoaded, isTrue);
      
      // Act - load again
      await embeddingService.loadModel();
      
      // Assert - should still be loaded
      expect(embeddingService.isModelLoaded, isTrue);
    });

    test('should throw exception when extracting embedding without loading model', () async {
      // Arrange - don't load model
      final testImage = img.Image(width: 200, height: 200);
      final testImageFile = File('${tempDir.path}/test.jpg');
      await testImageFile.writeAsBytes(img.encodeJpg(testImage));
      final faceBox = ui.Rect.fromLTWH(50, 50, 100, 100);
      
      // Act & Assert
      expect(
        () => embeddingService.extractEmbedding(testImageFile, faceBox),
        throwsException,
      );
    });
  });

  group('Image Preprocessing', () {
    test('should handle various image sizes', () async {
      // Arrange
      await embeddingService.loadModel();
      
      final testSizes = [
        (100, 100),
        (200, 300),
        (500, 400),
        (1000, 800),
      ];
      
      for (final (width, height) in testSizes) {
        // Create test image
        final image = img.Image(width: width, height: height);
        for (int y = 0; y < height; y++) {
          for (int x = 0; x < width; x++) {
            image.setPixelRgba(x, y, 128, 128, 128, 255);
          }
        }
        
        final testImageFile = File('${tempDir.path}/test_${width}x$height.jpg');
        await testImageFile.writeAsBytes(img.encodeJpg(image));
        
        // Create face box
        final faceBox = ui.Rect.fromLTWH(
          10,
          10,
          (width - 20).toDouble(),
          (height - 20).toDouble(),
        );
        
        // Act
        final embedding = await embeddingService.extractEmbedding(testImageFile, faceBox);
        
        // Assert - should successfully extract embedding
        expect(embedding, isNotNull);
        expect(embedding.length, equals(128));
        
        // Clean up
        await testImageFile.delete();
      }
    });

    test('should handle face boxes at image boundaries', () async {
      // Arrange
      await embeddingService.loadModel();
      
      final image = img.Image(width: 300, height: 300);
      for (int y = 0; y < 300; y++) {
        for (int x = 0; x < 300; x++) {
          image.setPixelRgba(x, y, 100, 150, 200, 255);
        }
      }
      
      final testImageFile = File('${tempDir.path}/test_boundary.jpg');
      await testImageFile.writeAsBytes(img.encodeJpg(image));
      
      // Test face box at top-left corner
      final faceBox1 = ui.Rect.fromLTWH(0, 0, 100, 100);
      final embedding1 = await embeddingService.extractEmbedding(testImageFile, faceBox1);
      expect(embedding1.length, equals(128));
      
      // Test face box at bottom-right corner
      final faceBox2 = ui.Rect.fromLTWH(200, 200, 100, 100);
      final embedding2 = await embeddingService.extractEmbedding(testImageFile, faceBox2);
      expect(embedding2.length, equals(128));
      
      // Clean up
      await testImageFile.delete();
    });
  });

  group('Embedding Extraction', () {
    test('should extract 128-dimensional embedding', () async {
      // Arrange
      await embeddingService.loadModel();
      
      final image = img.Image(width: 400, height: 400);
      for (int y = 0; y < 400; y++) {
        for (int x = 0; x < 400; x++) {
          image.setPixelRgba(x, y, 150, 150, 150, 255);
        }
      }
      
      final testImageFile = File('${tempDir.path}/test_extract.jpg');
      await testImageFile.writeAsBytes(img.encodeJpg(image));
      final faceBox = ui.Rect.fromLTWH(100, 100, 200, 200);
      
      // Act
      final embedding = await embeddingService.extractEmbedding(testImageFile, faceBox);
      
      // Assert
      expect(embedding, isNotNull);
      expect(embedding.length, equals(128),
          reason: 'Embedding should have exactly 128 dimensions');
      
      // All values should be finite
      for (int i = 0; i < embedding.length; i++) {
        expect(embedding[i].isFinite, isTrue,
            reason: 'Embedding value at index $i should be finite');
      }
    });

    test('should produce different embeddings for different images', () async {
      // Arrange
      await embeddingService.loadModel();
      
      // Create two different images
      final image1 = img.Image(width: 300, height: 300);
      for (int y = 0; y < 300; y++) {
        for (int x = 0; x < 300; x++) {
          image1.setPixelRgba(x, y, 100, 100, 100, 255);
        }
      }
      
      final image2 = img.Image(width: 300, height: 300);
      for (int y = 0; y < 300; y++) {
        for (int x = 0; x < 300; x++) {
          image2.setPixelRgba(x, y, 200, 200, 200, 255);
        }
      }
      
      final testImageFile1 = File('${tempDir.path}/test1.jpg');
      await testImageFile1.writeAsBytes(img.encodeJpg(image1));
      
      final testImageFile2 = File('${tempDir.path}/test2.jpg');
      await testImageFile2.writeAsBytes(img.encodeJpg(image2));
      
      final faceBox = ui.Rect.fromLTWH(50, 50, 200, 200);
      
      // Act
      final embedding1 = await embeddingService.extractEmbedding(testImageFile1, faceBox);
      final embedding2 = await embeddingService.extractEmbedding(testImageFile2, faceBox);
      
      // Assert - embeddings should be different
      bool areDifferent = false;
      for (int i = 0; i < 128; i++) {
        if ((embedding1[i] - embedding2[i]).abs() > 1e-6) {
          areDifferent = true;
          break;
        }
      }
      
      expect(areDifferent, isTrue,
          reason: 'Different images should produce different embeddings');
    });
  });

  group('L2 Normalization', () {
    test('should produce unit-length embeddings', () async {
      // Arrange
      await embeddingService.loadModel();
      
      final image = img.Image(width: 300, height: 300);
      for (int y = 0; y < 300; y++) {
        for (int x = 0; x < 300; x++) {
          image.setPixelRgba(x, y, 128, 128, 128, 255);
        }
      }
      
      final testImageFile = File('${tempDir.path}/test_norm.jpg');
      await testImageFile.writeAsBytes(img.encodeJpg(image));
      final faceBox = ui.Rect.fromLTWH(50, 50, 200, 200);
      
      // Act
      final embedding = await embeddingService.extractEmbedding(testImageFile, faceBox);
      
      // Calculate L2 norm
      double sumSquares = 0.0;
      for (final value in embedding) {
        sumSquares += value * value;
      }
      final norm = sqrt(sumSquares);
      
      // Assert - norm should be approximately 1.0
      expect(norm, closeTo(1.0, 1e-6),
          reason: 'L2 normalized embedding should have unit length');
    });

    test('should maintain L2 normalization across multiple extractions', () async {
      // Arrange
      await embeddingService.loadModel();
      
      for (int i = 0; i < 10; i++) {
        final image = img.Image(width: 300, height: 300);
        for (int y = 0; y < 300; y++) {
          for (int x = 0; x < 300; x++) {
            // Vary the pixel values
            final value = 50 + i * 20;
            image.setPixelRgba(x, y, value, value, value, 255);
          }
        }
        
        final testImageFile = File('${tempDir.path}/test_norm_$i.jpg');
        await testImageFile.writeAsBytes(img.encodeJpg(image));
        final faceBox = ui.Rect.fromLTWH(50, 50, 200, 200);
        
        // Act
        final embedding = await embeddingService.extractEmbedding(testImageFile, faceBox);
        
        // Calculate L2 norm
        double sumSquares = 0.0;
        for (final value in embedding) {
          sumSquares += value * value;
        }
        final norm = sqrt(sumSquares);
        
        // Assert
        expect(norm, closeTo(1.0, 1e-6),
            reason: 'Iteration $i: L2 norm should be approximately 1.0');
        
        // Clean up
        await testImageFile.delete();
      }
    });
  });

  group('Resource Management', () {
    test('should properly dispose resources', () async {
      // Arrange
      await embeddingService.loadModel();
      expect(embeddingService.isModelLoaded, isTrue);
      
      // Act
      await embeddingService.dispose();
      
      // Assert
      expect(embeddingService.isModelLoaded, isFalse);
    });

    test('should handle multiple dispose calls', () async {
      // Arrange
      await embeddingService.loadModel();
      
      // Act - dispose multiple times
      await embeddingService.dispose();
      await embeddingService.dispose();
      
      // Assert - should not throw
      expect(embeddingService.isModelLoaded, isFalse);
    });
  });
}
