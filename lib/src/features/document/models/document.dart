class Document {
  final String id;
  final String title;
  final String content;
  final String? summary;
  final List<String>? tags;
  final DateTime createdAt;
  final DateTime? processedAt;
  final String status; // pending, processing, completed
  final String filePath;
  final int? pageCount;
  final String? fileType; // native, scanned, mixed

  Document({
    required this.id,
    required this.title,
    required this.content,
    this.summary,
    this.tags,
    required this.createdAt,
    this.processedAt,
    required this.status,
    required this.filePath,
    this.pageCount,
    this.fileType,
  });

  // Método factory para criar um documento de exemplo
  static Document example() {
    return Document(
      id: '1',
      title: 'Documento de Exemplo',
      content: 'Este é um exemplo de conteúdo de documento. Ele pode conter texto extraído de PDFs, com parágrafos, listas e outras estruturas de texto.',
      summary: 'Este é um resumo gerado automaticamente do documento de exemplo.',
      tags: ['contrato', 'importante', 'financeiro'],
      createdAt: DateTime.now().subtract(const Duration(days: 2)),
      processedAt: DateTime.now().subtract(const Duration(days: 1)),
      status: 'completed',
      filePath: '/path/to/example.pdf',
      pageCount: 12,
      fileType: 'native',
    );
  }
}