import 'package:flutter/material.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';
import 'package:intl/intl.dart';

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
              // Implementar ações do menu
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
}