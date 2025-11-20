import 'package:flutter_test/flutter_test.dart';
import 'package:face_recognition_app/models/environment_info.dart';
import 'package:face_recognition_app/models/training_result.dart';
import 'package:face_recognition_app/models/verification_result.dart';
import 'package:face_recognition_app/models/face_detection_result.dart';

void main() {
  group('Model Serialization Tests', () {
    test('EnvironmentInfo toJson/fromJson round trip', () {
      final original = EnvironmentInfo(
        brightness: 150.0,
        isTooDark: false,
        isTooBright: false,
        blurScore: 120.0,
        isTooBlurry: false,
        faceSizeRatio: 0.25,
        isFaceTooSmall: false,
        warnings: ['Test warning'],
      );

      final json = original.toJson();
      final restored = EnvironmentInfo.fromJson(json);

      expect(restored.brightness, original.brightness);
      expect(restored.isTooDark, original.isTooDark);
      expect(restored.isTooBright, original.isTooBright);
      expect(restored.blurScore, original.blurScore);
      expect(restored.isTooBlurry, original.isTooBlurry);
      expect(restored.faceSizeRatio, original.faceSizeRatio);
      expect(restored.isFaceTooSmall, original.isFaceTooSmall);
      expect(restored.warnings, original.warnings);
    });

    test('TrainingResult toJson/fromJson round trip', () {
      final original = TrainingResult(
        success: true,
        numImages: 10,
        numEmbeddings: 10,
        errorMessage: null,
      );

      final json = original.toJson();
      final restored = TrainingResult.fromJson(json);

      expect(restored.success, original.success);
      expect(restored.numImages, original.numImages);
      expect(restored.numEmbeddings, original.numEmbeddings);
      expect(restored.errorMessage, original.errorMessage);
    });

    test('VerificationResult toJson/fromJson round trip', () {
      final envInfo = EnvironmentInfo(
        brightness: 150.0,
        isTooDark: false,
        isTooBright: false,
        blurScore: 120.0,
        isTooBlurry: false,
        faceSizeRatio: 0.25,
        isFaceTooSmall: false,
        warnings: [],
      );

      final original = VerificationResult(
        isMatch: true,
        distance: 0.5,
        threshold: 0.6,
        message: 'Khớp ✓',
        environmentInfo: envInfo,
      );

      final json = original.toJson();
      final restored = VerificationResult.fromJson(json);

      expect(restored.isMatch, original.isMatch);
      expect(restored.distance, original.distance);
      expect(restored.threshold, original.threshold);
      expect(restored.message, original.message);
      expect(restored.environmentInfo, isNotNull);
      expect(restored.environmentInfo!.brightness, envInfo.brightness);
    });

    test('FaceDetectionResult toJson/fromJson', () {
      final original = FaceDetectionResult(
        success: false,
        errorMessage: 'Test error',
        faceCount: 2,
      );

      final json = original.toJson();
      final restored = FaceDetectionResult.fromJson(json);

      expect(restored.success, original.success);
      expect(restored.errorMessage, original.errorMessage);
      expect(restored.faceCount, original.faceCount);
      expect(restored.face, isNull);
    });

    test('EnvironmentInfo computed properties', () {
      final withWarnings = EnvironmentInfo(
        brightness: 50.0,
        isTooDark: true,
        isTooBright: false,
        blurScore: 80.0,
        isTooBlurry: true,
        faceSizeRatio: 0.05,
        isFaceTooSmall: true,
        warnings: ['Too dark', 'Too blurry', 'Face too small'],
      );

      expect(withWarnings.hasWarnings, true);
      expect(withWarnings.isAcceptable, false);

      final noWarnings = EnvironmentInfo(
        brightness: 150.0,
        isTooDark: false,
        isTooBright: false,
        blurScore: 120.0,
        isTooBlurry: false,
        faceSizeRatio: 0.25,
        isFaceTooSmall: false,
        warnings: [],
      );

      expect(noWarnings.hasWarnings, false);
      expect(noWarnings.isAcceptable, true);
    });

    test('TrainingResult factory methods', () {
      final success = TrainingResult.successResult(
        numImages: 10,
        numEmbeddings: 10,
      );
      expect(success.success, true);
      expect(success.numImages, 10);
      expect(success.numEmbeddings, 10);

      final noImages = TrainingResult.noImages();
      expect(noImages.success, false);
      expect(noImages.numImages, 0);
      expect(noImages.errorMessage, isNotNull);

      final error = TrainingResult.error('Custom error', numImages: 5);
      expect(error.success, false);
      expect(error.numImages, 5);
      expect(error.errorMessage, 'Custom error');
    });

    test('VerificationResult factory methods', () {
      final match = VerificationResult.match(
        distance: 0.5,
        threshold: 0.6,
      );
      expect(match.isMatch, true);
      expect(match.message, 'Khớp ✓');

      final noMatch = VerificationResult.noMatch(
        distance: 0.8,
        threshold: 0.6,
      );
      expect(noMatch.isMatch, false);
      expect(noMatch.message, 'Không khớp ✗');

      final notTrained = VerificationResult.notTrained();
      expect(notTrained.isMatch, false);
      expect(notTrained.message, contains('Chưa huấn luyện'));
    });

    test('FaceDetectionResult factory methods', () {
      final noFace = FaceDetectionResult.noFace();
      expect(noFace.success, false);
      expect(noFace.faceCount, 0);
      expect(noFace.errorMessage, contains('Không phát hiện'));

      final multipleFaces = FaceDetectionResult.multipleFaces(3);
      expect(multipleFaces.success, false);
      expect(multipleFaces.faceCount, 3);
      expect(multipleFaces.errorMessage, contains('nhiều khuôn mặt'));

      final error = FaceDetectionResult.error('Custom error', 0);
      expect(error.success, false);
      expect(error.errorMessage, 'Custom error');
    });
  });
}
