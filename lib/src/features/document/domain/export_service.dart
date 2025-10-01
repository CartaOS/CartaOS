import 'dart:developer';
import 'package:intl/intl.dart';
import 'package:path/path.dart' as p;
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';
import 'package:carta_os/src/features/document/domain/exceptions/export_exception.dart';
import 'file_system.dart';

class ExportService {
  final FileSystem fileSystem;

  ExportService({this.fileSystem = const DefaultFileSystem()});

  Future<void> exportDocument({
    required Document document,
    required String targetDirectory,
    required String idLabel,
    required String createdAtLabel,
    required String processedAtLabel,
    required String statusLabel,
    required String fileTypeLabel,
    required String pagesLabel,
    required String summaryLabel,
    required String tagsLabel,
    required String pendingProcessingLabel,
    required String unknownLabel,
    required String notApplicableLabel,
  }) async {
    try {
      String safeTitle = document.title
          .replaceAll(RegExp(r'[\s/\\?%*:|"<>]+'), '_')
          .replaceAll(RegExp(r'[^\w.-]+'), '');

      if (safeTitle.isEmpty) {
        safeTitle = 'document_${document.id}';
      }

      if (!await fileSystem.fileExists(document.filePath)) {
        log('Original PDF file not found: ${document.filePath}', name: 'ExportService');
        throw ExportException('Original PDF file not found', details: document.filePath);
      }

      final pdfFileName = '${safeTitle}.pdf';
      final markdownFileName = '${safeTitle}.md';
      final newPdfFilePath = p.join(targetDirectory, pdfFileName);
      final markdownFilePath = p.join(targetDirectory, markdownFileName);

      final String markdownContent = '''
# ${document.title}

**$idLabel:** ${document.id}
**$createdAtLabel:** ${DateFormat('dd/MM/yyyy').format(document.createdAt)}
**$processedAtLabel:** ${document.processedAt != null ? DateFormat('dd/MM/yyyy').format(document.processedAt!) : pendingProcessingLabel}
**$statusLabel:** ${document.status.displayText}
**$fileTypeLabel:** ${document.fileType?.displayText ?? unknownLabel}
**$pagesLabel:** ${document.pageCount?.toString() ?? notApplicableLabel}

## $summaryLabel
${document.summary ?? notApplicableLabel}

## $tagsLabel
${(document.tags != null && document.tags!.isNotEmpty) ? document.tags!.map((tag) => '- $tag').join('\n') : notApplicableLabel}

''';

      await fileSystem.copyFile(document.filePath, newPdfFilePath);
      await fileSystem.writeFile(markdownFilePath, markdownContent);
    } catch (e, s) {
      log('Error during export: $e', error: e, stackTrace: s, name: 'ExportService');
      if (e is ExportException) {
        rethrow;
      }
      throw ExportException('An unexpected error occurred during export', details: e.toString());
    }
  }
}
