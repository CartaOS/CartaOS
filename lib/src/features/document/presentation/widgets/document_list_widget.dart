import 'package:flutter/material.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';
import 'package:carta_os/src/features/document/presentation/screens/document_detail_screen.dart';
import 'package:carta_os/src/localization/app_localizations.dart';
import 'package:intl/intl.dart';

class DocumentListWidget extends StatelessWidget {
  final List<Document> documents;

  const DocumentListWidget({Key? key, required this.documents}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    if (documents.isEmpty) {
      return Center(
        child: Text(l10n.noDocumentsFound),
      );
    }

    // Usar formatação de data com internacionalização
    final dateFormat = DateFormat('dd/MM/yyyy');

    return ListView.builder(
      itemCount: documents.length,
      itemBuilder: (context, index) {
        final document = documents[index];
        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: ListTile(
            contentPadding: const EdgeInsets.all(16.0),
            leading: CircleAvatar(
              backgroundColor: document.status.color.withOpacity(0.2),
              child: Icon(
                document.status.icon,
                color: document.status.color,
              ),
            ),
            title: Text(
              document.title,
              style: Theme.of(context)
                  .textTheme
                  .titleSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 4),
                Text(
                  '${document.summary ?? ''}',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 4.0,
                  runSpacing: 2.0,
                  children: (document.tags ?? [])
                      .take(3)
                      .map((tag) => Chip(
                            label: Text(
                              tag,
                              style: Theme.of(context).textTheme.labelSmall,
                            ),
                            backgroundColor: Colors.blue.shade50,
                            padding: const EdgeInsets.symmetric(
                                horizontal: 4.0, vertical: 2.0),
                            labelPadding: const EdgeInsets.symmetric(
                                horizontal: 4.0, vertical: 1.0),
                          ))
                      .toList(),
                ),
              ],
            ),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Text(
                  dateFormat.format(document.processedAt ?? document.createdAt),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 8.0, vertical: 2.0),
                  decoration: BoxDecoration(
                    color: document.status.color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10.0),
                  ),
                  child: Text(
                    document.status.displayText(l10n),
                    style: TextStyle(
                      fontSize: 10,
                      color: document.status.color,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => DocumentDetailScreen(document: document),
                ),
              );
            },
          ),
        );
      },
    );
  }
}
