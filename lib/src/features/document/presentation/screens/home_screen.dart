import 'package:flutter/material.dart';
import 'package:carta_os/src/features/document/presentation/widgets/document_list_widget.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';
import 'package:provider/provider.dart';
import 'package:carta_os/src/features/document/domain/export_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<Document> documents = [
    Document.example(),
    Document(
      id: '2',
      title: 'Contrato de Prestação de Serviços',
      content: 'Este é o conteúdo do contrato de prestação de serviços. Ele contém cláusulas importantes sobre obrigações, prazos e condições de pagamento.',
      summary: 'Contrato detalhando os termos de prestação de serviços entre as partes.',
      tags: ['contrato', 'financeiro', 'legal'],
      createdAt: DateTime(2025, 9, 25),
      processedAt: DateTime(2025, 9, 26),
      status: DocumentStatus.completed,
      filePath: '/path/to/contract.pdf',
      pageCount: 8,
      fileType: DocumentFileType.native,
    ),
    Document(
      id: '3',
      title: 'Relatório Trimestral',
      content: 'Relatório com os resultados financeiros do trimestre. Inclui gráficos e análise de performance.',
      summary: 'Relatório detalhado sobre os resultados do trimestre.',
      tags: ['relatório', 'financeiro', 'trimestral'],
      createdAt: DateTime(2025, 9, 20),
      processedAt: DateTime(2025, 9, 21),
      status: DocumentStatus.processing,
      filePath: '/path/to/quarterly_report.pdf',
      pageCount: 15,
      fileType: DocumentFileType.native,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final exportService = Provider.of<ExportService>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('CartaOS - Documentos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // Implementar busca
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // Implementar configurações
            },
          ),
        ],
      ),
      body: DocumentListWidget(documents: documents, exportService: exportService),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Implementar adição de novo documento
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}