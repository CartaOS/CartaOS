class ExportException implements Exception {
  final String message;
  final String? details;

  ExportException(this.message, {this.details});

  @override
  String toString() {
    return 'ExportException: $message' + (details != null ? ' ($details)' : '');
  }
}
