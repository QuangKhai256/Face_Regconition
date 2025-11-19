import 'dart:io';
import 'dart:math';
import 'package:flutter_test/flutter_test.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';
import 'package:faceid_mobile/services/storage_service.dart';

// Feature: mobile-embedded-backend, Property 6: Training image filename format
// Validates: Requirements 4.2

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
    tempDir = await Directory.systemTemp.createTemp('filename_test_');
    
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

  group('Property 6: Training image filename format', () {
    test('should match pattern user_YYYYMMDD_HHMMSS.jpg - iteration test', () async {
      // Run multiple iterations to test the property
      const iterations = 100;
      final random = Random();
      
      // Regex pattern for the expected filename format
      final filenamePattern = RegExp(
        r'^user_\d{8}_\d{6}\.jpg$'
      );
      
      // More specific pattern to validate actual date/time components
      final detailedPattern = RegExp(
        r'^user_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\.jpg$'
      );
      
      for (int i = 0; i < iterations; i++) {
        // Create a test image file
        final testImageFile = File('${tempDir.path}/test_$i.jpg');
        final randomBytes = List.generate(
          100 + random.nextInt(100),
          (_) => random.nextInt(256),
        );
        await testImageFile.writeAsBytes(randomBytes);
        
        // Save the image
        final savedFile = await storageService.saveTrainingImage(testImageFile);
        
        // Extract filename from path
        final filename = savedFile.path.split('/').last;
        
        // Property: Filename should match the basic pattern
        expect(filenamePattern.hasMatch(filename), isTrue,
            reason: 'Iteration $i: Filename "$filename" should match pattern user_YYYYMMDD_HHMMSS.jpg');
        
        // Property: Validate date/time components are valid
        final match = detailedPattern.firstMatch(filename);
        expect(match, isNotNull,
            reason: 'Iteration $i: Filename should match detailed pattern');
        
        if (match != null) {
          final year = int.parse(match.group(1)!);
          final month = int.parse(match.group(2)!);
          final day = int.parse(match.group(3)!);
          final hour = int.parse(match.group(4)!);
          final minute = int.parse(match.group(5)!);
          final second = int.parse(match.group(6)!);
          
          // Property: Year should be 4 digits and reasonable
          expect(year, greaterThanOrEqualTo(2020),
              reason: 'Iteration $i: Year should be >= 2020');
          expect(year, lessThanOrEqualTo(2100),
              reason: 'Iteration $i: Year should be <= 2100');
          
          // Property: Month should be 01-12
          expect(month, greaterThanOrEqualTo(1),
              reason: 'Iteration $i: Month should be >= 1');
          expect(month, lessThanOrEqualTo(12),
              reason: 'Iteration $i: Month should be <= 12');
          
          // Property: Day should be 01-31
          expect(day, greaterThanOrEqualTo(1),
              reason: 'Iteration $i: Day should be >= 1');
          expect(day, lessThanOrEqualTo(31),
              reason: 'Iteration $i: Day should be <= 31');
          
          // Property: Hour should be 00-23
          expect(hour, greaterThanOrEqualTo(0),
              reason: 'Iteration $i: Hour should be >= 0');
          expect(hour, lessThanOrEqualTo(23),
              reason: 'Iteration $i: Hour should be <= 23');
          
          // Property: Minute should be 00-59
          expect(minute, greaterThanOrEqualTo(0),
              reason: 'Iteration $i: Minute should be >= 0');
          expect(minute, lessThanOrEqualTo(59),
              reason: 'Iteration $i: Minute should be <= 59');
          
          // Property: Second should be 00-59
          expect(second, greaterThanOrEqualTo(0),
              reason: 'Iteration $i: Second should be >= 0');
          expect(second, lessThanOrEqualTo(59),
              reason: 'Iteration $i: Second should be <= 59');
        }
        
        // Clean up
        await testImageFile.delete();
        await savedFile.delete();
        
        // Small delay to ensure different timestamps
        if (i < iterations - 1) {
          await Future.delayed(const Duration(milliseconds: 10));
        }
      }
    });
    
    test('should generate unique filenames for sequential saves', () async {
      // Property: Sequential saves should generate different filenames
      final filenames = <String>{};
      
      for (int i = 0; i < 5; i++) {
        final testImageFile = File('${tempDir.path}/test_seq_$i.jpg');
        await testImageFile.writeAsBytes([1, 2, 3]);
        
        final savedFile = await storageService.saveTrainingImage(testImageFile);
        final filename = savedFile.path.split('/').last;
        
        filenames.add(filename);
        
        await testImageFile.delete();
        await savedFile.delete();
        
        // Delay to ensure different timestamps (1 second for reliable uniqueness)
        await Future.delayed(const Duration(seconds: 1));
      }
      
      // Property: All filenames should be unique
      expect(filenames.length, equals(5),
          reason: 'All generated filenames should be unique');
    });
  });
}
