import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:faceid_mobile/screens/verification_screen.dart';

/// Basic widget tests for VerificationScreen
/// These tests verify that the screen can be instantiated and basic UI elements exist
void main() {
  group('VerificationScreen Widget Tests', () {
    testWidgets('VerificationScreen can be instantiated', (WidgetTester tester) async {
      // Build the widget
      await tester.pumpWidget(
        const MaterialApp(
          home: VerificationScreen(),
        ),
      );

      // Verify the screen renders
      expect(find.byType(VerificationScreen), findsOneWidget);
    });

    testWidgets('VerificationScreen shows app bar with title', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: VerificationScreen(),
        ),
      );

      // Wait for initialization
      await tester.pump();

      // Verify app bar exists with title
      expect(find.text('Nhận diện'), findsOneWidget);
    });

    testWidgets('VerificationScreen shows loading indicator during initialization', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: VerificationScreen(),
        ),
      );

      // Should show loading indicator initially
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('VerificationScreen has correct structure', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: VerificationScreen(),
        ),
      );

      // Wait a bit for initialization
      await tester.pump(const Duration(milliseconds: 100));

      // Verify the screen has a Scaffold
      expect(find.byType(Scaffold), findsOneWidget);
      
      // Verify app bar with title exists
      expect(find.text('Nhận diện'), findsOneWidget);
    });
  });
}
