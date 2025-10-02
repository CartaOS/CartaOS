import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:carta_os/src/features/auth/presentation/screens/login_screen.dart';

void main() {
  testWidgets('LoginScreen has a title, two text fields and a button',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(
      home: LoginScreen(),
    ));

    // Verify that our screen has a title.
    expect(find.text('Acesse sua conta'), findsOneWidget);

    // Verify that our screen has two text fields.
    expect(find.byKey(const Key('loginEmailField')), findsOneWidget);
    expect(find.byKey(const Key('loginPasswordField')), findsOneWidget);

    // Verify that our screen has a button.
    expect(find.byKey(const Key('loginButton')), findsOneWidget);
  });

  testWidgets('LoginScreen shows error messages for empty fields',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(
      home: LoginScreen(),
    ));

    await tester.tap(find.byKey(const Key('loginButton')));
    await tester.pump();

    // Verify that our error messages are shown.
    expect(find.text('Por favor, insira seu email'), findsOneWidget);
    expect(find.text('Por favor, insira sua senha'), findsOneWidget);
  });

  testWidgets('LoginScreen shows error message for invalid email',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(
      home: LoginScreen(),
    ));

    // Enter an invalid email.
    await tester.enterText(
        find.byKey(const Key('loginEmailField')), 'invalid-email');

    // Tap the button.
    await tester.tap(find.byKey(const Key('loginButton')));
    await tester.pump();

    // Verify that our error message is shown.
    expect(find.text('Por favor, insira um email válido'), findsOneWidget);
  });
}
