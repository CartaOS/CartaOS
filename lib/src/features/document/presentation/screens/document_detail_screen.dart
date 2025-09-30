import 'package:flutter/material.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';
import 'package:carta_os/src/localization/app_localizations.dart';
import 'package:intl/intl.dart';

class DocumentDetailScreen extends StatelessWidget {
  final Document document;

  const DocumentDetailScreen({super.key, required this.document});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Text(
          document.title,
          style: Theme.of(context).textTheme.titleLarge,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            tooltip: l10n.shareLabel,
            onPressed: () {
              // Implementar compartilhamento
            },
          ),
          PopupMenuButton<String>(
            onSelected: (String result) {
              // Implementar ações do menu
            },
            itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
              PopupMenuItem<String>(
                value: 'export',
                child: Text(l10n.exportLabel),
              ),
              PopupMenuItem<String>(
                value: 'delete',
                child: Text(l10n.deleteLabel),
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
            _buildInfoCard(context),
            const SizedBox(height: 16),
            if (document.tags != null && document.tags!.isNotEmpty) ...[
              _buildSectionTitle(l10n.tagsLabel),
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
            if (document.keyConcepts != null &&
                document.keyConcepts!.isNotEmpty) ...[
              _buildSectionTitle(l10n.keyConceptsLabel),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8.0,
                runSpacing: 4.0,
                children: document.keyConcepts!.map((concept) {
                  return Chip(
                    label: Text(concept),
                    backgroundColor: Colors.green.shade100,
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
            ],
            if (document.summary != null && document.summary!.isNotEmpty) ...[
              _buildSectionTitle(l10n.summaryLabel),
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
            _buildSectionTitle(l10n.contentLabel),
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: _buildContent(context),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final dateFormat = DateFormat('dd/MM/yyyy');
    return Card(
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
                        document.status.displayText(l10n),
                        style: TextStyle(
                          color: document.status.color,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${l10n.documentTypeLabel}: ${document.fileType?.displayText(l10n) ?? l10n.unknownLabel}',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${l10n.pagesLabel}: ${document.pageCount?.toString() ?? 'N/A'}',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${l10n.fileLabel}: ${document.filePath}',
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
                    '${l10n.createdLabel}: ${dateFormat.format(document.createdAt)}',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    document.processedAt != null
                        ? '${l10n.processedLabel}: ${dateFormat.format(document.processedAt!)}'
                        : l10n.waitingProcessingLabel,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.bold,
      ),
    );
  }

  Widget _buildContent(BuildContext context) {
    final text = document.content;
    final keyConcepts = document.keyConcepts ?? [];
    final tags = document.tags ?? [];
    final allKeywords = [...keyConcepts, ...tags];

    if (allKeywords.isEmpty) {
      return SelectableText(
        text,
        style: Theme.of(context).textTheme.bodyLarge,
      );
    }

    final spans = <TextSpan>[];
    final pattern = allKeywords.map((e) => '\b${RegExp.escape(e)}\b').join('|');
    final regex = RegExp(pattern, caseSensitive: false);

    final lowercasedKeyConcepts = keyConcepts.map((c) => c.toLowerCase()).toSet();

    text.splitMapJoin(
      regex,
      onMatch: (match) {
        final matchedText = match.group(0)!;
        final isKeyConcept =
            lowercasedKeyConcepts.contains(matchedText.toLowerCase());
        spans.add(
          TextSpan(
            text: matchedText,
            style: TextStyle(
              backgroundColor:
                  isKeyConcept ? Colors.green.shade100 : Colors.blue.shade100,
              fontWeight: FontWeight.bold,
            ),
          ),
        );
        return '';
      },
      onNonMatch: (nonMatch) {
        spans.add(TextSpan(text: nonMatch));
        return '';
      },
    );

    return SelectableText.rich(
      TextSpan(
        children: spans,
        style: Theme.of(context).textTheme.bodyLarge,
      ),
    );
  }
}
