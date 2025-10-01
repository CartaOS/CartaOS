import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:carta_os/src/features/auth/presentation/screens/login_screen.dart';
import 'package:carta_os/src/features/auth/presentation/screens/registration_screen.dart';
import 'package:carta_os/src/features/document/presentation/screens/home_screen.dart';
import 'package:carta_os/src/localization/app_localizations.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CartaOS',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en', ''),
        Locale('pt', ''),
        Locale('pt', 'BR'), // Explicitly support pt-BR
      ],
      locale: const Locale('pt', 'BR'), // Set pt-BR as default
      initialRoute: '/',
      routes: {
        '/': (context) => const LoginScreen(),
        '/home': (context) => const HomeScreen(),
        '/register': (context) => const RegistrationScreen(),
      },
    );
  }
}