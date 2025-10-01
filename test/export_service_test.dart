import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:path/path.dart' as p;
import 'package:carta_os/src/features/document/domain/export_service.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';
import 'package:carta_os/src/features/document/domain/exceptions/export_exception.dart';
import 'package:carta_os/src/features/document/domain/file_system.dart';

import 'export_service_test.mocks.dart';

@GenerateMocks([FileSystem])
void main() {
  group('ExportService', () {
    late ExportService exportService;
    late Document mockDocument;
    late MockFileSystem mockFileSystem;

    setUp(() {
      mockFileSystem = MockFileSystem();
      exportService = ExportService(fileSystem: mockFileSystem);

      mockDocument = Document(
        id: 'test-id',
        title: 'Test Document',
        content: 'This is some test content.',
        summary: 'Test summary.',
        tags: ['tag1', 'tag2'],
        createdAt: DateTime(2023, 1, 1),
        processedAt: DateTime(2023, 1, 2),
        status: DocumentStatus.completed,
        filePath: '/path/to/original/test_document.pdf',
        pageCount: 10,
        fileType: DocumentFileType.native,
      );

      when(mockFileSystem.fileExists(any)).thenAnswer((_) async => true);
      when(mockFileSystem.copyFile(any, any)).thenAnswer((_) async {});
      when(mockFileSystem.writeFile(any, any)).thenAnswer((_) async {});
    });

    test('should export document successfully', () async {
      final String targetDirectory = '/path/to/export';

      await exportService.exportDocument(
        document: mockDocument,
        targetDirectory: targetDirectory,
        idLabel: 'ID',
        createdAtLabel: 'Created',
        processedAtLabel: 'Processed',
        statusLabel: 'Status',
        fileTypeLabel: 'Type',
        pagesLabel: 'Pages',
        summaryLabel: 'Summary',
        tagsLabel: 'Tags',
        pendingProcessingLabel: 'Pending',
        unknownLabel: 'Unknown',
        notApplicableLabel: 'N/A',
      );

      verify(mockFileSystem.fileExists(mockDocument.filePath)).called(1);
      final expectedPdfPath = p.join(targetDirectory, 'Test_Document.pdf');
      final expectedMarkdownPath = p.join(targetDirectory, 'Test_Document.md');
      verify(mockFileSystem.copyFile(mockDocument.filePath, expectedPdfPath)).called(1);
      verify(mockFileSystem.writeFile(expectedMarkdownPath, any)).called(1);
    });

    test('should throw ExportException if original PDF does not exist', () async {
      when(mockFileSystem.fileExists(any)).thenAnswer((_) async => false);

      final String targetDirectory = '/path/to/export';

      expect(
        () => exportService.exportDocument(
          document: mockDocument,
          targetDirectory: targetDirectory,
          idLabel: 'ID',
          createdAtLabel: 'Created',
          processedAtLabel: 'Processed',
          statusLabel: 'Status',
          fileTypeLabel: 'Type',
          pagesLabel: 'Pages',
          summaryLabel: 'Summary',
          tagsLabel: 'Tags',
          pendingProcessingLabel: 'Pending',
          unknownLabel: 'Unknown',
          notApplicableLabel: 'N/A',
        ),
        throwsA(isA<ExportException>()),
      );
    });

    test('should use fallback filename if sanitized title is empty', () async {
      mockDocument = Document(
        id: 'test-id',
        title: '!!!',
        content: 'This is some test content.',
        summary: 'Test summary.',
        tags: ['tag1', 'tag2'],
        createdAt: DateTime(2023, 1, 1),
        processedAt: DateTime(2023, 1, 2),
        status: DocumentStatus.completed,
        filePath: '/path/to/original/test_document.pdf',
        pageCount: 10,
        fileType: DocumentFileType.native,
      );

      final String targetDirectory = '/path/to/export';

      await exportService.exportDocument(
        document: mockDocument,
        targetDirectory: targetDirectory,
        idLabel: 'ID',
        createdAtLabel: 'Created',
        processedAtLabel: 'Processed',
        statusLabel: 'Status',
        fileTypeLabel: 'Type',
        pagesLabel: 'Pages',
        summaryLabel: 'Summary',
        tagsLabel: 'Tags',
        pendingProcessingLabel: 'Pending',
        unknownLabel: 'Unknown',
        notApplicableLabel: 'N/A',
      );

      final expectedPdfPath = p.join(targetDirectory, 'document_test-id.pdf');
      verify(mockFileSystem.copyFile(mockDocument.filePath, expectedPdfPath)).called(1);
    });

    test('should correctly format tags in Markdown content', () async {
      final String targetDirectory = '/path/to/export';

      await exportService.exportDocument(
        document: mockDocument,
        targetDirectory: targetDirectory,
        idLabel: 'ID',
        createdAtLabel: 'Created',
        processedAtLabel: 'Processed',
        statusLabel: 'Status',
        fileTypeLabel: 'Type',
        pagesLabel: 'Pages',
        summaryLabel: 'Summary',
        tagsLabel: 'Tags',
        pendingProcessingLabel: 'Pending',
        unknownLabel: 'Unknown',
        notApplicableLabel: 'N/A',
      );

      final capturedMarkdownContent = verify(mockFileSystem.writeFile(any, captureAny)).captured.single as String;
      expect(capturedMarkdownContent, contains('## Tags'));
      expect(capturedMarkdownContent, contains('- tag1'));
      expect(capturedMarkdownContent, contains('- tag2'));
    });
  });
}
