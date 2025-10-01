import 'package:flutter/material.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/models/document_enums.dart';
import 'package:intl/intl.dart';
import 'package:carta_os/src/localization/app_localizations.dart';
import 'dart:io';
import 'package:file_picker/file_picker.dart';

import 'package:carta_os/src/features/document/domain/export_service.dart';

class DocumentDetailScreen extends StatefulWidget {
  final Document document;
  final ExportService exportService;

  const DocumentDetailScreen({
    Key? key,
    required this.document,
    required this.exportService,
  }) : super(key: key);

  @override
  State<DocumentDetailScreen> createState() => _DocumentDetailScreenState();
}

class _DocumentDetailScreenState extends State<DocumentDetailScreen> {
  bool _isExporting = false; // For loading indicator

  @override
  Widget build(BuildContext context) {
    final AppLocalizations appLocalizations = AppLocalizations.of(context)!;
    final dateFormat = DateFormat('dd/MM/yyyy');

    return Stack(
      children: [
        Scaffold(
          appBar: AppBar(
            title: Text(
              widget.document.title,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.share),
                onPressed: () {
                  // Implementar compartilhamento
                },
              ),
              PopupMenuButton<String>(
                onSelected: (String result) {
                  if (result == 'export') {
                    _exportDocument(context);
                  } else if (result == 'delete') {
                    // Implementar exclusão
                  }
                },
                itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
                  PopupMenuItem<String>(
                    value: 'export',
                    child: Text(appLocalizations.exportOption),
                  ),
                  PopupMenuItem<String>(
                    value: 'delete',
                    child: Text(appLocalizations.deleteOption),
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
                // Status e informações do documento
                Card(
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
                                    widget.document.status.icon,
                                    color: widget.document.status.color,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    widget.document.status.displayText,
                                    style: TextStyle(
                                      color: widget.document.status.color,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${appLocalizations.documentType}: ${widget.document.fileType?.displayText ?? appLocalizations.unknown}',
                                style: Theme.of(context).textTheme.bodyMedium,
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${appLocalizations.pageCount}: ${widget.document.pageCount?.toString() ?? appLocalizations.notApplicable}',
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
                                '${appLocalizations.createdAt}: ${dateFormat.format(widget.document.createdAt)}',
                                style: Theme.of(context).textTheme.bodyMedium,
                              ),
                              const SizedBox(height: 4),
                              Text(
                                widget.document.processedAt != null
                                    ? '${appLocalizations.processedAt}: ${dateFormat.format(widget.document.processedAt!)}'
                                    : appLocalizations.pendingProcessing,
                                style: Theme.of(context).textTheme.bodyMedium,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                // Tags
                if (widget.document.tags != null && widget.document.tags!.isNotEmpty) ...[
                  Text(
                    appLocalizations.tagsTitle,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8.0,
                    runSpacing: 4.0,
                    children: widget.document.tags!.map((tag) {
                      return Chip(
                        label: Text(tag),
                        backgroundColor: Colors.blue.shade100,
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 16),
                ],

                // Sumário (se disponível)
                if (widget.document.summary != null && widget.document.summary!.isNotEmpty) ...[
                  Text(
                    appLocalizations.summaryTitle,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(
                        widget.document.summary!,
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // Conteúdo do documento
                Text(
                  appLocalizations.contentTitle,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: SelectableText(
                      widget.document.content,
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        if (_isExporting)
          Container(
            color: Colors.black.withAlpha(128),
            child: const Center(
              child: CircularProgressIndicator(),
            ),
          ),
      ],
    );
  }

  void _exportDocument(BuildContext context) async {
    setState(() {
      _isExporting = true;
    });

    final String? selectedDirectory = await FilePicker.platform.getDirectoryPath();

    if (selectedDirectory == null) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(AppLocalizations.of(context)!.exportCanceled)),
      );
      setState(() {
        _isExporting = false;
      });
      return;
    }

    try {
      final l10n = AppLocalizations.of(context)!;
      await widget.exportService.exportDocument(
        document: widget.document,
        targetDirectory: selectedDirectory,
        idLabel: l10n.idLabel,
        createdAtLabel: l10n.createdAt,
        processedAtLabel: l10n.processedAt,
        statusLabel: l10n.statusLabel,
        fileTypeLabel: l10n.documentType,
        pagesLabel: l10n.pageCount,
        summaryLabel: l10n.summaryTitle,
        tagsLabel: l10n.tagsTitle,
        pendingProcessingLabel: l10n.pendingProcessing,
        unknownLabel: l10n.unknown,
        notApplicableLabel: l10n.notApplicable,
      );

      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(AppLocalizations.of(context)!.documentExportedTo(selectedDirectory))),
      );
    } on FileSystemException catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(AppLocalizations.of(context)!.fileExportError(e.message))),
      );
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(AppLocalizations.of(context)!.unexpectedExportError)),
      );
    } finally {
      setState(() {
        _isExporting = false;
      });
    }
  }
}
