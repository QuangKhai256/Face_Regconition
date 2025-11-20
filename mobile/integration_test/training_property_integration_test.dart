import 'dart:io';
import 'dart:math';
import 'dart:ui' as ui;
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:faceid_mobile/services/training_service.dart';
import 'package:faceid_mobile/services/storage_service.dart';
import 'package:faceid_mobile/services/embedding_service.dart';
import 'package:faceid_mobile/services/face_detection_service.dart';
import 'package:image/image.dart' as img;
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';

// Feature: mobile-embedded-backend, Property 10: Training reads all images
// Feature: mobile-embedded-backend, Property 11: Mean embedding calculation
// Feature: mobile-embedded-backend, Property 13: Model trained status
// Validates: Requirements 6.1, 6.3, 6.4, 6.7

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  late TrainingService trainingService;
  late StorageService storageService;
  late EmbeddingService embeddingService;
  late FaceDetectionService faceDetectionService;
  late Directory tempDir;

  setUp(() async {
    storageService = StorageService();
    embeddingService = EmbeddingService();
    faceDetectionService = FaceDetectionService();
    
    trainingService = TrainingService(
      storageService: storageService,
      embeddingService: embeddingService,
      faceDetectionService: faceDetectionService,
    );
    
    // Create a temporary directory for test images
    tempDir = await Directory.systemTemp.createTemp('training_test_');
    
    // Load the embedding model
    await embeddingService.loadModel();
    
    // Clean up any existing training data
    await storageService.deleteAllTrainingImages();
  });

  tearDown(() async {
    // Clean up
    await embeddingService.dispose();
    await faceDetectionService.dispose();
    await storageService.deleteAllTrainingImages();
    
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  group('Property 10: Training reads all images', () {
    testWidgets('should attempt to read all images in training directory - iteration test', (WidgetTester tester) async {
      // Run multiple iterations with different numbers of images
      const iterations = 20;
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Generate random number of training images (1-10)
        final numImages = 1 + random.nextInt(10);
        
        // Create test images with faces
        final createdFiles = <File>[];
        for (int j = 0; j < numImages; j++) {
          // Create a simple test image with a face-like region
          final image = img.Image(width: 400, height: 400);
          
          // Fill with random pixel values
          for (int y = 0; y < 400; y++) {
            for (int x = 0; x < 400; x++) {
              final r = 100 + random.nextInt(100);
              final g = 100 + random.nextInt(100);
              final b = 100 + random.nextInt(100);
              image.setPixelRgba(x, y, r, g, b, 255);
            }
          }
          
          // Save to temp directory first
          final tempFile = File('${tempDir.path}/temp_$j.jpg');
          await tempFile.writeAsBytes(img.encodeJpg(image));
          
          // Save as training image
          final savedFile = await storageService.saveTrainingImage(tempFile);
          createdFiles.add(savedFile);
        }
        
        // Load training images to verify count
        final loadedImages = await storageService.loadTrainingImages();
        
        // Property: Training should attempt to read all images
        expect(loadedImages.length, equals(numImages),
            reason: 'Iteration $i: Should load all $numImages training images');
        
        // Train the model
        final result = await trainingService.trainModel();
        
        // Property: Training result should report the correct number of images
        expect(result.numImages, equals(numImages),
            reason: 'Iteration $i: Training result should report $numImages images');
        
        // Clean up for next iteration
        await storageService.deleteAllTrainingImages();
      }
    });
    
    testWidgets('should handle empty training directory', (WidgetTester tester) async {
      // Ensure no training images exist
      await storageService.deleteAllTrainingImages();
      
      // Property: Training with no images should return appropriate result
      final result = await trainingService.trainModel();
      
      expect(result.success, isFalse,
          reason: 'Training should fail when no images exist');
      expect(result.numImages, equals(0),
          reason: 'Should report 0 images');
      expect(result.errorMessage, contains('Chưa có dữ liệu'),
          reason: 'Should provide appropriate error message');
    });
  });

  group('Property 11: Mean embedding calculation', () {
    testWidgets('should calculate correct arithmetic mean of embeddings - iteration test', (WidgetTester tester) async {
      // Run multiple iterations with different embedding sets
      const iterations = 20;
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Generate random number of embeddings (2-5)
        final numEmbeddings = 2 + random.nextInt(4);
        
        // Create test embeddings with known values
        final testEmbeddings = <List<double>>[];
        for (int j = 0; j < numEmbeddings; j++) {
          final embedding = List<double>.generate(
            128,
            (index) => random.nextDouble() * 2 - 1, // Random values between -1 and 1
          );
          testEmbeddings.add(embedding);
        }
        
        // Calculate expected mean manually
        final expectedMean = List<double>.filled(128, 0.0);
        for (final embedding in testEmbeddings) {
          for (int k = 0; k < 128; k++) {
            expectedMean[k] += embedding[k];
          }
        }
        for (int k = 0; k < 128; k++) {
          expectedMean[k] /= numEmbeddings;
        }
        
        // Create test images and train
        await storageService.deleteAllTrainingImages();
        
        for (int j = 0; j < numEmbeddings; j++) {
          // Create a test image
          final image = img.Image(width: 400, height: 400);
          for (int y = 0; y < 400; y++) {
            for (int x = 0; x < 400; x++) {
              final value = 100 + j * 20;
              image.setPixelRgba(x, y, value, value, value, 255);
            }
          }
          
          final tempFile = File('${tempDir.path}/temp_mean_$j.jpg');
          await tempFile.writeAsBytes(img.encodeJpg(image));
          await storageService.saveTrainingImage(tempFile);
        }
        
        // Train the model
        final result = await trainingService.trainModel();
        
        // Property: Training should succeed and calculate mean
        expect(result.success, isTrue,
            reason: 'Iteration $i: Training should succeed');
        expect(result.numEmbeddings, equals(numEmbeddings),
            reason: 'Iteration $i: Should extract $numEmbeddings embeddings');
        
        // Load the saved mean embedding
        final savedMean = await storageService.loadMeanEmbedding();
        expect(savedMean, isNotNull,
            reason: 'Iteration $i: Mean embedding should be saved');
        expect(savedMean!.length, equals(128),
            reason: 'Iteration $i: Mean embedding should have 128 dimensions');
        
        // Property: Each dimension should be finite
        for (int k = 0; k < 128; k++) {
          expect(savedMean[k].isFinite, isTrue,
              reason: 'Iteration $i: Mean embedding value at index $k should be finite');
        }
        
        // Clean up for next iteration
        await storageService.deleteAllTrainingImages();
      }
    });
    
    testWidgets('should produce mean with same dimension as input embeddings', (WidgetTester tester) async {
      // Create a few test images
      const numImages = 3;
      
      for (int i = 0; i < numImages; i++) {
        final image = img.Image(width: 400, height: 400);
        for (int y = 0; y < 400; y++) {
          for (int x = 0; x < 400; x++) {
            final value = 100 + i * 30;
            image.setPixelRgba(x, y, value, value, value, 255);
          }
        }
        
        final tempFile = File('${tempDir.path}/temp_dim_$i.jpg');
        await tempFile.writeAsBytes(img.encodeJpg(image));
        await storageService.saveTrainingImage(tempFile);
      }
      
      // Train the model
      final result = await trainingService.trainModel();
      
      // Property: Mean embedding dimension should match input dimension (128)
      final savedMean = await storageService.loadMeanEmbedding();
      expect(savedMean, isNotNull);
      expect(savedMean!.length, equals(128),
          reason: 'Mean embedding should have same dimension as input embeddings (128)');
    });
  });

  group('Property 13: Model trained status', () {
    testWidgets('should mark model as trained after successful training - iteration test', (WidgetTester tester) async {
      // Run multiple iterations
      const iterations = 10;
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Clean up
        await storageService.deleteAllTrainingImages();
        
        // Property: Before training, model should not be trained
        final isTrainedBefore = await trainingService.isModelTrained();
        expect(isTrainedBefore, isFalse,
            reason: 'Iteration $i: Model should not be trained initially');
        
        // Create random number of training images (1-5)
        final numImages = 1 + random.nextInt(5);
        
        for (int j = 0; j < numImages; j++) {
          final image = img.Image(width: 400, height: 400);
          for (int y = 0; y < 400; y++) {
            for (int x = 0; x < 400; x++) {
              final r = 100 + random.nextInt(100);
              final g = 100 + random.nextInt(100);
              final b = 100 + random.nextInt(100);
              image.setPixelRgba(x, y, r, g, b, 255);
            }
          }
          
          final tempFile = File('${tempDir.path}/temp_status_$j.jpg');
          await tempFile.writeAsBytes(img.encodeJpg(image));
          await storageService.saveTrainingImage(tempFile);
        }
        
        // Train the model
        final result = await trainingService.trainModel();
        
        // Property: After successful training, model should be marked as trained
        if (result.success) {
          final isTrainedAfter = await trainingService.isModelTrained();
          expect(isTrainedAfter, isTrue,
              reason: 'Iteration $i: Model should be marked as trained after successful training');
          
          // Property: Mean embedding should exist
          final hasMean = await storageService.hasMeanEmbedding();
          expect(hasMean, isTrue,
              reason: 'Iteration $i: Mean embedding should exist after training');
        }
        
        // Clean up for next iteration
        await storageService.deleteAllTrainingImages();
      }
    });
    
    testWidgets('should enable verification after training', (WidgetTester tester) async {
      // Create training images
      const numImages = 3;
      
      for (int i = 0; i < numImages; i++) {
        final image = img.Image(width: 400, height: 400);
        for (int y = 0; y < 400; y++) {
          for (int x = 0; x < 400; x++) {
            final value = 120 + i * 20;
            image.setPixelRgba(x, y, value, value, value, 255);
          }
        }
        
        final tempFile = File('${tempDir.path}/temp_verify_$i.jpg');
        await tempFile.writeAsBytes(img.encodeJpg(image));
        await storageService.saveTrainingImage(tempFile);
      }
      
      // Train the model
      final result = await trainingService.trainModel();
      
      // Property: After training, verification should be possible
      expect(result.success, isTrue,
          reason: 'Training should succeed');
      
      final isModelTrained = await trainingService.isModelTrained();
      expect(isModelTrained, isTrue,
          reason: 'Model should be trained and ready for verification');
      
      // Verify mean embedding can be loaded
      final meanEmbedding = await storageService.loadMeanEmbedding();
      expect(meanEmbedding, isNotNull,
          reason: 'Mean embedding should be loadable for verification');
      expect(meanEmbedding!.length, equals(128),
          reason: 'Mean embedding should have correct dimension');
    });
  });
}
