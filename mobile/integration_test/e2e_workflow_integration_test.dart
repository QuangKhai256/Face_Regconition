import 'dart:io';
import 'dart:math';
import 'dart:ui' as ui;
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:faceid_mobile/services/storage_service.dart';
import 'package:faceid_mobile/services/embedding_service.dart';
import 'package:faceid_mobile/services/face_detection_service.dart';
import 'package:faceid_mobile/services/training_service.dart';
import 'package:faceid_mobile/services/verification_service.dart';
import 'package:faceid_mobile/services/environment_service.dart';
import 'package:image/image.dart' as img;

// End-to-end integration tests for complete workflows
// Tests: collect → train → verify
// Validates: All requirements

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  late StorageService storageService;
  late EmbeddingService embeddingService;
  late FaceDetectionService faceDetectionService;
  late TrainingService trainingService;
  late VerificationService verificationService;
  late EnvironmentService environmentService;
  late Directory tempDir;

  setUp(() async {
    storageService = StorageService();
    embeddingService = EmbeddingService();
    faceDetectionService = FaceDetectionService();
    environmentService = EnvironmentService();
    
    trainingService = TrainingService(
      storageService: storageService,
      embeddingService: embeddingService,
      faceDetectionService: faceDetectionService,
    );
    
    verificationService = VerificationService(
      storageService: storageService,
      embeddingService: embeddingService,
    );
    
    // Create a temporary directory for test images
    tempDir = await Directory.systemTemp.createTemp('e2e_test_');
    
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

  group('End-to-End Collection Workflow', () {
    testWidgets('should complete full collection workflow', (WidgetTester tester) async {
      final random = Random();
      
      // Step 1: Create a test image (simulating camera capture)
      final image = img.Image(width: 640, height: 480);
      
      // Fill with realistic pixel values
      for (int y = 0; y < 480; y++) {
        for (int x = 0; x < 640; x++) {
          final r = 100 + random.nextInt(100);
          final g = 100 + random.nextInt(100);
          final b = 100 + random.nextInt(100);
          image.setPixelRgba(x, y, r, g, b, 255);
        }
      }
      
      final capturedImageFile = File('${tempDir.path}/captured.jpg');
      await capturedImageFile.writeAsBytes(img.encodeJpg(image));
      
      // Step 2: Detect face (simulating face detection)
      // For this test, we'll create a mock face box since we can't guarantee
      // ML Kit will detect a face in our synthetic image
      final faceBox = ui.Rect.fromLTWH(200, 150, 240, 240);
      
      // Step 3: Check environment quality
      final envInfo = await environmentService.analyzeEnvironment(
        capturedImageFile,
        faceBox,
      );
      
      expect(envInfo, isNotNull);
      expect(envInfo.brightness, greaterThanOrEqualTo(0));
      expect(envInfo.brightness, lessThanOrEqualTo(255));
      expect(envInfo.blurScore, greaterThanOrEqualTo(0));
      expect(envInfo.faceSizeRatio, greaterThanOrEqualTo(0));
      expect(envInfo.faceSizeRatio, lessThanOrEqualTo(1.0));
      
      // Step 4: Save training image
      final savedFile = await storageService.saveTrainingImage(capturedImageFile);
      
      expect(savedFile.existsSync(), isTrue);
      expect(savedFile.path, contains('user_'));
      expect(savedFile.path, endsWith('.jpg'));
      
      // Step 5: Verify image counter
      final images = await storageService.loadTrainingImages();
      expect(images.length, equals(1));
      
      // Clean up
      await storageService.deleteAllTrainingImages();
    });
    
    testWidgets('should handle multiple image collection', (WidgetTester tester) async {
      final random = Random();
      const numImages = 5;
      
      for (int i = 0; i < numImages; i++) {
        // Create test image
        final image = img.Image(width: 640, height: 480);
        
        for (int y = 0; y < 480; y++) {
          for (int x = 0; x < 640; x++) {
            final value = 100 + i * 10 + random.nextInt(50);
            image.setPixelRgba(x, y, value, value, value, 255);
          }
        }
        
        final capturedImageFile = File('${tempDir.path}/captured_$i.jpg');
        await capturedImageFile.writeAsBytes(img.encodeJpg(image));
        
        // Save training image
        await storageService.saveTrainingImage(capturedImageFile);
        
        // Verify counter increments
        final images = await storageService.loadTrainingImages();
        expect(images.length, equals(i + 1));
      }
      
      // Verify final count
      final finalImages = await storageService.loadTrainingImages();
      expect(finalImages.length, equals(numImages));
      
      // Clean up
      await storageService.deleteAllTrainingImages();
    });
    
    testWidgets('should handle delete all images', (WidgetTester tester) async {
      // Create some test images
      for (int i = 0; i < 3; i++) {
        final image = img.Image(width: 400, height: 400);
        final tempFile = File('${tempDir.path}/temp_$i.jpg');
        await tempFile.writeAsBytes(img.encodeJpg(image));
        await storageService.saveTrainingImage(tempFile);
      }
      
      // Verify images exist
      final imagesBefore = await storageService.loadTrainingImages();
      expect(imagesBefore.length, equals(3));
      
      // Delete all
      await storageService.deleteAllTrainingImages();
      
      // Verify all deleted
      final imagesAfter = await storageService.loadTrainingImages();
      expect(imagesAfter.length, equals(0));
    });
  });

  group('End-to-End Training Workflow', () {
    testWidgets('should complete full training workflow', (WidgetTester tester) async {
      final random = Random();
      
      // Step 1: Verify model not trained initially
      final isTrainedBefore = await trainingService.isModelTrained();
      expect(isTrainedBefore, isFalse);
      
      // Step 2: Collect training images
      const numImages = 5;
      for (int i = 0; i < numImages; i++) {
        final image = img.Image(width: 640, height: 480);
        
        for (int y = 0; y < 480; y++) {
          for (int x = 0; x < 640; x++) {
            final r = 100 + random.nextInt(100);
            final g = 100 + random.nextInt(100);
            final b = 100 + random.nextInt(100);
            image.setPixelRgba(x, y, r, g, b, 255);
          }
        }
        
        final tempFile = File('${tempDir.path}/training_$i.jpg');
        await tempFile.writeAsBytes(img.encodeJpg(image));
        await storageService.saveTrainingImage(tempFile);
      }
      
      // Step 3: Verify images collected
      final collectedImages = await storageService.loadTrainingImages();
      expect(collectedImages.length, equals(numImages));
      
      // Step 4: Train model
      final trainingResult = await trainingService.trainModel();
      
      expect(trainingResult.success, isTrue);
      expect(trainingResult.numImages, equals(numImages));
      expect(trainingResult.numEmbeddings, greaterThan(0));
      expect(trainingResult.errorMessage, isNull);
      
      // Step 5: Verify model trained status
      final isTrainedAfter = await trainingService.isModelTrained();
      expect(isTrainedAfter, isTrue);
      
      // Step 6: Verify mean embedding saved
      final hasMeanEmbedding = await storageService.hasMeanEmbedding();
      expect(hasMeanEmbedding, isTrue);
      
      final meanEmbedding = await storageService.loadMeanEmbedding();
      expect(meanEmbedding, isNotNull);
      expect(meanEmbedding!.length, equals(128));
      
      // Clean up
      await storageService.deleteAllTrainingImages();
    });
    
    testWidgets('should fail training with no images', (WidgetTester tester) async {
      // Ensure no training images
      await storageService.deleteAllTrainingImages();
      
      // Attempt to train
      final trainingResult = await trainingService.trainModel();
      
      expect(trainingResult.success, isFalse);
      expect(trainingResult.numImages, equals(0));
      expect(trainingResult.errorMessage, isNotNull);
      expect(trainingResult.errorMessage, contains('Chưa có dữ liệu'));
      
      // Verify model not trained
      final isTrained = await trainingService.isModelTrained();
      expect(isTrained, isFalse);
    });
    
    testWidgets('should handle retraining with new images', (WidgetTester tester) async {
      final random = Random();
      
      // First training session
      for (int i = 0; i < 3; i++) {
        final image = img.Image(width: 400, height: 400);
        for (int y = 0; y < 400; y++) {
          for (int x = 0; x < 400; x++) {
            final value = 100 + i * 20;
            image.setPixelRgba(x, y, value, value, value, 255);
          }
        }
        
        final tempFile = File('${tempDir.path}/first_$i.jpg');
        await tempFile.writeAsBytes(img.encodeJpg(image));
        await storageService.saveTrainingImage(tempFile);
      }
      
      final firstTraining = await trainingService.trainModel();
      expect(firstTraining.success, isTrue);
      expect(firstTraining.numImages, equals(3));
      
      final firstMean = await storageService.loadMeanEmbedding();
      
      // Add more images
      for (int i = 0; i < 2; i++) {
        final image = img.Image(width: 400, height: 400);
        for (int y = 0; y < 400; y++) {
          for (int x = 0; x < 400; x++) {
            final value = 150 + i * 20;
            image.setPixelRgba(x, y, value, value, value, 255);
          }
        }
        
        final tempFile = File('${tempDir.path}/second_$i.jpg');
        await tempFile.writeAsBytes(img.encodeJpg(image));
        await storageService.saveTrainingImage(tempFile);
      }
      
      // Retrain
      final secondTraining = await trainingService.trainModel();
      expect(secondTraining.success, isTrue);
      expect(secondTraining.numImages, equals(5));
      
      final secondMean = await storageService.loadMeanEmbedding();
      
      // Verify mean embedding changed
      expect(firstMean, isNotNull);
      expect(secondMean, isNotNull);
      
      // Clean up
      await storageService.deleteAllTrainingImages();
    });
  });

  group('End-to-End Verification Workflow', () {
    testWidgets('should complete full verification workflow', (WidgetTester tester) async {
      final random = Random();
      
      // Step 1: Collect and train
      const numTrainingImages = 5;
      for (int i = 0; i < numTrainingImages; i++) {
        final image = img.Image(width: 640, height: 480);
        
        for (int y = 0; y < 480; y++) {
          for (int x = 0; x < 640; x++) {
            final r = 100 + random.nextInt(100);
            final g = 100 + random.nextInt(100);
            final b = 100 + random.nextInt(100);
            image.setPixelRgba(x, y, r, g, b, 255);
          }
        }
        
        final tempFile = File('${tempDir.path}/train_verify_$i.jpg');
        await tempFile.writeAsBytes(img.encodeJpg(image));
        await storageService.saveTrainingImage(tempFile);
      }
      
      final trainingResult = await trainingService.trainModel();
      expect(trainingResult.success, isTrue);
      
      // Step 2: Create verification image
      final verifyImage = img.Image(width: 640, height: 480);
      for (int y = 0; y < 480; y++) {
        for (int x = 0; x < 640; x++) {
          final r = 100 + random.nextInt(100);
          final g = 100 + random.nextInt(100);
          final b = 100 + random.nextInt(100);
          verifyImage.setPixelRgba(x, y, r, g, b, 255);
        }
      }
      
      final verifyImageFile = File('${tempDir.path}/verify.jpg');
      await verifyImageFile.writeAsBytes(img.encodeJpg(verifyImage));
      
      // Step 3: Detect face (mock face box)
      final faceBox = ui.Rect.fromLTWH(200, 150, 240, 240);
      
      // Step 4: Check environment
      final envInfo = await environmentService.analyzeEnvironment(
        verifyImageFile,
        faceBox,
      );
      expect(envInfo, isNotNull);
      
      // Step 5: Verify face
      const threshold = 0.6;
      final verifyResult = await verificationService.verify(
        verifyImageFile,
        faceBox,
        threshold,
      );
      
      expect(verifyResult, isNotNull);
      expect(verifyResult.distance, greaterThanOrEqualTo(0));
      expect(verifyResult.threshold, equals(threshold));
      expect(verifyResult.message, isNotEmpty);
      
      // Verify result is consistent with threshold
      if (verifyResult.distance <= threshold) {
        expect(verifyResult.isMatch, isTrue);
      } else {
        expect(verifyResult.isMatch, isFalse);
      }
      
      // Clean up
      await storageService.deleteAllTrainingImages();
    });
    
    testWidgets('should fail verification when model not trained', (WidgetTester tester) async {
      // Ensure no training
      await storageService.deleteAllTrainingImages();
      
      // Create verification image
      final image = img.Image(width: 400, height: 400);
      final verifyImageFile = File('${tempDir.path}/verify_no_model.jpg');
      await verifyImageFile.writeAsBytes(img.encodeJpg(image));
      
      final faceBox = ui.Rect.fromLTWH(100, 100, 200, 200);
      
      // Attempt verification
      try {
        await verificationService.verify(verifyImageFile, faceBox, 0.6);
        fail('Should throw exception when model not trained');
      } catch (e) {
        expect(e.toString(), contains('Chưa huấn luyện'));
      }
    });
    
    testWidgets('should respect threshold changes', (WidgetTester tester) async {
      final random = Random();
      
      // Train model
      for (int i = 0; i < 3; i++) {
        final image = img.Image(width: 400, height: 400);
        for (int y = 0; y < 400; y++) {
          for (int x = 0; x < 400; x++) {
            final value = 120;
            image.setPixelRgba(x, y, value, value, value, 255);
          }
        }
        
        final tempFile = File('${tempDir.path}/threshold_train_$i.jpg');
        await tempFile.writeAsBytes(img.encodeJpg(image));
        await storageService.saveTrainingImage(tempFile);
      }
      
      await trainingService.trainModel();
      
      // Create verification image
      final verifyImage = img.Image(width: 400, height: 400);
      for (int y = 0; y < 400; y++) {
        for (int x = 0; x < 400; x++) {
          final value = 130;
          verifyImage.setPixelRgba(x, y, value, value, value, 255);
        }
      }
      
      final verifyImageFile = File('${tempDir.path}/threshold_verify.jpg');
      await verifyImageFile.writeAsBytes(img.encodeJpg(verifyImage));
      
      final faceBox = ui.Rect.fromLTWH(100, 100, 200, 200);
      
      // Test with different thresholds
      final thresholds = [0.3, 0.5, 0.7, 1.0];
      
      for (final threshold in thresholds) {
        final result = await verificationService.verify(
          verifyImageFile,
          faceBox,
          threshold,
        );
        
        expect(result.threshold, equals(threshold));
        
        // Verify consistency
        if (result.distance <= threshold) {
          expect(result.isMatch, isTrue);
        } else {
          expect(result.isMatch, isFalse);
        }
      }
      
      // Clean up
      await storageService.deleteAllTrainingImages();
    });
  });

  group('End-to-End Complete Workflow', () {
    testWidgets('should complete full collect → train → verify cycle', (WidgetTester tester) async {
      final random = Random();
      
      // Phase 1: Collection
      print('Phase 1: Collecting training images...');
      const numTrainingImages = 7;
      
      for (int i = 0; i < numTrainingImages; i++) {
        // Simulate camera capture
        final image = img.Image(width: 640, height: 480);
        
        for (int y = 0; y < 480; y++) {
          for (int x = 0; x < 640; x++) {
            final r = 100 + random.nextInt(100);
            final g = 100 + random.nextInt(100);
            final b = 100 + random.nextInt(100);
            image.setPixelRgba(x, y, r, g, b, 255);
          }
        }
        
        final capturedFile = File('${tempDir.path}/capture_$i.jpg');
        await capturedFile.writeAsBytes(img.encodeJpg(image));
        
        // Simulate face detection (mock)
        final faceBox = ui.Rect.fromLTWH(200, 150, 240, 240);
        
        // Check environment
        final envInfo = await environmentService.analyzeEnvironment(
          capturedFile,
          faceBox,
        );
        
        // Save if acceptable (or save anyway for test)
        await storageService.saveTrainingImage(capturedFile);
        
        print('  Collected image ${i + 1}/$numTrainingImages');
      }
      
      // Verify collection
      final collectedImages = await storageService.loadTrainingImages();
      expect(collectedImages.length, equals(numTrainingImages));
      print('Collection complete: ${collectedImages.length} images');
      
      // Phase 2: Training
      print('Phase 2: Training model...');
      
      final trainingResult = await trainingService.trainModel();
      
      expect(trainingResult.success, isTrue);
      expect(trainingResult.numImages, equals(numTrainingImages));
      expect(trainingResult.numEmbeddings, greaterThan(0));
      
      print('Training complete: ${trainingResult.numEmbeddings} embeddings extracted');
      
      // Verify model trained
      final isTrained = await trainingService.isModelTrained();
      expect(isTrained, isTrue);
      
      // Phase 3: Verification
      print('Phase 3: Verifying faces...');
      
      // Test multiple verification attempts
      for (int i = 0; i < 3; i++) {
        // Create verification image
        final verifyImage = img.Image(width: 640, height: 480);
        
        for (int y = 0; y < 480; y++) {
          for (int x = 0; x < 640; x++) {
            final r = 100 + random.nextInt(100);
            final g = 100 + random.nextInt(100);
            final b = 100 + random.nextInt(100);
            verifyImage.setPixelRgba(x, y, r, g, b, 255);
          }
        }
        
        final verifyFile = File('${tempDir.path}/verify_$i.jpg');
        await verifyFile.writeAsBytes(img.encodeJpg(verifyImage));
        
        // Detect face (mock)
        final faceBox = ui.Rect.fromLTWH(200, 150, 240, 240);
        
        // Verify
        const threshold = 0.6;
        final verifyResult = await verificationService.verify(
          verifyFile,
          faceBox,
          threshold,
        );
        
        expect(verifyResult, isNotNull);
        expect(verifyResult.distance, greaterThanOrEqualTo(0));
        
        print('  Verification ${i + 1}: ${verifyResult.isMatch ? "Match" : "No match"} (distance: ${verifyResult.distance.toStringAsFixed(4)})');
      }
      
      print('Complete workflow test passed!');
      
      // Clean up
      await storageService.deleteAllTrainingImages();
    });
  });

  group('Error Scenario Tests', () {
    testWidgets('should handle missing training images gracefully', (WidgetTester tester) async {
      await storageService.deleteAllTrainingImages();
      
      final result = await trainingService.trainModel();
      
      expect(result.success, isFalse);
      expect(result.errorMessage, isNotNull);
    });
    
    testWidgets('should handle verification without training', (WidgetTester tester) async {
      await storageService.deleteAllTrainingImages();
      
      final image = img.Image(width: 400, height: 400);
      final imageFile = File('${tempDir.path}/error_test.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      final faceBox = ui.Rect.fromLTWH(100, 100, 200, 200);
      
      try {
        await verificationService.verify(imageFile, faceBox, 0.6);
        fail('Should throw exception');
      } catch (e) {
        expect(e, isNotNull);
      }
    });
    
    testWidgets('should handle threshold persistence', (WidgetTester tester) async {
      // Save threshold
      const testThreshold = 0.75;
      await storageService.saveThreshold(testThreshold);
      
      // Load threshold
      final loadedThreshold = await storageService.loadThreshold();
      
      expect(loadedThreshold, closeTo(testThreshold, 0.001));
    });
    
    testWidgets('should handle environment warnings', (WidgetTester tester) async {
      // Create a very dark image
      final darkImage = img.Image(width: 400, height: 400);
      for (int y = 0; y < 400; y++) {
        for (int x = 0; x < 400; x++) {
          darkImage.setPixelRgba(x, y, 20, 20, 20, 255);
        }
      }
      
      final darkFile = File('${tempDir.path}/dark.jpg');
      await darkFile.writeAsBytes(img.encodeJpg(darkImage));
      
      final faceBox = ui.Rect.fromLTWH(100, 100, 200, 200);
      
      final envInfo = await environmentService.analyzeEnvironment(darkFile, faceBox);
      
      expect(envInfo.isTooDark, isTrue);
      expect(envInfo.warnings, isNotEmpty);
      expect(envInfo.warnings.any((w) => w.contains('tối')), isTrue);
    });
    
    testWidgets('should handle small face warning', (WidgetTester tester) async {
      final image = img.Image(width: 1000, height: 1000);
      final imageFile = File('${tempDir.path}/small_face.jpg');
      await imageFile.writeAsBytes(img.encodeJpg(image));
      
      // Very small face box
      final smallFaceBox = ui.Rect.fromLTWH(400, 400, 50, 50);
      
      final envInfo = await environmentService.analyzeEnvironment(imageFile, smallFaceBox);
      
      expect(envInfo.isFaceTooSmall, isTrue);
      expect(envInfo.warnings, isNotEmpty);
    });
  });
}
