import 'package:flutter/material.dart';
import 'package:carta_os/src/localization/app_localizations.dart';

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
  String displayText(AppLocalizations l10n) {
    switch (this) {
      case DocumentStatus.completed:
        return l10n.documentStatusCompleted;
      case DocumentStatus.processing:
        return l10n.documentStatusProcessing;
      case DocumentStatus.pending:
        return l10n.documentStatusPending;
    }
  }
}

/// Enum para representar os diferentes tipos de arquivos de documento
enum DocumentFileType { native, scanned, mixed }

extension DocumentFileTypeDisplay on DocumentFileType {
  /// Retorna o texto a ser exibido para o tipo de arquivo do documento
  String displayText(AppLocalizations l10n) {
    switch (this) {
      case DocumentFileType.native:
        return l10n.documentFileTypeNative;
      case DocumentFileType.scanned:
        return l10n.documentFileTypeScanned;
      case DocumentFileType.mixed:
        return l10n.documentFileTypeMixed;
    }
  }
}
