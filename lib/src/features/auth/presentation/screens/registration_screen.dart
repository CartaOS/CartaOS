import 'package:carta_os/src/features/auth/data/auth_service.dart';
import 'package:flutter/material.dart';
import 'package:carta_os/src/localization/app_localizations.dart'; // Added import

final _emailRegex = RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');

class RegistrationScreen extends StatefulWidget {
  const RegistrationScreen({super.key});

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _authService = AuthService();
  bool _isLoading = false;

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
                      if (!_emailRegex.hasMatch(value)) {
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
                  if (_isLoading)
                    const CircularProgressIndicator()
                  else
                    ElevatedButton(
                      key: const Key('registerButton'), // Added Key
                      onPressed: _register,
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

  void _register() async {
    if (_formKey.currentState?.validate() ?? false) {
      setState(() {
        _isLoading = true;
      });

      final success = await _authService.register(
        email: _emailController.text,
        password: _passwordController.text,
      );

      if (mounted) {
        setState(() {
          _isLoading = false;
        });

        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Registro realizado com sucesso!')),
          );
          Navigator.of(context).pushReplacementNamed('/home');
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Falha no registro. Tente novamente.')),
          );
        }
      }
    }
  }
}
