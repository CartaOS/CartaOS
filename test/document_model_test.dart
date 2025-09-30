import 'package:flutter_test/flutter_test.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';

void main() {
  group('Document Model', () {
    final testDocument = Document(
      id: '1',
      title: 'Test Document',
      content: 'This is a test document content',
      summary: 'Summary of the test document',
      tags: const ['test', 'flutter'],
      keyConcepts: const ['concept1', 'concept2'],
      createdAt: DateTime(2023, 1, 1),
      processedAt: DateTime(2023, 1, 2),
      status: DocumentStatus.completed,
      filePath: '/path/to/file.pdf',
      pageCount: 10,
      fileType: DocumentFileType.native,
    );

    test('should create a document with all properties', () {
      expect(testDocument.id, '1');
      expect(testDocument.title, 'Test Document');
      expect(testDocument.content, 'This is a test document content');
      expect(testDocument.summary, 'Summary of the test document');
      expect(testDocument.tags, ['test', 'flutter']);
      expect(testDocument.keyConcepts, ['concept1', 'concept2']);
      expect(testDocument.createdAt, DateTime(2023, 1, 1));
      expect(testDocument.processedAt, DateTime(2023, 1, 2));
      expect(testDocument.status, DocumentStatus.completed);
      expect(testDocument.filePath, '/path/to/file.pdf');
      expect(testDocument.pageCount, 10);
      expect(testDocument.fileType, DocumentFileType.native);
    });

    test('should support value equality', () {
      expect(
        testDocument,
        equals(testDocument.copyWith()),
      );
    });

    test('should have the correct props', () {
      expect(testDocument.props, [
        '1',
        'Test Document',
        'This is a test document content',
        'Summary of the test document',
        ['test', 'flutter'],
        ['concept1', 'concept2'],
        DateTime(2023, 1, 1),
        DateTime(2023, 1, 2),
        DocumentStatus.completed,
        '/path/to/file.pdf',
        10,
        DocumentFileType.native,
      ]);
    });

    test('should create a copy with updated values', () {
      final updatedDocument = testDocument.copyWith(
        title: 'Updated Title',
        status: DocumentStatus.processing,
      );

      expect(updatedDocument.id, testDocument.id);
      expect(updatedDocument.title, 'Updated Title');
      expect(updatedDocument.status, DocumentStatus.processing);
      expect(updatedDocument.content, testDocument.content);
    });

    test('should serialize to and from JSON', () {
      final json = testDocument.toJson();
      final fromJson = Document.fromJson(json);

      expect(fromJson, equals(testDocument));
    });

    test('should create an example document', () {
      final document = Document.example();

      expect(document.id, '1');
      expect(document.title, 'Documento de Exemplo');
      expect(document.tags, ['importante', 'financeiro', 'legal']);
      expect(document.status, DocumentStatus.completed);
      expect(document.pageCount, 12);
      expect(document.fileType, DocumentFileType.native);
    });
  });
}
