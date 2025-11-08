"""
Utility-Modul für die Extraktion von Platzhaltern aus verschiedenen Dateiformaten
"""
import re
from typing import List, Set, Dict, Optional
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

class PlaceholderExtractor:
    """Extrahiert Platzhalter aus verschiedenen Dateiformaten"""
    
    # Regex-Pattern für Platzhalter im Format {{feldname}}
    PLACEHOLDER_PATTERN = re.compile(r'\{\{([^}]+)\}\}')
    
    @staticmethod
    def extract_from_text(text: str) -> Set[str]:
        """
        Extrahiert Platzhalter aus einem Text-String
        
        Args:
            text: Der Text, aus dem Platzhalter extrahiert werden sollen
            
        Returns:
            Set von Platzhalternamen (ohne {{}})
        """
        matches = PlaceholderExtractor.PLACEHOLDER_PATTERN.findall(text)
        # Entferne Leerzeichen und normalisiere
        placeholders = {match.strip() for match in matches if match.strip()}
        return placeholders
    
    @staticmethod
    def extract_from_docx(file_path: Path) -> Set[str]:
        """
        Extrahiert Platzhalter aus einer Word-Datei (.docx)
        
        Args:
            file_path: Pfad zur .docx-Datei
            
        Returns:
            Set von Platzhalternamen
        """
        try:
            from docx import Document
            
            doc = Document(file_path)
            all_text = []
            
            # Durchlaufe alle Absätze
            for paragraph in doc.paragraphs:
                all_text.append(paragraph.text)
            
            # Durchlaufe alle Tabellen
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        all_text.append(cell.text)
            
            # Durchlaufe Header und Footer
            for section in doc.sections:
                for header in section.header.paragraphs:
                    all_text.append(header.text)
                for footer in section.footer.paragraphs:
                    all_text.append(footer.text)
            
            text = '\n'.join(all_text)
            return PlaceholderExtractor.extract_from_text(text)
            
        except ImportError:
            logger.error("python-docx ist nicht installiert")
            raise ImportError("python-docx ist erforderlich für .docx-Unterstützung")
        except Exception as e:
            logger.error(f"Fehler beim Lesen der Word-Datei: {str(e)}")
            raise
    
    @staticmethod
    def extract_from_xlsx(file_path: Path) -> Set[str]:
        """
        Extrahiert Platzhalter aus einer Excel-Datei (.xlsx)
        
        Args:
            file_path: Pfad zur .xlsx-Datei
            
        Returns:
            Set von Platzhalternamen
        """
        try:
            from openpyxl import load_workbook
            
            workbook = load_workbook(file_path, data_only=True)
            all_text = []
            
            # Durchlaufe alle Arbeitsblätter
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                for row in sheet.iter_rows(values_only=True):
                    for cell_value in row:
                        if cell_value is not None:
                            all_text.append(str(cell_value))
            
            text = '\n'.join(all_text)
            return PlaceholderExtractor.extract_from_text(text)
            
        except ImportError:
            logger.error("openpyxl ist nicht installiert")
            raise ImportError("openpyxl ist erforderlich für .xlsx-Unterstützung")
        except Exception as e:
            logger.error(f"Fehler beim Lesen der Excel-Datei: {str(e)}")
            raise
    
    @staticmethod
    def extract_from_file(file_path: Path) -> Set[str]:
        """
        Extrahiert Platzhalter aus einer Datei basierend auf der Dateierweiterung
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Set von Platzhalternamen
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        if suffix == '.docx':
            return PlaceholderExtractor.extract_from_docx(file_path)
        elif suffix == '.xlsx':
            return PlaceholderExtractor.extract_from_xlsx(file_path)
        elif suffix in ['.md', '.txt', '.markdown']:
            # Für Text-Dateien einfach den Inhalt lesen
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return PlaceholderExtractor.extract_from_text(text)
        else:
            raise ValueError(f"Nicht unterstütztes Dateiformat: {suffix}")
