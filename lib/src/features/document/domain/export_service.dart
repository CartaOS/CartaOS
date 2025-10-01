import 'dart:io';
import 'package:intl/intl.dart';
import 'package:path/path.dart' as p;
import 'package:carta_os/src/features/document/models/document.dart';

class ExportService {
  Future<void> exportDocument({
    required Document document,
    required String targetDirectory,
  }) async {
    try {
      // Sanitize filename to be safe for filesystems
      String safeTitle = document.title
          .replaceAll(RegExp(r'[\s/\\?%*:|"<>]+'), '_')
          .replaceAll(RegExp(r'[^\w.-]+'), '');

      if (safeTitle.isEmpty) {
        safeTitle = 'document_${document.id}'; // Fallback filename
      }

      final originalPdfFile = File(document.filePath);
      if (!await originalPdfFile.exists()) {
        throw FileSystemException('Original PDF file not found', document.filePath);
      }

      // Define file paths using the 'path' package for cross-platform compatibility
      final pdfFileName = '${safeTitle}.pdf';
      final markdownFileName = '${safeTitle}.md';
      final newPdfFile = File(p.join(targetDirectory, pdfFileName));
      final markdownFile = File(p.join(targetDirectory, markdownFileName));

      // Create Markdown content
      final String markdownContent = '''
# ${document.title}

**ID:** ${document.id}
**Criado em:** ${DateFormat('dd/MM/yyyy').format(document.createdAt)}
**Processado em:** ${document.processedAt != null ? DateFormat('dd/MM/yyyy').format(document.processedAt!) : 'Aguardando processamento'}
**Status:** ${document.status.displayText}
**Tipo de Arquivo:** ${document.fileType?.displayText ?? 'Desconhecido'}
**Páginas:** ${document.pageCount?.toString() ?? 'N/A'}

## Sumário
${document.summary ?? 'N/A'}

## Tags
${(document.tags != null && document.tags!.isNotEmpty) ? document.tags!.map((tag) => '- $tag').join('\n') : 'N/A'}

## Conteúdo
${document.content}
''';

      // Copy original PDF and write Markdown file
      await originalPdfFile.copy(newPdfFile.path);
      await markdownFile.writeAsString(markdownContent);
    } on FileSystemException {
      rethrow; // Rethrow FileSystemExceptions as they are specific
    } catch (e, s) {
      print('Unexpected error during export: $e\n$s');
      throw Exception('Ocorreu um erro inesperado ao exportar o documento.');
    }
  }
}
