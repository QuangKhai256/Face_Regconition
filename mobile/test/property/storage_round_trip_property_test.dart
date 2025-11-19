import 'dart:io';
import 'dart:math';
import 'package:flutter_test/flutter_test.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:faceid_mobile/services/storage_service.dart';

// Feature: mobile-embedded-backend, Property 1: Image save/load round trip
// Feature: mobile-embedded-backend, Property 12: Mean embedding persistence round trip
// Feature: mobile-embedded-backend, Property 17: Threshold persistence round trip
// Validates: Requirements 1.5, 6.5, 8.3

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
    
    // Create a temporary directory for testing
    tempDir = await Directory.systemTemp.createTemp('storage_test_');
    
    // Mock path_provider to use temp directory
    mockPathProvider = MockPathProviderPlatform();
    mockPathProvider.setTempPath(tempDir.path);
    PathProviderPlatform.instance = mockPathProvider;
    
    // Clear SharedPreferences
    SharedPreferences.setMockInitialValues({});
  });

  tearDown(() async {
    // Clean up temp directory
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  group('Property 1: Image save/load round trip', () {
    test('should preserve image content after save and load - iteration test', () async {
      // Run multiple iterations to test the property
      const iterations = 100;
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Generate a random test image with random content
        final testImageFile = File('${tempDir.path}/test_input_$i.jpg');
        
        // Create random image data (simulating a JPEG)
        final randomBytes = List.generate(
          100 + random.nextInt(900), // Random size between 100-1000 bytes
          (_) => random.nextInt(256),
        );
        await testImageFile.writeAsBytes(randomBytes);
        
        // Save the image
        final savedFile = await storageService.saveTrainingImage(testImageFile);
        
        // Verify the saved file exists
        expect(await savedFile.exists(), isTrue,
            reason: 'Iteration $i: Saved file should exist');
        
        // Load the saved file content
        final savedContent = await savedFile.readAsBytes();
        final originalContent = await testImageFile.readAsBytes();
        
        // Property: Content should be identical
        expect(savedContent, equals(originalContent),
            reason: 'Iteration $i: Saved content should match original content');
        
        // Clean up for next iteration
        await testImageFile.delete();
        await savedFile.delete();
      }
    });
  });

  group('Property 12: Mean embedding persistence round trip', () {
    test('should preserve embedding values after save and load - iteration test', () async {
      // Run multiple iterations to test the property
      const iterations = 100;
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Generate random embedding (128 or 512 dimensions)
        final dimension = random.nextBool() ? 128 : 512;
        final embedding = List.generate(
          dimension,
          (_) => random.nextDouble() * 2 - 1, // Random values between -1 and 1
        );
        
        // Save the embedding
        await storageService.saveMeanEmbedding(embedding);
        
        // Load the embedding
        final loadedEmbedding = await storageService.loadMeanEmbedding();
        
        // Property: Loaded embedding should not be null
        expect(loadedEmbedding, isNotNull,
            reason: 'Iteration $i: Loaded embedding should not be null');
        
        // Property: Dimension should match
        expect(loadedEmbedding!.length, equals(embedding.length),
            reason: 'Iteration $i: Embedding dimension should match');
        
        // Property: Values should match (within floating point precision)
        for (int j = 0; j < embedding.length; j++) {
          expect(loadedEmbedding[j], closeTo(embedding[j], 1e-10),
              reason: 'Iteration $i: Embedding value at index $j should match');
        }
      }
    });
    
    test('should return null when no embedding exists', () async {
      // Property: Loading non-existent embedding should return null
      final result = await storageService.loadMeanEmbedding();
      expect(result, isNull);
    });
  });

  group('Property 17: Threshold persistence round trip', () {
    setUp(() {
      // Reset SharedPreferences before each test
      SharedPreferences.setMockInitialValues({});
    });
    
    test('should preserve threshold value after save and load - iteration test', () async {
      // Run multiple iterations to test the property
      const iterations = 100;
      final random = Random();
      
      for (int i = 0; i < iterations; i++) {
        // Generate random threshold in valid range [0.3, 1.0]
        final threshold = 0.3 + random.nextDouble() * 0.7;
        
        // Save the threshold
        await storageService.saveThreshold(threshold);
        
        // Load the threshold
        final loadedThreshold = await storageService.loadThreshold();
        
        // Property: Values should match (within floating point precision)
        expect(loadedThreshold, closeTo(threshold, 1e-10),
            reason: 'Iteration $i: Threshold value should match');
      }
    });
    
    test('should return default threshold when none exists', () async {
      // Property: Loading non-existent threshold should return default (0.6)
      final result = await storageService.loadThreshold();
      expect(result, equals(0.6));
    });
  });
}
