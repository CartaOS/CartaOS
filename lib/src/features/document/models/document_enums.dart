import 'package:flutter/material.dart';

/// Enums para representar os diferentes estados e tipos de documentos
enum DocumentStatus { pending, processing, completed }

extension DocumentStatusInfo on DocumentStatus {
  /// Retorna o ícone apropriado para o status do documento
  IconData get icon {
    switch (this) {
      case DocumentStatus.completed:
        return Icons.check_circle;
      case DocumentStatus.processing:
        return Icons.hourglass_top;
      case DocumentStatus.pending:
        return Icons.access_time;
    }
  }

  /// Retorna a cor apropriada para o status do documento
  Color get color {
    switch (this) {
      case DocumentStatus.completed:
        return Colors.green;
      case DocumentStatus.processing:
        return Colors.orange;
      case DocumentStatus.pending:
        return Colors.grey;
    }
  }

  /// Retorna o texto a ser exibido para o status do documento
  String get displayText {
    switch (this) {
      case DocumentStatus.completed:
        return 'Processado';
      case DocumentStatus.processing:
        return 'Processando';
      case DocumentStatus.pending:
        return 'Pendente';
    }
  }
}

/// Enum para representar os diferentes tipos de arquivos de documento
enum DocumentFileType { native, scanned, mixed }

extension DocumentFileTypeDisplay on DocumentFileType {
  /// Retorna o texto a ser exibido para o tipo de arquivo do documento
  String get displayText {
    switch (this) {
      case DocumentFileType.native:
        return 'Nativo';
      case DocumentFileType.scanned:
        return 'Digitalizado';
      case DocumentFileType.mixed:
        return 'Misto';
    }
  }
}