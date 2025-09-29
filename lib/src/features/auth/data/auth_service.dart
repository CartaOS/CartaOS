class AuthService {
  Future<bool> login({required String email, required String password}) async {
    await Future.delayed(const Duration(seconds: 2)); // Simulate network delay

    if (password == 'wrong') {
      return false; // Simulate wrong credentials
    }
    return true; // Simulate successful login
  }
}
