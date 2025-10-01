class AuthService {
  Future<bool> login({required String email, required String password}) async {
    await Future.delayed(const Duration(seconds: 2)); // Simulate network delay

    if (password == 'wrong') {
      return false; // Simulate wrong credentials
    }
    return true; // Simulate successful login
  }

  Future<bool> register({required String email, required String password}) async {
    await Future.delayed(const Duration(seconds: 2)); // Simulate network delay

    // Simulate a case where registration might fail, for example, if the email is already in use.
    if (email.contains('fail')) {
      return false;
    }

    return true; // Simulate successful registration
  }
}
