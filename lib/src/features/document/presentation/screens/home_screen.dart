import 'package:flutter/material.dart';
import 'package:carta_os/src/features/document/presentation/widgets/document_list_widget.dart';
import 'package:carta_os/src/features/document/models/document.dart';

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
      createdAt: DateTime.now().subtract(const Duration(days: 5)),
      processedAt: DateTime.now().subtract(const Duration(days: 4)),
      status: 'completed',
      filePath: '/path/to/contract.pdf',
      pageCount: 8,
      fileType: 'native',
    ),
    Document(
      id: '3',
      title: 'Relatório Trimestral',
      content: 'Relatório com os resultados financeiros do trimestre. Inclui gráficos e análise de performance.',
      summary: 'Relatório detalhado sobre os resultados do trimestre.',
      tags: ['relatório', 'financeiro', 'trimestral'],
      createdAt: DateTime.now().subtract(const Duration(days: 10)),
      processedAt: DateTime.now().subtract(const Duration(days: 9)),
      status: 'processing',
      filePath: '/path/to/quarterly_report.pdf',
      pageCount: 15,
      fileType: 'native',
    ),
  ];

  @override
  Widget build(BuildContext context) {
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
      body: DocumentListWidget(documents: documents),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Implementar adição de novo documento
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}