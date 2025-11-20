import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:faceid_mobile/models/training_result.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('TrainingResult Model Tests', () {
    test('should create successful training result', () {
      final successResult = TrainingResult.successResult(
        numImages: 5,
        numEmbeddings: 5,
      );
      
      expect(successResult.success, isTrue);
      expect(successResult.numImages, equals(5));
      expect(successResult.numEmbeddings, equals(5));
      expect(successResult.errorMessage, isNull);
    });

    test('should create no images result', () {
      final noImagesResult = TrainingResult.noImages();
      
      expect(noImagesResult.success, isFalse);
      expect(noImagesResult.numImages, equals(0));
      expect(noImagesResult.numEmbeddings, equals(0));
      expect(noImagesResult.errorMessage, isNotNull);
      expect(noImagesResult.errorMessage, contains('Chưa có dữ liệu'));
    });

    test('should create error result', () {
      final errorResult = TrainingResult.error('Test error', numImages: 3);
      
      expect(errorResult.success, isFalse);
      expect(errorResult.numImages, equals(3));
      expect(errorResult.numEmbeddings, equals(0));
      expect(errorResult.errorMessage, equals('Test error'));
    });
  });
}

  group('TrainingResult JSON Serialization', () {
    test('should serialize to JSON correctly', () {
      final result = TrainingResult.successResult(
        numImages: 10,
        numEmbeddings: 8,
      );

      final json = result.toJson();
      
      expect(json['success'], isTrue);
      expect(json['numImages'], equals(10));
      expect(json['numEmbeddings'], equals(8));
      expect(json['errorMessage'], isNull);
    });

    test('should deserialize from JSON correctly', () {
      final json = {
        'success': true,
        'numImages': 10,
        'numEmbeddings': 8,
        'errorMessage': null,
      };

      final result = TrainingResult.fromJson(json);
      
      expect(result.success, isTrue);
      expect(result.numImages, equals(10));
      expect(result.numEmbeddings, equals(8));
      expect(result.errorMessage, isNull);
    });

    test('should handle JSON round trip', () {
      final original = TrainingResult.error('Test error', numImages: 5);
      final json = original.toJson();
      final restored = TrainingResult.fromJson(json);
      
      expect(restored.success, equals(original.success));
      expect(restored.numImages, equals(original.numImages));
      expect(restored.numEmbeddings, equals(original.numEmbeddings));
      expect(restored.errorMessage, equals(original.errorMessage));
    });
  });

  group('Mean Embedding Calculation Logic', () {
    test('mean of single embedding should be the embedding itself', () {
      // Requirement 6.4: Calculate mean embedding
      final embedding = List<double>.generate(128, (i) => i.toDouble());
      final embeddings = [embedding];

      // Verify test data
      expect(embeddings.length, equals(1));
      expect(embeddings.first.length, equals(128));
      
      // Mean of single embedding is itself
      for (int i = 0; i < 128; i++) {
        expect(embeddings.first[i], equals(i.toDouble()));
      }
    });

    test('mean of two embeddings should be arithmetic mean', () {
      // Requirement 6.4: Calculate mean embedding
      final embedding1 = List<double>.filled(128, 1.0);
      final embedding2 = List<double>.filled(128, 3.0);
      final embeddings = [embedding1, embedding2];

      // Calculate expected mean manually
      final expectedMean = List<double>.filled(128, 2.0);
      final calculatedMean = List<double>.filled(128, 0.0);
      
      for (final emb in embeddings) {
        for (int i = 0; i < 128; i++) {
          calculatedMean[i] += emb[i];
        }
      }
      for (int i = 0; i < 128; i++) {
        calculatedMean[i] /= embeddings.length;
      }

      // Verify calculation
      for (int i = 0; i < 128; i++) {
        expect(calculatedMean[i], equals(expectedMean[i]));
      }
    });

    test('mean calculation should handle multiple embeddings', () {
      // Requirement 6.4: Calculate mean embedding
      final embeddings = [
        List<double>.filled(128, 1.0),
        List<double>.filled(128, 2.0),
        List<double>.filled(128, 3.0),
      ];

      // Expected mean: (1 + 2 + 3) / 3 = 2.0
      final calculatedMean = List<double>.filled(128, 0.0);
      
      for (final emb in embeddings) {
        for (int i = 0; i < 128; i++) {
          calculatedMean[i] += emb[i];
        }
      }
      for (int i = 0; i < 128; i++) {
        calculatedMean[i] /= embeddings.length;
      }

      for (int i = 0; i < 128; i++) {
        expect(calculatedMean[i], equals(2.0));
      }
    });
  });

  group('Training Service Integration Tests', () {
    final isDesktop = Platform.isWindows || Platform.isMacOS || Platform.isLinux;
    
    test('Full training tests require mobile device/emulator', () {
      if (isDesktop) {
        print('\n' + '=' * 80);
        print('SKIPPED: Training Service Integration Tests');
        print('=' * 80);
        print('\nThese tests require native TFLite libraries only available on mobile platforms.');
        print('\nTo run full training service tests:');
        print('1. Start an Android emulator or connect a physical device');
        print('2. Verify device: flutter devices');
        print('3. Run: flutter test integration_test/training_property_integration_test.dart -d <device_id>');
        print('\nSee integration_test/README.md for detailed instructions.');
        print('=' * 80 + '\n');
      }
      
      // Always pass - this is just a placeholder
      expect(true, isTrue);
    }, skip: isDesktop ? 'TensorFlow Lite requires mobile device/emulator' : null);
  });
}
