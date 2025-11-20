import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:faceid_mobile/widgets/permission_dialog.dart';

/// Widget tests for PermissionDialog
/// Tests dialog display and user interactions
/// Requirements: 10.3, 10.4, 10.5
void main() {
  group('PermissionDialog', () {
    late PermissionDialog permissionDialog;

    setUp(() {
      permissionDialog = PermissionDialog();
    });

    testWidgets('showPermissionDeniedDialog displays correct message', (tester) async {
      // Requirement 10.4: Handle permission denied cases
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () {
                  permissionDialog.showPermissionDeniedDialog(
                    context,
                    'Test permission denied message',
                  );
                },
                child: const Text('Show Dialog'),
              );
            },
          ),
        ),
      );

      // Tap button to show dialog
      await tester.tap(find.text('Show Dialog'));
      await tester.pumpAndSettle();

      // Verify dialog is shown
      expect(find.text('Quyền bị từ chối'), findsOneWidget);
      expect(find.text('Test permission denied message'), findsOneWidget);
      expect(find.text('Đóng'), findsOneWidget);
    });

    testWidgets('showPermanentlyDeniedDialog displays settings option', (tester) async {
      // Requirement 10.5: Provide link to app settings if permission permanently denied
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () {
                  permissionDialog.showPermanentlyDeniedDialog(context);
                },
                child: const Text('Show Dialog'),
              );
            },
          ),
        ),
      );

      // Tap button to show dialog
      await tester.tap(find.text('Show Dialog'));
      await tester.pumpAndSettle();

      // Verify dialog is shown with settings option
      expect(find.text('Cần cấp quyền'), findsOneWidget);
      expect(find.text('Hủy'), findsOneWidget);
      expect(find.text('Mở Cài đặt'), findsOneWidget);
    });

    testWidgets('permission denied dialog can be dismissed', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () {
                  permissionDialog.showPermissionDeniedDialog(
                    context,
                    'Test message',
                  );
                },
                child: const Text('Show Dialog'),
              );
            },
          ),
        ),
      );

      // Show dialog
      await tester.tap(find.text('Show Dialog'));
      await tester.pumpAndSettle();

      // Tap close button
      await tester.tap(find.text('Đóng'));
      await tester.pumpAndSettle();

      // Verify dialog is dismissed
      expect(find.text('Quyền bị từ chối'), findsNothing);
    });

    testWidgets('permanently denied dialog can be cancelled', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () {
                  permissionDialog.showPermanentlyDeniedDialog(context);
                },
                child: const Text('Show Dialog'),
              );
            },
          ),
        ),
      );

      // Show dialog
      await tester.tap(find.text('Show Dialog'));
      await tester.pumpAndSettle();

      // Tap cancel button
      await tester.tap(find.text('Hủy'));
      await tester.pumpAndSettle();

      // Verify dialog is dismissed
      expect(find.text('Cần cấp quyền'), findsNothing);
    });
  });
}
