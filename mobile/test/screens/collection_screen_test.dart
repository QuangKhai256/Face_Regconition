import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:faceid_mobile/screens/collection_screen.dart';

/// Basic widget tests for CollectionScreen
/// These tests verify that the screen can be instantiated and basic UI elements exist
void main() {
  group('CollectionScreen Widget Tests', () {
    testWidgets('CollectionScreen can be instantiated', (WidgetTester tester) async {
      // Build the widget
      await tester.pumpWidget(
        const MaterialApp(
          home: CollectionScreen(),
        ),
      );

      // Verify the screen renders
      expect(find.byType(CollectionScreen), findsOneWidget);
    });

    testWidgets('CollectionScreen shows app bar with title', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: CollectionScreen(),
        ),
      );

      // Wait for initialization
      await tester.pump();

      // Verify app bar exists with title
      expect(find.text('Thu thập ảnh'), findsOneWidget);
    });

    testWidgets('CollectionScreen shows image counter in app bar', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: CollectionScreen(),
        ),
      );

      // Wait for initialization
      await tester.pump();

      // Verify image counter exists (should show "0 ảnh" initially)
      expect(find.text('0 ảnh'), findsOneWidget);
    });

    testWidgets('CollectionScreen shows loading indicator during initialization', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: CollectionScreen(),
        ),
      );

      // Should show loading indicator initially
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });
  });
}
