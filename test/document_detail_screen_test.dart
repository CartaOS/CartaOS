import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/presentation/screens/document_detail_screen.dart';

void main() {
  group('DocumentDetailScreen', () {
    final testDocument = Document.example();

    testWidgets('should display document details correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: DocumentDetailScreen(document: testDocument),
        ),
      );

      // Verificar se o título do documento é exibido
      expect(find.text(testDocument.title), findsOneWidget);

      // Verificar se o conteúdo do documento é exibido
      expect(find.text(testDocument.content), findsOneWidget);

      // Verificar se o sumário do documento é exibido (se existir)
      if (testDocument.summary != null) {
        expect(find.text(testDocument.summary!), findsOneWidget);
      }

      // Verificar se as tags são exibidas (se existirem)
      if (testDocument.tags != null) {
        for (String tag in testDocument.tags!) {
          expect(find.text(tag), findsOneWidget);
        }
      }
    });

    testWidgets('should display status information', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: DocumentDetailScreen(document: testDocument),
        ),
      );

      // Verificar se as informações de status são exibidas
      expect(find.textContaining('Tipo:'), findsOneWidget);
      expect(find.textContaining('Páginas:'), findsOneWidget);
    });

    testWidgets('should have share and menu options in app bar', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: DocumentDetailScreen(document: testDocument),
        ),
      );

      // Verificar se os ícones estão presentes
      expect(find.byIcon(Icons.share), findsOneWidget);
      expect(find.byType(PopupMenuButton<String>), findsOneWidget);
    });
  });
}