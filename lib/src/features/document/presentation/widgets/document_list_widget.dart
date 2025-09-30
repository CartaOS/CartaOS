import 'package:flutter/material.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/presentation/screens/document_detail_screen.dart';

class DocumentListWidget extends StatelessWidget {
  final List<Document> documents;

  const DocumentListWidget({Key? key, required this.documents}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (documents.isEmpty) {
      return const Center(
        child: Text('Nenhum documento encontrado'),
      );
    }

    return ListView.builder(
      itemCount: documents.length,
      itemBuilder: (context, index) {
        final document = documents[index];
        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: ListTile(
            contentPadding: const EdgeInsets.all(16.0),
            leading: CircleAvatar(
              backgroundColor: _getStatusColor(document.status).withOpacity(0.2),
              child: Icon(
                _getStatusIcon(document.status),
                color: _getStatusColor(document.status),
              ),
            ),
            title: Text(
              document.title,
              style: const TextStyle(fontWeight: FontWeight.bold),
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
                  style: const TextStyle(fontSize: 12),
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
                              style: const TextStyle(fontSize: 10),
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
                  _formatDate(document.processedAt ?? document.createdAt),
                  style: const TextStyle(fontSize: 12),
                ),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 8.0, vertical: 2.0),
                  decoration: BoxDecoration(
                    color: _getStatusColor(document.status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10.0),
                  ),
                  child: Text(
                    _getStatusText(document.status),
                    style: TextStyle(
                      fontSize: 10,
                      color: _getStatusColor(document.status),
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

  IconData _getStatusIcon(String status) {
    switch (status) {
      case 'completed':
        return Icons.check_circle;
      case 'processing':
        return Icons.hourglass_top;
      case 'pending':
      default:
        return Icons.access_time;
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'completed':
        return Colors.green;
      case 'processing':
        return Colors.orange;
      case 'pending':
      default:
        return Colors.grey;
    }
  }

  String _getStatusText(String status) {
    switch (status) {
      case 'completed':
        return 'Pronto';
      case 'processing':
        return 'Processando';
      case 'pending':
      default:
        return 'Pendente';
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}