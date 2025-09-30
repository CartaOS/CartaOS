import 'package:flutter/material.dart';
import 'package:carta_os/src/features/document/presentation/widgets/document_list_widget.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/data/document_service.dart';
import 'package:carta_os/src/localization/app_localizations.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late Future<List<Document>> _documentsFuture;
  final DocumentService _documentService = DocumentService();

  @override
  void initState() {
    super.initState();
    _documentsFuture = _documentService.getDocuments();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.homeScreenTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            tooltip: l10n.searchLabel,
            onPressed: () {
              // Implementar busca
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: l10n.settingsLabel,
            onPressed: () {
              // Implementar configurações
            },
          ),
        ],
      ),
      body: FutureBuilder<List<Document>>(
        future: _documentsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return Center(child: Text(l10n.noDocumentsFound));
          } else {
            return DocumentListWidget(documents: snapshot.data!);
          }
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Implementar adição de novo documento
        },
        tooltip: l10n.addDocumentTooltip,
        child: const Icon(Icons.add),
      ),
    );
  }
}