import 'package:flutter_test/flutter_test.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';

void main() {
  group('Document Model', () {
    test('should create a document with all properties', () {
      final document = Document(
        id: '1',
        title: 'Test Document',
        content: 'This is a test document content',
        summary: 'Summary of the test document',
        tags: ['test', 'flutter'],
        createdAt: DateTime(2023, 1, 1),
        processedAt: DateTime(2023, 1, 2),
        status: DocumentStatus.completed,
        filePath: '/path/to/file.pdf',
        pageCount: 10,
        fileType: DocumentFileType.native,
      );

      expect(document.id, '1');
      expect(document.title, 'Test Document');
      expect(document.content, 'This is a test document content');
      expect(document.summary, 'Summary of the test document');
      expect(document.tags, ['test', 'flutter']);
      expect(document.createdAt, DateTime(2023, 1, 1));
      expect(document.processedAt, DateTime(2023, 1, 2));
      expect(document.status, DocumentStatus.completed);
      expect(document.filePath, '/path/to/file.pdf');
      expect(document.pageCount, 10);
      expect(document.fileType, DocumentFileType.native);
    });

    test('should create an example document', () {
      final document = Document.example();

      expect(document.id, '1');
      expect(document.title, 'Documento de Exemplo');
      expect(document.tags, ['contrato', 'importante', 'financeiro']);
      expect(document.status, DocumentStatus.completed);
      expect(document.pageCount, 12);
      expect(document.fileType, DocumentFileType.native);
    });
  });
}