import 'package:flutter/material.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';
import 'package:intl/intl.dart';
import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:path/path.dart' as p;

class DocumentDetailScreen extends StatelessWidget {
  final Document document;

  const DocumentDetailScreen({Key? key, required this.document}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Usar formatação de data com internacionalização
    final dateFormat = DateFormat('dd/MM/yyyy');

    return Scaffold(
      appBar: AppBar(
        title: Text(
          document.title,
          style: Theme.of(context).textTheme.titleLarge,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () {
              // Implementar compartilhamento
            },
          ),
          PopupMenuButton<String>(
            onSelected: (String result) {
              if (result == 'export') {
                _exportDocument(context, document);
              } else if (result == 'delete') {
                // Implementar exclusão
              }
            },
            itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
              const PopupMenuItem<String>(
                value: 'export',
                child: Text('Exportar'),
              ),
              const PopupMenuItem<String>(
                value: 'delete',
                child: Text('Excluir'),
              ),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status e informações do documento
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                document.status.icon,
                                color: document.status.color,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                document.status.displayText,
                                style: TextStyle(
                                  color: document.status.color,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Tipo: ${document.fileType?.displayText ?? 'Desconhecido'}',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Páginas: ${document.pageCount?.toString() ?? 'N/A'}',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Criado: ${dateFormat.format(document.createdAt)}',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            document.processedAt != null 
                                ? 'Processado: ${dateFormat.format(document.processedAt!)}' 
                                : 'Aguardando processamento',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Tags
            if (document.tags != null && document.tags!.isNotEmpty) ...[
              const Text(
                'Tags',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8.0,
                runSpacing: 4.0,
                children: document.tags!.map((tag) {
                  return Chip(
                    label: Text(tag),
                    backgroundColor: Colors.blue.shade100,
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
            ],
            
            // Sumário (se disponível)
            if (document.summary != null && document.summary!.isNotEmpty) ...[
              const Text(
                'Sumário',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(
                    document.summary!,
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],
            
            // Conteúdo do documento
            const Text(
              'Conteúdo',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: SelectableText(
                  document.content,
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _exportDocument(BuildContext context, Document document) async {
    final String? selectedDirectory = await FilePicker.platform.getDirectoryPath();

    if (selectedDirectory == null) {
      // User canceled the picker
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Exportação cancelada.')),
      );
      return;
    }

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
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Arquivo PDF original não encontrado.')),
        );
        return;
      }

      // Define file paths using the 'path' package for cross-platform compatibility
      final pdfFileName = '${safeTitle}.pdf';
      final markdownFileName = '${safeTitle}.md';
      final newPdfFile = File(p.join(selectedDirectory, pdfFileName));
      final markdownFile = File(p.join(selectedDirectory, markdownFileName));

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

      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Documento exportado para $selectedDirectory')),
      );
    } on FileSystemException catch (e, s) {
      print('File system error during export: $e\n$s');
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro de arquivo ao exportar: ${e.message}')),
      );
    } catch (e, s) {
      print('Unexpected error during export: $e\n$s');
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ocorreu um erro inesperado ao exportar.')),
      );
    }
  }
}
