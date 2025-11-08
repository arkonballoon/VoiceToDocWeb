<template>
  <div class="help-page">
    <div class="help-container">
      <h1>Template-Hilfe</h1>
      <p class="intro">
        Diese Seite erklärt, wie Sie Templates für die verschiedenen unterstützten Formate vorbereiten können.
      </p>

      <!-- Übersicht -->
      <section class="help-section">
        <h2>Übersicht</h2>
        <div class="content-box">
          <h3>Was sind Templates?</h3>
          <p>
            Templates sind Vorlagen, die mit Platzhaltern versehen werden können. Diese Platzhalter werden 
            automatisch mit Informationen aus Transkriptionen gefüllt, um strukturierte Dokumente zu erstellen.
          </p>
          
          <h3>Unterstützte Formate</h3>
          <ul>
            <li><strong>Markdown (.md)</strong> - Textbasierte Templates</li>
            <li><strong>Word (.docx)</strong> - Microsoft Word Dokumente</li>
            <li><strong>Excel (.xlsx)</strong> - Microsoft Excel Arbeitsmappen</li>
          </ul>
        </div>
      </section>

      <!-- Platzhalter-Syntax -->
      <section class="help-section">
        <h2>Platzhalter-Syntax</h2>
        <div class="content-box">
          <h3>Format</h3>
          <p>
            Platzhalter müssen im folgenden Format geschrieben werden:
          </p>
          <div class="code-block">
            <code>&#123;&#123;feldname&#125;&#125;</code>
          </div>
          
          <h3>Regeln für Platzhalternamen</h3>
          <ul>
            <li>Nur Buchstaben, Zahlen und Unterstriche</li>
            <li>Keine Leerzeichen</li>
            <li>Keine Sonderzeichen (außer Unterstriche)</li>
            <li>Aussagekräftig und eindeutig</li>
          </ul>
          
          <div class="example-box">
            <strong>Beispiele:</strong>
            <ul>
              <li><code>&#123;&#123;projektname&#125;&#125;</code> ✅ Korrekt</li>
              <li><code>&#123;&#123;projekt_name&#125;&#125;</code> ✅ Korrekt</li>
              <li><code>&#123;&#123;projekt-name&#125;&#125;</code> ❌ Falsch (Bindestrich)</li>
              <li><code>&#123;&#123;projekt name&#125;&#125;</code> ❌ Falsch (Leerzeichen)</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Markdown-Templates -->
      <section class="help-section">
        <h2>Markdown-Templates</h2>
        <div class="content-box">
          <h3>Wie erstellen?</h3>
          <p>
            Markdown-Templates können direkt in der Template-Verwaltung erstellt werden. 
            Verwenden Sie den Markdown-Editor, um Ihr Template zu schreiben.
          </p>
          
          <h3>Platzhalter einfügen</h3>
          <p>
            Fügen Sie Platzhalter einfach als Text in Ihr Markdown-Dokument ein:
          </p>
          
          <div class="code-block">
            <pre><code># Projektbericht: &#123;&#123;projektname&#125;&#125;

## Zusammenfassung
&#123;&#123;zusammenfassung&#125;&#125;

## Details
- **Datum:** &#123;&#123;datum&#125;&#125;
- **Projektleiter:** &#123;&#123;projektleiter&#125;&#125;
- **Status:** &#123;&#123;status&#125;&#125;</code></pre>
          </div>
        </div>
      </section>

      <!-- Word-Templates -->
      <section class="help-section">
        <h2>Word-Templates (.docx)</h2>
        <div class="content-box">
          <h3>Platzhalter als Text</h3>
          <p>
            Platzhalter können direkt als Text in Word-Dokumenten verwendet werden:
          </p>
          <div class="code-block">
            <code>Projekt: &#123;&#123;projektname&#125;&#125;</code>
          </div>
          
          <h3>Platzhalter in Tabellen</h3>
          <p>
            Platzhalter funktionieren auch in Word-Tabellen:
          </p>
          <div class="table-example">
            <table>
              <tr>
                <th>Feld</th>
                <th>Wert</th>
              </tr>
              <tr>
                <td>Projektname</td>
                <td>&#123;&#123;projektname&#125;&#125;</td>
              </tr>
              <tr>
                <td>Datum</td>
                <td>&#123;&#123;datum&#125;&#125;</td>
              </tr>
            </table>
          </div>
          
          <div class="info-box">
            <strong>💡 Tipp:</strong> Platzhalter werden in allen Bereichen des Word-Dokuments erkannt, 
            einschließlich Header, Footer und Textfeldern.
          </div>
        </div>
      </section>

      <!-- Excel-Templates -->
      <section class="help-section">
        <h2>Excel-Templates (.xlsx)</h2>
        <div class="content-box">
          <h3>Platzhalter in Zellen (als Text)</h3>
          <p>
            Platzhalter können direkt als Text in Excel-Zellen eingegeben werden:
          </p>
          <div class="code-block">
            <code>Projekt: &#123;&#123;projektname&#125;&#125;</code>
          </div>
          
          <h3>Platzhalter in Formeln</h3>
          <p>
            Platzhalter können auch in Excel-Formeln verwendet werden:
          </p>
          <div class="code-block">
            <pre><code>="Projekt: "&&#123;&#123;projektname&#125;&#125;
=CONCATENATE("Status: ", &#123;&#123;status&#125;&#125;)
="Kosten: "&TEXT(&#123;&#123;kosten&#125;&#125;, "0.00 €")</code></pre>
          </div>
          
          <div class="warning-box">
            <strong>⚠️ Wichtig:</strong> 
            <ul>
              <li>Platzhalter in Formeln werden nur erkannt, wenn die Datei in Excel geöffnet und gespeichert wurde</li>
              <li>Berechnete Werte werden ebenfalls gelesen, aber Formeln haben Priorität</li>
              <li>Stellen Sie sicher, dass die Datei vor dem Hochladen in Excel gespeichert wurde</li>
            </ul>
          </div>
          
          <h3>Beispiel-Excel-Struktur</h3>
          <div class="table-example">
            <table>
              <tr>
                <th>A</th>
                <th>B</th>
              </tr>
              <tr>
                <td>Projektname</td>
                <td>&#123;&#123;projektname&#125;&#125;</td>
              </tr>
              <tr>
                <td>Datum</td>
                <td>&#123;&#123;datum&#125;&#125;</td>
              </tr>
              <tr>
                <td>Kosten</td>
                <td>=&#123;&#123;kosten&#125;&#125;</td>
              </tr>
            </table>
          </div>
        </div>
      </section>

      <!-- Best Practices -->
      <section class="help-section">
        <h2>Best Practices</h2>
        <div class="content-box">
          <ul>
            <li>
              <strong>Aussagekräftige Namen:</strong> Verwenden Sie klare, beschreibende Platzhalternamen 
              wie <code>&#123;&#123;projektname&#125;&#125;</code> statt <code>&#123;&#123;pn&#125;&#125;</code>
            </li>
            <li>
              <strong>Keine Sonderzeichen:</strong> Vermeiden Sie Leerzeichen, Bindestriche und andere 
              Sonderzeichen in Platzhalternamen
            </li>
            <li>
              <strong>Konsistenz:</strong> Verwenden Sie ein einheitliches Namensschema (z.B. camelCase 
              oder snake_case)
            </li>
            <li>
              <strong>Testen:</strong> Laden Sie Ihr Template hoch und prüfen Sie, ob alle Platzhalter 
              erkannt wurden
            </li>
            <li>
              <strong>Dokumentation:</strong> Fügen Sie eine Beschreibung zu Ihrem Template hinzu, 
              die erklärt, welche Platzhalter verwendet werden
            </li>
          </ul>
        </div>
      </section>

      <!-- Häufige Probleme -->
      <section class="help-section">
        <h2>Häufige Probleme &amp; Lösungen</h2>
        <div class="content-box">
          <div class="problem-box">
            <h3>❌ Problem: Platzhalter werden nicht erkannt</h3>
            <p><strong>Mögliche Ursachen:</strong></p>
            <ul>
              <li>Falsches Format (z.B. <code>&#123;feldname&#125;</code> statt <code>&#123;&#123;feldname&#125;&#125;</code>)</li>
              <li>Leerzeichen oder Sonderzeichen im Platzhalternamen</li>
              <li>Platzhalter in versteckten Zellen oder Kommentaren (Excel)</li>
            </ul>
            <p><strong>Lösung:</strong></p>
            <ul>
              <li>Prüfen Sie das Format: genau zwei geschweifte Klammern</li>
              <li>Verwenden Sie nur Buchstaben, Zahlen und Unterstriche</li>
              <li>Stellen Sie sicher, dass Platzhalter in sichtbaren Zellen stehen</li>
            </ul>
          </div>

          <div class="problem-box">
            <h3>❌ Problem: Excel-Formeln funktionieren nicht</h3>
            <p><strong>Mögliche Ursachen:</strong></p>
            <ul>
              <li>Datei wurde nicht in Excel geöffnet und gespeichert</li>
              <li>Formeln enthalten Platzhalter in falschem Format</li>
              <li>Datei wurde als CSV statt XLSX gespeichert</li>
            </ul>
            <p><strong>Lösung:</strong></p>
            <ul>
              <li>Öffnen Sie die Datei in Excel und speichern Sie sie erneut</li>
              <li>Verwenden Sie das Format <code>&#123;&#123;feldname&#125;&#125;</code> in Formeln</li>
              <li>Stellen Sie sicher, dass die Datei als .xlsx gespeichert wird</li>
            </ul>
          </div>

          <div class="problem-box">
            <h3>❌ Problem: Platzhalter werden doppelt erkannt</h3>
            <p><strong>Mögliche Ursachen:</strong></p>
            <ul>
              <li>Platzhalter steht sowohl in Formel als auch in berechnetem Wert</li>
              <li>Platzhalter in mehreren Zellen</li>
            </ul>
            <p><strong>Lösung:</strong></p>
            <ul>
              <li>Das ist normal - jeder Platzhalter wird nur einmal in der Liste angezeigt</li>
              <li>Sie können den Prompt für jeden Platzhalter individuell konfigurieren</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Quick Start -->
      <section class="help-section">
        <h2>Quick Start</h2>
        <div class="content-box">
          <ol>
            <li>
              <strong>Template erstellen:</strong> Erstellen Sie eine Word- oder Excel-Datei mit Ihren Platzhaltern
            </li>
            <li>
              <strong>Platzhalter einfügen:</strong> Verwenden Sie das Format <code>&#123;&#123;feldname&#125;&#125;</code>
            </li>
            <li>
              <strong>Hochladen:</strong> Laden Sie die Datei in der Template-Verwaltung hoch
            </li>
            <li>
              <strong>Prüfen:</strong> Überprüfen Sie, ob alle Platzhalter erkannt wurden
            </li>
            <li>
              <strong>Prompts anpassen:</strong> Bearbeiten Sie die Prompts für jeden Platzhalter, um die Extraktion zu optimieren
            </li>
            <li>
              <strong>Verwenden:</strong> Verwenden Sie das Template bei der Template-Verarbeitung
            </li>
          </ol>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HelpView',
  mounted() {
    document.title = 'Hilfe - Template-Vorbereitung | VoiceToDoc'
  }
}
</script>

<style scoped>
.help-page {
  padding: 1rem;
  max-width: 1000px;
  margin: 4rem auto 0;
  min-height: calc(100vh - 4rem);
}

.help-container {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h1 {
  color: var(--secondary-color);
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

.intro {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.help-section {
  margin-bottom: 3rem;
}

.help-section h2 {
  color: var(--secondary-color);
  font-size: 1.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--primary-color);
}

.content-box {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 6px;
  border-left: 4px solid var(--primary-color);
}

.content-box h3 {
  color: var(--secondary-color);
  font-size: 1.2rem;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.content-box h3:first-child {
  margin-top: 0;
}

.content-box p {
  line-height: 1.6;
  margin-bottom: 1rem;
  color: #333;
}

.content-box ul {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
  line-height: 1.8;
}

.content-box li {
  margin-bottom: 0.5rem;
}

.code-block {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
  overflow-x: auto;
}

.code-block code {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: #f8f8f2;
}

.code-block pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.example-box {
  background: #e8f5e9;
  border: 1px solid #4caf50;
  border-radius: 4px;
  padding: 1rem;
  margin: 1rem 0;
}

.example-box strong {
  display: block;
  margin-bottom: 0.5rem;
  color: #2e7d32;
}

.example-box ul {
  margin: 0.5rem 0 0 1.5rem;
}

.example-box code {
  background: white;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: monospace;
}

.info-box {
  background: #e3f2fd;
  border: 1px solid #2196f3;
  border-radius: 4px;
  padding: 1rem;
  margin: 1rem 0;
}

.info-box strong {
  color: #1976d2;
}

.warning-box {
  background: #fff3cd;
  border: 2px solid #ffc107;
  border-radius: 4px;
  padding: 1rem;
  margin: 1rem 0;
  color: #856404;
}

.warning-box strong {
  color: #856404;
  display: block;
  margin-bottom: 0.5rem;
}

.warning-box ul {
  margin: 0.5rem 0 0 1.5rem;
}

.problem-box {
  background: #ffebee;
  border-left: 4px solid #f44336;
  border-radius: 4px;
  padding: 1rem;
  margin: 1.5rem 0;
}

.problem-box h3 {
  color: #c62828;
  margin-top: 0;
  margin-bottom: 0.75rem;
}

.problem-box p {
  margin: 0.5rem 0;
}

.problem-box ul {
  margin: 0.5rem 0 0 1.5rem;
}

.table-example {
  margin: 1rem 0;
  overflow-x: auto;
}

.table-example table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border: 1px solid #ddd;
}

.table-example th,
.table-example td {
  padding: 0.75rem;
  border: 1px solid #ddd;
  text-align: left;
}

.table-example th {
  background: #f5f5f5;
  font-weight: bold;
  color: var(--secondary-color);
}

.content-box ol {
  margin-left: 1.5rem;
  line-height: 1.8;
}

.content-box ol li {
  margin-bottom: 0.75rem;
}

.content-box ol li strong {
  color: var(--secondary-color);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .help-page {
    padding: 0.5rem;
    margin-top: 3.5rem;
  }

  .help-container {
    padding: 1rem;
  }

  h1 {
    font-size: 1.5rem;
  }

  .help-section h2 {
    font-size: 1.2rem;
  }

  .content-box {
    padding: 1rem;
  }

  .code-block {
    padding: 0.75rem;
    font-size: 0.85rem;
  }
}
</style>

