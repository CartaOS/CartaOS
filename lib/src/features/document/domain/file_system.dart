import 'dart:io';

abstract class FileSystem {
  Future<bool> fileExists(String path);
  Future<void> copyFile(String source, String destination);
  Future<void> writeFile(String path, String content);
}

class DefaultFileSystem implements FileSystem {
  const DefaultFileSystem();

  @override
  Future<bool> fileExists(String path) => File(path).exists();

  @override
  Future<void> copyFile(String source, String destination) async {
    await File(source).copy(destination);
  }

  @override
  Future<void> writeFile(String path, String content) async {
    await File(path).writeAsString(content);
  }
}
