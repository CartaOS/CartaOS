import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:carta_os/src/features/auth/presentation/screens/registration_screen.dart';
import 'package:carta_os/src/localization/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

void main() {
  Widget createWidgetForTesting({required Widget child}) {
    return MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('pt', ''),
      ],
      home: child,
    );
  }

  testWidgets('RegistrationScreen has a title, two text fields and a button',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester
        .pumpWidget(createWidgetForTesting(child: const RegistrationScreen()));
    final l10n = AppLocalizations(const Locale('pt'));

    // Verify that our screen has a title.
    expect(find.text(l10n.registrationScreenHeadline), findsOneWidget);

    // Verify that our screen has two text fields.
    expect(find.byType(TextFormField), findsNWidgets(2));

    // Verify that our screen has a button.
    expect(find.byType(ElevatedButton), findsOneWidget);
  });

  testWidgets('RegistrationScreen shows error messages for empty fields',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester
        .pumpWidget(createWidgetForTesting(child: const RegistrationScreen()));
    final l10n = AppLocalizations(const Locale('pt'));

    // Tap the button without entering any text.
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    // Verify that our error messages are shown.
    expect(find.text(l10n.emailRequiredError), findsOneWidget);
    expect(find.text(l10n.passwordRequiredError), findsOneWidget);
  });

  testWidgets('RegistrationScreen shows error message for invalid email',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester
        .pumpWidget(createWidgetForTesting(child: const RegistrationScreen()));
    final l10n = AppLocalizations(const Locale('pt'));

    // Enter an invalid email.
    await tester.enterText(find.byType(TextFormField).first, 'invalid-email');

    // Tap the button.
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    // Verify that our error message is shown.
    expect(find.text(l10n.invalidEmailError), findsOneWidget);
  });

  testWidgets('RegistrationScreen shows error message for short password',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester
        .pumpWidget(createWidgetForTesting(child: const RegistrationScreen()));
    final l10n = AppLocalizations(const Locale('pt'));

    // Enter a short password.
    await tester.enterText(find.byType(TextFormField).last, '123');

    // Tap the button.
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    // Verify that our error message is shown.
    expect(find.text(l10n.passwordLengthError), findsOneWidget);
  });
}