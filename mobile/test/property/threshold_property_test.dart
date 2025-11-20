import 'dart:math';
import 'package:flutter_test/flutter_test.dart';
import 'package:faceid_mobile/services/storage_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Property-based tests for threshold management
/// Tests universal properties that should hold across all inputs
/// Feature: mobile-embedded-backend

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Threshold Property Tests', () {
    late StorageService storageService;

    setUp(() async {
      // Clear SharedPreferences before each test
      SharedPreferences.setMockInitialValues({});
      storageService = StorageService();
    });

    /// Feature: mobile-embedded-backend, Property 16: Threshold range validation
    /// **Validates: Requirements 8.2**
    /// 
    /// Property: For any threshold value set by the user,
    /// the value should be within the range [0.3, 1.0]
    test('Property 16: Threshold range validation', () async {
      final random = Random(42); // Fixed seed for reproducibility
      const int numTests = 100;

      for (int testNum = 0; testNum < numTests; testNum++) {
        // Generate random threshold values in different ranges
        double threshold;
        bool shouldBeValid;

        if (testNum % 4 == 0) {
          // Valid range [0.3, 1.0]
          threshold = 0.3 + random.nextDouble() * 0.7; // [0.3, 1.0]
          shouldBeValid = true;
        } else if (testNum % 4 == 1) {
          // Below minimum (< 0.3)
          threshold = random.nextDouble() * 0.3; // [0.0, 0.3)
          shouldBeValid = false;
        } else if (testNum % 4 == 2) {
          // Above maximum (> 1.0)
          threshold = 1.0 + random.nextDouble() * 2.0; // (1.0, 3.0]
          shouldBeValid = false;
        } else {
          // Edge cases
          if (random.nextBool()) {
            threshold = 0.3; // Minimum boundary
            shouldBeValid = true;
          } else {
            threshold = 1.0; // Maximum boundary
            shouldBeValid = true;
          }
        }

        // Test validation method
        final isValid = storageService.isValidThreshold(threshold);
        expect(
          isValid,
          equals(shouldBeValid),
          reason: 'Test $testNum: Threshold $threshold should be '
              '${shouldBeValid ? "valid" : "invalid"}',
        );

        // Test save method - should throw for invalid values
        if (shouldBeValid) {
          // Should save successfully
          await expectLater(
            storageService.saveThreshold(threshold),
            completes,
            reason: 'Test $testNum: Valid threshold $threshold should save successfully',
          );

          // Verify it was saved correctly
          final loaded = await storageService.loadThreshold();
          expect(
            loaded,
            closeTo(threshold, 1e-10),
            reason: 'Test $testNum: Loaded threshold should match saved value',
          );
        } else {
          // Should throw ArgumentError
          await expectLater(
            storageService.saveThreshold(threshold),
            throwsA(isA<ArgumentError>()),
            reason: 'Test $testNum: Invalid threshold $threshold should throw ArgumentError',
          );
        }
      }
    });

    /// Test boundary values explicitly
    test('Property 16: Threshold boundary values', () async {
      // Test exact minimum (0.3) - should be valid
      expect(storageService.isValidThreshold(0.3), isTrue);
      await expectLater(
        storageService.saveThreshold(0.3),
        completes,
      );
      expect(await storageService.loadThreshold(), equals(0.3));

      // Test exact maximum (1.0) - should be valid
      expect(storageService.isValidThreshold(1.0), isTrue);
      await expectLater(
        storageService.saveThreshold(1.0),
        completes,
      );
      expect(await storageService.loadThreshold(), equals(1.0));

      // Test just below minimum (0.29999) - should be invalid
      expect(storageService.isValidThreshold(0.29999), isFalse);
      await expectLater(
        storageService.saveThreshold(0.29999),
        throwsA(isA<ArgumentError>()),
      );

      // Test just above maximum (1.00001) - should be invalid
      expect(storageService.isValidThreshold(1.00001), isFalse);
      await expectLater(
        storageService.saveThreshold(1.00001),
        throwsA(isA<ArgumentError>()),
      );

      // Test default value (0.6) - should be valid
      expect(storageService.isValidThreshold(0.6), isTrue);
      await expectLater(
        storageService.saveThreshold(0.6),
        completes,
      );
      expect(await storageService.loadThreshold(), equals(0.6));
    });

    /// Test that default threshold is returned when no value is saved
    test('Property 16: Default threshold when not set', () async {
      // Load without saving - should return default (0.6)
      final threshold = await storageService.loadThreshold();
      expect(threshold, equals(0.6));
      expect(storageService.isValidThreshold(threshold), isTrue);
    });

    /// Test that corrupted data returns default threshold
    test('Property 16: Corrupted data returns default', () async {
      // Manually set an invalid value in SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setDouble('face_threshold', 5.0); // Invalid value

      // Load should return default instead of invalid value
      final threshold = await storageService.loadThreshold();
      expect(threshold, equals(0.6));
      expect(storageService.isValidThreshold(threshold), isTrue);
    });

    /// Test threshold range properties
    test('Property 16: Threshold range properties', () {
      // Min should be less than max
      expect(storageService.minThreshold, lessThan(storageService.maxThreshold));

      // Default should be within range
      expect(storageService.defaultThreshold, greaterThanOrEqualTo(storageService.minThreshold));
      expect(storageService.defaultThreshold, lessThanOrEqualTo(storageService.maxThreshold));

      // Specific values
      expect(storageService.minThreshold, equals(0.3));
      expect(storageService.maxThreshold, equals(1.0));
      expect(storageService.defaultThreshold, equals(0.6));
    });

    /// Test that validation is consistent across multiple calls
    test('Property 16: Validation consistency', () {
      final random = Random(123);
      const int numTests = 50;

      for (int i = 0; i < numTests; i++) {
        final threshold = random.nextDouble() * 2.0; // [0.0, 2.0]
        
        // Call validation multiple times - should always return same result
        final result1 = storageService.isValidThreshold(threshold);
        final result2 = storageService.isValidThreshold(threshold);
        final result3 = storageService.isValidThreshold(threshold);

        expect(result1, equals(result2));
        expect(result2, equals(result3));

        // Result should match expected based on range
        final expected = threshold >= 0.3 && threshold <= 1.0;
        expect(result1, equals(expected));
      }
    });
  });
}
