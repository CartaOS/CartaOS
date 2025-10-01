import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:carta_os/src/features/auth/presentation/screens/registration_screen.dart';
import 'package:carta_os/src/localization/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

void main() {
  testWidgets('RegistrationScreen has a title, two text fields and a button',
      (WidgetTester tester) async {
    await tester.pumpWidget(createWidgetForTesting(child: const RegistrationScreen()));
    final BuildContext context = tester.element(find.byType(RegistrationScreen));
    final l10n = AppLocalizations.of(context)!;

    // Verify that our screen has a title.
    expect(find.text(l10n.registrationScreenHeadline), findsOneWidget);

    // Verify that our screen has two text fields.
    expect(find.byKey(const Key('registrationEmailField')), findsOneWidget);
    expect(find.byKey(const Key('registrationPasswordField')), findsOneWidget);

    // Verify that our screen has a button.
    expect(find.byKey(const Key('registerButton')), findsOneWidget);
  });

  testWidgets('RegistrationScreen shows error messages for empty fields',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(createWidgetForTesting(child: const RegistrationScreen()));
    final BuildContext context = tester.element(find.byType(RegistrationScreen));
    final l10n = AppLocalizations.of(context)!;

    await tester.tap(find.byKey(const Key('registerButton')));
    await tester.pump();

    // Verify that our error messages are shown.
    expect(find.text(l10n.emailRequiredError), findsOneWidget);
    expect(find.text(l10n.passwordRequiredError), findsOneWidget);
  });

  testWidgets('RegistrationScreen shows error message for invalid email',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(createWidgetForTesting(child: const RegistrationScreen()));
    final BuildContext context = tester.element(find.byType(RegistrationScreen));
    final l10n = AppLocalizations.of(context)!;

    // Enter an invalid email.
    await tester.enterText(
        find.byKey(const Key('registrationEmailField')), 'invalid-email');

    // Tap the button.
    await tester.tap(find.byKey(const Key('registerButton')));
    await tester.pump();

    // Verify that our error message is shown.
    expect(find.text(l10n.invalidEmailError), findsOneWidget);
  });

  testWidgets('RegistrationScreen shows error message for short password',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(createWidgetForTesting(child: const RegistrationScreen()));
    final BuildContext context = tester.element(find.byType(RegistrationScreen));
    final l10n = AppLocalizations.of(context)!;

    // Enter a short password.
    await tester.enterText(find.byKey(const Key('registrationPasswordField')), '123');

    // Tap the button.
    await tester.tap(find.byKey(const Key('registerButton')));
    await tester.pump();

    // Verify that our error message is shown.
    expect(find.text(l10n.passwordLengthError), findsOneWidget);
  });
}

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
