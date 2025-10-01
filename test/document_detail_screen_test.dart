import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/presentation/screens/document_detail_screen.dart';
import 'package:carta_os/src/features/document/domain/export_service.dart';
import 'package:mockito/mockito.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:carta_os/src/localization/app_localizations.dart';

class MockExportService extends Mock implements ExportService {}

void main() {
  group('DocumentDetailScreen', () {
    final testDocument = Document.example();
    late MockExportService mockExportService;

    setUp(() {
      mockExportService = MockExportService();
    });

    testWidgets('should display document details correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
          ],
          supportedLocales: [
            const Locale('en', ''),
          ],
          home: DocumentDetailScreen(document: testDocument, exportService: mockExportService),
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
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
          ],
          supportedLocales: [
            const Locale('en', ''),
          ],
          home: DocumentDetailScreen(document: testDocument, exportService: mockExportService),
        ),
      );

      // Verificar se as informações de status são exibidas
      expect(find.textContaining('Type'), findsOneWidget);
      expect(find.textContaining('Pages'), findsOneWidget);
    });

    testWidgets('should have share and menu options in app bar', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
          ],
          supportedLocales: [
            const Locale('en', ''),
          ],
          home: DocumentDetailScreen(document: testDocument, exportService: mockExportService),
        ),
      );

      // Verificar se os ícones estão presentes
      expect(find.byIcon(Icons.share), findsOneWidget);
      expect(find.byType(PopupMenuButton<String>), findsOneWidget);
    });
  });
}
