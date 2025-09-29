import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:carta_os/src/features/auth/presentation/screens/registration_screen.dart';

void main() {
  testWidgets('RegistrationScreen has a title, two text fields and a button',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(
      home: RegistrationScreen(),
    ));

    // Verify that our screen has a title.
    expect(find.text('Crie sua conta'), findsOneWidget);

    // Verify that our screen has two text fields.
    expect(find.byType(TextFormField), findsNWidgets(2));

    // Verify that our screen has a button.
    expect(find.byType(ElevatedButton), findsOneWidget);
  });

  testWidgets('RegistrationScreen shows error messages for empty fields',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(
      home: RegistrationScreen(),
    ));

    // Tap the button without entering any text.
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    // Verify that our error messages are shown.
    expect(find.text('Por favor, insira seu email'), findsOneWidget);
    expect(find.text('Por favor, insira sua senha'), findsOneWidget);
  });

  testWidgets('RegistrationScreen shows error message for invalid email',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(
      home: RegistrationScreen(),
    ));

    // Enter an invalid email.
    await tester.enterText(find.byType(TextFormField).first, 'invalid-email');

    // Tap the button.
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    // Verify that our error message is shown.
    expect(find.text('Por favor, insira um email válido'), findsOneWidget);
  });

  testWidgets('RegistrationScreen shows error message for short password',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(
      home: RegistrationScreen(),
    ));

    // Enter a short password.
    await tester.enterText(find.byType(TextFormField).last, '123');

    // Tap the button.
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    // Verify that our error message is shown.
    expect(find.text('A senha deve ter pelo menos 6 caracteres'), findsOneWidget);
  });
}
