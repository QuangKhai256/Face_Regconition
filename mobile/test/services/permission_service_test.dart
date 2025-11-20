import 'package:flutter_test/flutter_test.dart';
import 'package:faceid_mobile/services/permission_service.dart';

/// Unit tests for PermissionService
/// Tests permission handling logic
/// Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
void main() {
  group('PermissionService', () {
    late PermissionService permissionService;

    setUp(() {
      permissionService = PermissionService();
    });

    group('Permission Rationale Messages', () {
      test('getCameraPermissionRationale returns Vietnamese message', () {
        // Requirement 10.3: Show permission rationale dialogs
        final message = permissionService.getCameraPermissionRationale();
        
        expect(message, isNotEmpty);
        expect(message, contains('camera'));
        expect(message, contains('khuôn mặt'));
      });

      test('getStoragePermissionRationale returns Vietnamese message', () {
        // Requirement 10.3: Show permission rationale dialogs
        final message = permissionService.getStoragePermissionRationale();
        
        expect(message, isNotEmpty);
        expect(message, contains('lưu trữ'));
        expect(message, contains('ảnh'));
      });
    });

    group('Permission Denied Messages', () {
      test('getCameraPermissionDeniedMessage returns Vietnamese message', () {
        // Requirement 10.4: Handle permission denied cases
        final message = permissionService.getCameraPermissionDeniedMessage();
        
        expect(message, isNotEmpty);
        expect(message, contains('camera'));
        expect(message, contains('cài đặt'));
      });

      test('getStoragePermissionDeniedMessage returns Vietnamese message', () {
        // Requirement 10.4: Handle permission denied cases
        final message = permissionService.getStoragePermissionDeniedMessage();
        
        expect(message, isNotEmpty);
        expect(message, contains('lưu'));
        expect(message, contains('cài đặt'));
      });
    });

    group('Settings Redirect Message', () {
      test('getSettingsRedirectMessage returns Vietnamese message', () {
        // Requirement 10.5: Provide link to app settings if permission permanently denied
        final message = permissionService.getSettingsRedirectMessage();
        
        expect(message, isNotEmpty);
        expect(message, contains('Cài đặt'));
        expect(message, contains('quyền'));
      });
    });

    group('Message Content Validation', () {
      test('all messages are in Vietnamese', () {
        final messages = [
          permissionService.getCameraPermissionRationale(),
          permissionService.getStoragePermissionRationale(),
          permissionService.getCameraPermissionDeniedMessage(),
          permissionService.getStoragePermissionDeniedMessage(),
          permissionService.getSettingsRedirectMessage(),
        ];

        for (final message in messages) {
          expect(message, isNotEmpty);
          // Check for Vietnamese characters or common Vietnamese words
          final hasVietnamese = message.contains(RegExp(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]')) ||
              message.contains('camera') ||
              message.contains('ảnh') ||
              message.contains('quyền') ||
              message.contains('cài đặt');
          expect(hasVietnamese, isTrue, reason: 'Message should be in Vietnamese: $message');
        }
      });

      test('camera messages mention camera', () {
        expect(
          permissionService.getCameraPermissionRationale().toLowerCase(),
          contains('camera'),
        );
        expect(
          permissionService.getCameraPermissionDeniedMessage().toLowerCase(),
          contains('camera'),
        );
      });

      test('storage messages mention storage or saving', () {
        final rationaleMessage = permissionService.getStoragePermissionRationale().toLowerCase();
        final deniedMessage = permissionService.getStoragePermissionDeniedMessage().toLowerCase();
        
        expect(
          rationaleMessage.contains('lưu') || rationaleMessage.contains('storage'),
          isTrue,
        );
        expect(
          deniedMessage.contains('lưu') || deniedMessage.contains('storage'),
          isTrue,
        );
      });
    });
  });
}
