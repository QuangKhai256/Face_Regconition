import 'dart:io';
import 'dart:math';
import 'package:flutter_test/flutter_test.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';
import 'package:faceid_mobile/services/storage_service.dart';

// Feature: mobile-embedded-backend, Property 7: Image counter consistency
// Validates: Requirements 4.3

// Mock PathProvider for testing
class MockPathProviderPlatform extends Fake
    with MockPlatformInterfaceMixin
    implements PathProviderPlatform {
  String? _tempPath;

  void setTempPath(String path) {
    _tempPath = path;
  }

  @override
  Future<String?> getApplicationDocumentsPath() async {
    return _tempPath;
  }

  @override
  Future<String?> getTemporaryPath() async {
    return _tempPath;
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  
  late StorageService storageService;
  late Directory tempDir;
  late MockPathProviderPlatform mockPathProvider;

  setUp(() async {
    storageService = StorageService();
    tempDir = await Directory.systemTemp.createTemp('counter_test_');
    
    // Mock path_provider to use temp directory
    mockPathProvider = MockPathProviderPlatform();
    mockPathProvider.setTempPath(tempDir.path);
    PathProviderPlatform.instance = mockPathProvider;
  });

  tearDown(() async {
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  group('Property 7: Image counter consistency', () {
    test('should match number of successfully saved images - iteration test', () async {
      // Run multiple iterations with different numbers of images
      // Note: Due to second-precision timestamps, we need delays between saves
      const iterations = 10;
      final random = Random();
      
      for (int iteration = 0; iteration < iterations; iteration++) {
        // Clean up any existing training images
        await storageService.deleteAllTrainingImages();
        
        // Generate random number of images to save (1-3 to keep test time reasonable)
        final numImagesToSave = 1 + random.nextInt(3);
        int successfullySaved = 0;
        
        // Save images
        for (int i = 0; i < numImagesToSave; i++) {
          try {
            final testImageFile = File('${tempDir.path}/test_iter${iteration}_img$i.jpg');
            final randomBytes = List.generate(
              100 + random.nextInt(100),
              (_) => random.nextInt(256),
            );
            await testImageFile.writeAsBytes(randomBytes);
            
            // Save the image
            await storageService.saveTrainingImage(testImageFile);
            successfullySaved++;
            
            // Clean up source file
            await testImageFile.delete();
            
            // Delay to ensure unique timestamps (1 second for second-precision timestamps)
            if (i < numImagesToSave - 1) {
              await Future.delayed(const Duration(seconds: 1, milliseconds: 100));
            }
          } catch (e) {
            // If save fails, don't increment counter
            print('Save failed for iteration $iteration, image $i: $e');
          }
        }
        
        // Load all training images
        final loadedImages = await storageService.loadTrainingImages();
        
        // Property: Count should equal number of successfully saved images
        expect(loadedImages.length, equals(successfullySaved),
            reason: 'Iteration $iteration: Loaded image count should match successfully saved count (expected $successfullySaved, got ${loadedImages.length})');
        
        // Property: All loaded files should exist
        for (final file in loadedImages) {
          expect(await file.exists(), isTrue,
              reason: 'Iteration $iteration: All loaded files should exist');
        }
        
        // Property: All loaded files should be image files
        for (final file in loadedImages) {
          final filename = file.path.split(Platform.pathSeparator).last;
          expect(filename.endsWith('.jpg') || filename.endsWith('.jpeg'), isTrue,
              reason: 'Iteration $iteration: All loaded files should be image files');
        }
      }
    });
    
    test('should return zero count after deleteAllTrainingImages', () async {
      // Save some images first (reduced number for test speed)
      final random = Random();
      final numImages = 2 + random.nextInt(3);
      
      for (int i = 0; i < numImages; i++) {
        final testImageFile = File('${tempDir.path}/test_delete_$i.jpg');
        await testImageFile.writeAsBytes([1, 2, 3]);
        await storageService.saveTrainingImage(testImageFile);
        await testImageFile.delete();
        // Delay to ensure unique timestamps
        if (i < numImages - 1) {
          await Future.delayed(const Duration(seconds: 1, milliseconds: 100));
        }
      }
      
      // Verify images were saved
      var loadedImages = await storageService.loadTrainingImages();
      expect(loadedImages.length, equals(numImages));
      
      // Delete all images
      await storageService.deleteAllTrainingImages();
      
      // Property: Count should be zero after deletion
      loadedImages = await storageService.loadTrainingImages();
      expect(loadedImages.length, equals(0),
          reason: 'Image count should be zero after deleteAllTrainingImages');
    });
    
    test('should maintain correct count across multiple save-delete cycles', () async {
      final random = Random();
      
      for (int cycle = 0; cycle < 5; cycle++) {
        // Save random number of images (1-2 to keep test time reasonable)
        final numToSave = 1 + random.nextInt(2);
        
        for (int i = 0; i < numToSave; i++) {
          final testImageFile = File('${tempDir.path}/test_cycle${cycle}_$i.jpg');
          await testImageFile.writeAsBytes([1, 2, 3]);
          await storageService.saveTrainingImage(testImageFile);
          await testImageFile.delete();
          // Delay to ensure unique timestamps
          if (i < numToSave - 1) {
            await Future.delayed(const Duration(seconds: 1, milliseconds: 100));
          }
        }
        
        // Verify count
        var loadedImages = await storageService.loadTrainingImages();
        expect(loadedImages.length, equals(numToSave),
            reason: 'Cycle $cycle: Count should match saved images');
        
        // Delete all
        await storageService.deleteAllTrainingImages();
        
        // Verify count is zero
        loadedImages = await storageService.loadTrainingImages();
        expect(loadedImages.length, equals(0),
            reason: 'Cycle $cycle: Count should be zero after delete');
      }
    });
    
    test('should handle empty directory correctly', () async {
      // Ensure directory is empty
      await storageService.deleteAllTrainingImages();
      
      // Property: Loading from empty directory should return empty list
      final loadedImages = await storageService.loadTrainingImages();
      expect(loadedImages.length, equals(0),
          reason: 'Empty directory should return zero count');
    });
  });
}
