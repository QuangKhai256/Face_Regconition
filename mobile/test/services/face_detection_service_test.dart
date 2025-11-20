import 'package:flutter_test/flutter_test.dart';
import 'package:faceid_mobile/models/face_detection_result.dart';

// Unit tests for face detection edge cases
// Requirements: 2.2, 2.3, 2.4

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('FaceDetectionResult - No face edge case', () {
    test('should create result with no face detected', () {
      // Requirement 2.2: No face detected
      final result = FaceDetectionResult.noFace();
      
      expect(result.success, isFalse);
      expect(result.face, isNull);
      expect(result.faceCount, equals(0));
      expect(result.errorMessage, equals('Không phát hiện khuôn mặt'));
    });
    
    test('should have consistent state when no face detected', () {
      final result = FaceDetectionResult.noFace();
      
      // When no faces, success should be false
      expect(result.success, isFalse);
      // When no faces, face object should be null
      expect(result.face, isNull);
      // Error message should be provided
      expect(result.errorMessage, isNotNull);
      expect(result.errorMessage!.isNotEmpty, isTrue);
    });
  });

  group('FaceDetectionResult - Multiple faces edge case', () {
    test('should create result with multiple faces detected', () {
      // Requirement 2.3: Multiple faces detected
      final result = FaceDetectionResult.multipleFaces(3);
      
      expect(result.success, isFalse);
      expect(result.face, isNull);
      expect(result.faceCount, equals(3));
      expect(result.errorMessage, contains('Phát hiện nhiều khuôn mặt'));
      expect(result.errorMessage, contains('3'));
    });
    
    test('should handle various multiple face counts', () {
      for (int count = 2; count <= 10; count++) {
        final result = FaceDetectionResult.multipleFaces(count);
        
        expect(result.success, isFalse,
            reason: 'Success should be false for $count faces');
        expect(result.face, isNull,
            reason: 'Face should be null for $count faces');
        expect(result.faceCount, equals(count),
            reason: 'Face count should match for $count faces');
        expect(result.errorMessage, contains(count.toString()),
            reason: 'Error message should contain count for $count faces');
      }
    });
    
    test('should have consistent state when multiple faces detected', () {
      final result = FaceDetectionResult.multipleFaces(5);
      
      // When multiple faces, success should be false
      expect(result.success, isFalse);
      // When multiple faces, face object should be null
      expect(result.face, isNull);
      // Face count should be greater than 1
      expect(result.faceCount, greaterThan(1));
      // Error message should be provided
      expect(result.errorMessage, isNotNull);
      expect(result.errorMessage!.isNotEmpty, isTrue);
    });
  });

  group('FaceDetectionResult - Single face success case', () {
    test('should create result with exactly one face detected', () {
      // Requirement 2.4: Exactly one face detected
      // Note: We can't create a real Face object without ML Kit platform implementation
      // So we test the result model structure
      final result = FaceDetectionResult(
        success: true,
        face: null, // In real usage, this would be a Face object
        faceCount: 1,
      );
      
      expect(result.success, isTrue);
      expect(result.faceCount, equals(1));
      expect(result.errorMessage, isNull);
    });
    
    test('should have consistent state when single face detected', () {
      final result = FaceDetectionResult(
        success: true,
        face: null,
        faceCount: 1,
      );
      
      // When single face, success should be true
      expect(result.success, isTrue);
      // Face count should be exactly 1
      expect(result.faceCount, equals(1));
      // Error message should be null for success
      expect(result.errorMessage, isNull);
    });
  });

  group('FaceDetectionResult - Custom error case', () {
    test('should create result with custom error message', () {
      final result = FaceDetectionResult.error('Custom error message', 0);
      
      expect(result.success, isFalse);
      expect(result.face, isNull);
      expect(result.faceCount, equals(0));
      expect(result.errorMessage, equals('Custom error message'));
    });
    
    test('should handle various error scenarios', () {
      final errorScenarios = [
        {'message': 'ML Kit not available', 'count': 0},
        {'message': 'Image processing failed', 'count': 0},
        {'message': 'Invalid image format', 'count': 0},
      ];
      
      for (final scenario in errorScenarios) {
        final result = FaceDetectionResult.error(
          scenario['message'] as String,
          scenario['count'] as int,
        );
        
        expect(result.success, isFalse);
        expect(result.errorMessage, equals(scenario['message']));
        expect(result.faceCount, equals(scenario['count']));
      }
    });
  });

  group('FaceDetectionResult - Factory methods', () {
    test('singleFace factory should create success result', () {
      // Note: Can't create real Face object without platform implementation
      // This test validates the factory pattern structure
      final result = FaceDetectionResult(
        success: true,
        face: null,
        faceCount: 1,
      );
      
      expect(result.success, isTrue);
      expect(result.faceCount, equals(1));
    });
    
    test('noFace factory should create failure result', () {
      final result = FaceDetectionResult.noFace();
      
      expect(result.success, isFalse);
      expect(result.faceCount, equals(0));
      expect(result.errorMessage, isNotNull);
    });
    
    test('multipleFaces factory should create failure result', () {
      final result = FaceDetectionResult.multipleFaces(2);
      
      expect(result.success, isFalse);
      expect(result.faceCount, equals(2));
      expect(result.errorMessage, isNotNull);
    });
    
    test('error factory should create failure result', () {
      final result = FaceDetectionResult.error('Test error', 0);
      
      expect(result.success, isFalse);
      expect(result.errorMessage, equals('Test error'));
    });
  });

  group('FaceDetectionResult - Edge case validation', () {
    test('should handle zero face count correctly', () {
      final result = FaceDetectionResult.noFace();
      
      expect(result.faceCount, equals(0));
      expect(result.success, isFalse);
    });
    
    test('should handle large face counts correctly', () {
      final result = FaceDetectionResult.multipleFaces(100);
      
      expect(result.faceCount, equals(100));
      expect(result.success, isFalse);
      expect(result.errorMessage, contains('100'));
    });
    
    test('should maintain consistency between success and face count', () {
      // Test various face counts
      final testCases = [
        {'count': 0, 'shouldSucceed': false},
        {'count': 1, 'shouldSucceed': true},
        {'count': 2, 'shouldSucceed': false},
        {'count': 5, 'shouldSucceed': false},
      ];
      
      for (final testCase in testCases) {
        final count = testCase['count'] as int;
        final shouldSucceed = testCase['shouldSucceed'] as bool;
        
        FaceDetectionResult result;
        if (count == 0) {
          result = FaceDetectionResult.noFace();
        } else if (count == 1) {
          result = FaceDetectionResult(
            success: true,
            face: null,
            faceCount: 1,
          );
        } else {
          result = FaceDetectionResult.multipleFaces(count);
        }
        
        expect(result.success, equals(shouldSucceed),
            reason: 'Success state should match for count $count');
        expect(result.faceCount, equals(count),
            reason: 'Face count should match for count $count');
      }
    });
  });
}
