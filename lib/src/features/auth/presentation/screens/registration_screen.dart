import 'package:flutter/material.dart';
import 'package:carta_os/src/localization/app_localizations.dart'; // Added import

class RegistrationScreen extends StatefulWidget {
  const RegistrationScreen({super.key});

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!; // Added l10n
    return Scaffold(
      appBar: AppBar(title: Text(l10n.registrationScreenTitle)), // Used l10n
      body: Center(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    l10n.registrationScreenHeadline, // Used l10n
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 32.0),
                  TextFormField(
                    key: const Key('registrationEmailField'), // Added Key
                    controller: _emailController,
                    decoration: InputDecoration( // Changed to InputDecoration
                      labelText: l10n.emailLabel, // Used l10n
                      border: const OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return l10n.emailRequiredError; // Used l10n
                      }
                      // Using a more robust email regex
                      final emailRegex = RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');
                      if (!emailRegex.hasMatch(value)) {
                        return l10n.invalidEmailError; // Used l10n
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16.0),
                  TextFormField(
                    key: const Key('registrationPasswordField'), // Added Key
                    controller: _passwordController,
                    obscureText: true,
                    decoration: InputDecoration( // Changed to InputDecoration
                      labelText: l10n.passwordLabel, // Used l10n
                      border: const OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return l10n.passwordRequiredError; // Used l10n
                      }
                      if (value.length < 6) {
                        return l10n.passwordLengthError; // Used l10n
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 32.0),
                  ElevatedButton(
                    key: const Key('registerButton'), // Added Key
                    onPressed: () {
                      if (_formKey.currentState!.validate()) {
                        // TODO: Implement actual registration logic
                        // ignore: avoid_print
                        print('Email: ${_emailController.text}');
                        // ignore: avoid_print
                        print('Senha: ${_passwordController.text}');
                      }
                    },
                    child: Text(l10n.registerButtonLabel), // Used l10n
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
