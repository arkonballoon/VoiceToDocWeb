"""
Utility-Modul für die Generierung von Standard-Prompts basierend auf Platzhalternamen
"""
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class PromptGenerator:
    """Generiert Standard-Prompts basierend auf Platzhalternamen"""
    
    # Mapping von Platzhalternamen zu Standard-Prompts
    DEFAULT_PROMPTS: Dict[str, str] = {
        'zusammenfassung': 'Erstelle eine prägnante Zusammenfassung der wichtigsten Punkte.',
        'summary': 'Erstelle eine prägnante Zusammenfassung der wichtigsten Punkte.',
        'datum': 'Extrahiere das Datum aus dem Text. Falls kein Datum gefunden wird, verwende das aktuelle Datum.',
        'date': 'Extrahiere das Datum aus dem Text. Falls kein Datum gefunden wird, verwende das aktuelle Datum.',
        'titel': 'Extrahiere den Titel oder die Hauptüberschrift.',
        'title': 'Extrahiere den Titel oder die Hauptüberschrift.',
        'teilnehmer': 'Liste alle Teilnehmer oder Personen auf, die erwähnt werden.',
        'participants': 'Liste alle Teilnehmer oder Personen auf, die erwähnt werden.',
        'themen': 'Identifiziere die wichtigsten Themen oder Diskussionspunkte.',
        'topics': 'Identifiziere die wichtigsten Themen oder Diskussionspunkte.',
        'beschlüsse': 'Extrahiere alle Beschlüsse oder Entscheidungen.',
        'decisions': 'Extrahiere alle Beschlüsse oder Entscheidungen.',
        'aktionen': 'Identifiziere alle Aktionspunkte oder Aufgaben.',
        'actions': 'Identifiziere alle Aktionspunkte oder Aufgaben.',
        'nächste_schritte': 'Beschreibe die nächsten Schritte oder Folgeaktionen.',
        'next_steps': 'Beschreibe die nächsten Schritte oder Folgeaktionen.',
        'notizen': 'Extrahiere wichtige Notizen oder Anmerkungen.',
        'notes': 'Extrahiere wichtige Notizen oder Anmerkungen.',
        'protokoll': 'Erstelle ein strukturiertes Protokoll der Besprechung.',
        'protocol': 'Erstelle ein strukturiertes Protokoll der Besprechung.',
    }
    
    @staticmethod
    def generate_prompt(placeholder_name: str) -> str:
        """
        Generiert einen Standard-Prompt für einen Platzhalter
        
        Args:
            placeholder_name: Name des Platzhalters (normalisiert)
            
        Returns:
            Standard-Prompt-Text
        """
        # Normalisiere den Platzhalternamen (lowercase, ohne Sonderzeichen)
        normalized = placeholder_name.lower().strip()
        
        # Prüfe ob ein Standard-Prompt existiert
        if normalized in PromptGenerator.DEFAULT_PROMPTS:
            return PromptGenerator.DEFAULT_PROMPTS[normalized]
        
        # Fallback: Generischer Prompt basierend auf dem Namen
        # Ersetze Unterstriche durch Leerzeichen für bessere Lesbarkeit
        readable_name = normalized.replace('_', ' ').title()
        return f"Extrahiere oder erstelle den Wert für '{readable_name}' basierend auf dem Kontext der Transkription."
    
    @staticmethod
    def generate_prompts_for_placeholders(placeholders: set) -> Dict[str, str]:
        """
        Generiert Standard-Prompts für eine Menge von Platzhaltern
        
        Args:
            placeholders: Set von Platzhalternamen
            
        Returns:
            Dictionary mit Platzhalternamen als Keys und Prompts als Values
        """
        return {
            placeholder: PromptGenerator.generate_prompt(placeholder)
            for placeholder in placeholders
        }
