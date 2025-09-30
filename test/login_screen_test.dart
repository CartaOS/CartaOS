import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:carta_os/src/features/auth/presentation/screens/login_screen.dart';
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

  testWidgets('LoginScreen has a title, two text fields and a button',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(createWidgetForTesting(child: const LoginScreen()));
    final l10n = AppLocalizations(const Locale('pt'));

    // Verify that our screen has a title.
    expect(find.text(l10n.loginScreenHeadline), findsOneWidget);

    // Verify that our screen has two text fields.
    expect(find.byKey(const Key('loginEmailField')), findsOneWidget);
    expect(find.byKey(const Key('loginPasswordField')), findsOneWidget);

    // Verify that our screen has a button.
    expect(find.byKey(const Key('loginButton')), findsOneWidget);
  });

  testWidgets('LoginScreen shows error messages for empty fields',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(createWidgetForTesting(child: const LoginScreen()));
    final l10n = AppLocalizations(const Locale('pt'));

    await tester.tap(find.byKey(const Key('loginButton')));
    await tester.pump();

    // Verify that our error messages are shown.
    expect(find.text(l10n.emailRequiredError), findsOneWidget);
    expect(find.text(l10n.passwordRequiredError), findsOneWidget);
  });

  testWidgets('LoginScreen shows error message for invalid email',
      (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(createWidgetForTesting(child: const LoginScreen()));
    final l10n = AppLocalizations(const Locale('pt'));

    // Enter an invalid email.
    await tester.enterText(
        find.byKey(const Key('loginEmailField')), 'invalid-email');

    // Tap the button.
    await tester.tap(find.byKey(const Key('loginButton')));
    await tester.pump();

    // Verify that our error message is shown.
    expect(find.text(l10n.invalidEmailError), findsOneWidget);
  });
}
