import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:carta_os/src/features/document/models/document.dart';
import 'package:carta_os/src/features/document/presentation/screens/document_detail_screen.dart';
import 'package:carta_os/src/localization/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

void main() {
  group('DocumentDetailScreen', () {
    final testDocument = Document.example();

    Widget createWidgetForTesting({required Widget child}) {
      return MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [
          Locale('pt', ''),
        ],
        home: child,
      );
    }

    testWidgets('should display document details correctly',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        createWidgetForTesting(
          child: DocumentDetailScreen(document: testDocument),
        ),
      );

      // Check if the document title is displayed
      expect(find.text(testDocument.title), findsOneWidget);

      // Check if the document summary is displayed (if it exists)
      if (testDocument.summary != null) {
        expect(find.text(testDocument.summary!), findsOneWidget);
      }

      // Check if the tags are displayed (if they exist)
      if (testDocument.tags != null) {
        for (String tag in testDocument.tags!) {
          expect(find.text(tag), findsWidgets);
        }
      }

      // Check if the key concepts are displayed (if they exist)
      if (testDocument.keyConcepts != null) {
        for (String concept in testDocument.keyConcepts!) {
          expect(find.text(concept), findsWidgets);
        }
      }
    });

    testWidgets('should display status information',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        createWidgetForTesting(
          child: DocumentDetailScreen(document: testDocument),
        ),
      );
      final l10n = AppLocalizations(const Locale('pt'));

      // Check if the status information is displayed
      expect(find.textContaining(l10n.documentTypeLabel), findsOneWidget);
      expect(find.textContaining(l10n.pagesLabel), findsOneWidget);
    });

    testWidgets('should have share and menu options in app bar',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        createWidgetForTesting(
          child: DocumentDetailScreen(document: testDocument),
        ),
      );

      // Check if the icons are present
      expect(find.byIcon(Icons.share), findsOneWidget);
      expect(find.byType(PopupMenuButton<String>), findsOneWidget);
    });

    testWidgets('should highlight key concepts and tags in content',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        createWidgetForTesting(
          child: DocumentDetailScreen(document: testDocument),
        ),
      );

      final selectableText = tester.widget<SelectableText>(
        find.byType(SelectableText),
      );

      final richText = selectableText.textSpan as TextSpan?;

      expect(richText, isNotNull);

      final spans = richText!.children ?? [];

      // Check if the content is correctly split and highlighted
      bool hasHighlightedKeyConcept = false;
      bool hasHighlightedTag = false;

      for (final span in spans) {
        if (span is TextSpan) {
          if (span.style?.backgroundColor == Colors.green.shade100) {
            hasHighlightedKeyConcept = true;
          } else if (span.style?.backgroundColor == Colors.blue.shade100) {
            hasHighlightedTag = true;
          }
        }
      }

      expect(hasHighlightedKeyConcept, isTrue);
      expect(hasHighlightedTag, isTrue);
    });
  });
}
