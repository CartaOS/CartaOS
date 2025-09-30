import 'package:equatable/equatable.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';

class Document extends Equatable {
  final String id;
  final String title;
  final String content;
  final String? summary;
  final List<String>? tags;
  final List<String>? keyConcepts;
  final DateTime createdAt;
  final DateTime? processedAt;
  final DocumentStatus status;
  final String filePath;
  final int? pageCount;
  final DocumentFileType? fileType;

  const Document({
    required this.id,
    required this.title,
    required this.content,
    this.summary,
    this.tags,
    this.keyConcepts,
    required this.createdAt,
    this.processedAt,
    required this.status,
    required this.filePath,
    this.pageCount,
    this.fileType,
  });

  @override
  List<Object?> get props => [
        id,
        title,
        content,
        summary,
        tags,
        keyConcepts,
        createdAt,
        processedAt,
        status,
        filePath,
        pageCount,
        fileType,
      ];

  Document copyWith({
    String? id,
    String? title,
    String? content,
    String? summary,
    List<String>? tags,
    List<String>? keyConcepts,
    DateTime? createdAt,
    DateTime? processedAt,
    DocumentStatus? status,
    String? filePath,
    int? pageCount,
    DocumentFileType? fileType,
  }) {
    return Document(
      id: id ?? this.id,
      title: title ?? this.title,
      content: content ?? this.content,
      summary: summary ?? this.summary,
      tags: tags ?? this.tags,
      keyConcepts: keyConcepts ?? this.keyConcepts,
      createdAt: createdAt ?? this.createdAt,
      processedAt: processedAt ?? this.processedAt,
      status: status ?? this.status,
      filePath: filePath ?? this.filePath,
      pageCount: pageCount ?? this.pageCount,
      fileType: fileType ?? this.fileType,
    );
  }

  factory Document.fromJson(Map<String, dynamic> json) {
    return Document(
      id: json['id'],
      title: json['title'],
      content: json['content'],
      summary: json['summary'],
      tags: json['tags']?.cast<String>(),
      keyConcepts: json['keyConcepts']?.cast<String>(),
      createdAt: DateTime.parse(json['createdAt']),
      processedAt: json['processedAt'] != null
          ? DateTime.parse(json['processedAt'])
          : null,
      status: DocumentStatus.values.byName(json['status']),
      filePath: json['filePath'],
      pageCount: json['pageCount'],
      fileType: json['fileType'] != null
          ? DocumentFileType.values.byName(json['fileType'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'summary': summary,
      'tags': tags,
      'keyConcepts': keyConcepts,
      'createdAt': createdAt.toIso8601String(),
      'processedAt': processedAt?.toIso8601String(),
      'status': status.name,
      'filePath': filePath,
      'pageCount': pageCount,
      'fileType': fileType?.name,
    };
  }

  // Método factory para criar um documento de exemplo
  static Document example() {
    return Document(
      id: '1',
      title: 'Documento de Exemplo',
      content:
          'Este é um exemplo de conteúdo de documento. Ele pode conter texto extraído de PDFs, com parágrafos, listas e outras estruturas de texto. Este documento é muito importante e tem implicações do âmbito financeiro e legal. O contrato estabelece as obrigações e cláusulas para a validade do acordo.',
      summary:
          'Este é um resumo gerado automaticamente do documento de exemplo.',
      tags: ['importante', 'financeiro', 'legal'],
      keyConcepts: ['contrato', 'obrigações', 'cláusulas', 'validade'],
      createdAt: DateTime(2025, 9, 28),
      processedAt: DateTime(2025, 9, 29),
      status: DocumentStatus.completed,
      filePath: '/path/to/example.pdf',
      pageCount: 12,
      fileType: DocumentFileType.native,
    );
  }
}
