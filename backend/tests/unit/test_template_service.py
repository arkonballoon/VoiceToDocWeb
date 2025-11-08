"""
Unit-Tests für die TemplateService-Klasse
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
import uuid
import sys

# Import-Pfad anpassen für Tests
backend_src = Path(__file__).parent.parent.parent / "src"
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

from services.template_service import TemplateService, TemplateNotFoundError
from models.template import Template, TemplateUpdate
from utils.singleton import Singleton


@pytest.fixture
def reset_template_service_singleton():
    """Fixture zum Zurücksetzen des TemplateService Singleton vor/nach jedem Test"""
    # Vor dem Test: Singleton zurücksetzen
    if TemplateService in Singleton._instances:
        del Singleton._instances[TemplateService]
    if TemplateService in Singleton._initialized:
        del Singleton._initialized[TemplateService]
    
    yield
    
    # Nach dem Test: Singleton wieder zurücksetzen
    if TemplateService in Singleton._instances:
        del Singleton._instances[TemplateService]
    if TemplateService in Singleton._initialized:
        del Singleton._initialized[TemplateService]


@pytest.fixture
def mock_storage_adapter():
    """Fixture für gemockten Storage-Adapter"""
    mock_adapter = MagicMock()
    mock_adapter.save_template = AsyncMock()
    mock_adapter.get_templates = AsyncMock()
    mock_adapter.get_template = AsyncMock()
    mock_adapter.update_template = AsyncMock()
    mock_adapter.delete_template = AsyncMock()
    return mock_adapter


@pytest.fixture(autouse=True)
def mock_logger():
    """Fixture zum Mocken des Loggers (autouse=True bedeutet, dass es automatisch verwendet wird)"""
    with patch('services.template_service.logger') as mock_logger:
        yield mock_logger


@pytest.fixture
def sample_template_data():
    """Fixture für Test-Template-Daten"""
    template_id = str(uuid.uuid4())
    return {
        "id": template_id,
        "name": "Test Template",
        "content": "Template Content",
        "description": "Test Description",
        "created_at": datetime.now()
    }


@pytest.fixture
def sample_template_data_list(sample_template_data):
    """Fixture für Liste von Test-Template-Daten"""
    template_id_2 = str(uuid.uuid4())
    template_data_2 = {
        "id": template_id_2,
        "name": "Test Template 2",
        "content": "Template Content 2",
        "description": "Test Description 2",
        "created_at": datetime.now()
    }
    return [sample_template_data, template_data_2]


class TestSaveTemplate:
    """Tests für die save_template Methode"""
    
    @pytest.mark.asyncio
    @patch('services.template_service.StorageFactory.get_adapter')
    async def test_save_template(
        self, 
        mock_get_adapter, 
        mock_storage_adapter, 
        sample_template_data,
        reset_template_service_singleton
    ):
        """Testet das Speichern eines Templates"""
        # Mock StorageFactory
        mock_get_adapter.return_value = mock_storage_adapter
        mock_storage_adapter.save_template.return_value = sample_template_data
        
        # TemplateService initialisieren
        service = TemplateService()
        
        # Template speichern
        result = await service.save_template(
            name="Test Template",
            content="Template Content",
            description="Test Description"
        )
        
        # Verifizieren
        assert isinstance(result, Template)
        assert result.id == sample_template_data["id"]
        assert result.name == sample_template_data["name"]
        assert result.content == sample_template_data["content"]
        assert result.description == sample_template_data["description"]
        mock_storage_adapter.save_template.assert_called_once_with(
            "Test Template",
            "Template Content",
            "Test Description"
        )


class TestGetTemplates:
    """Tests für die get_templates Methode"""
    
    @pytest.mark.asyncio
    @patch('services.template_service.StorageFactory.get_adapter')
    async def test_get_templates(
        self,
        mock_get_adapter,
        mock_storage_adapter,
        sample_template_data_list,
        reset_template_service_singleton
    ):
        """Testet das Laden aller Templates"""
        # Mock StorageFactory
        mock_get_adapter.return_value = mock_storage_adapter
        mock_storage_adapter.get_templates.return_value = sample_template_data_list
        
        # TemplateService initialisieren
        service = TemplateService()
        
        # Templates laden
        result = await service.get_templates()
        
        # Verifizieren
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(t, Template) for t in result)
        assert result[0].name == sample_template_data_list[0]["name"]
        assert result[1].name == sample_template_data_list[1]["name"]
        mock_storage_adapter.get_templates.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('services.template_service.StorageFactory.get_adapter')
    async def test_get_templates_empty(
        self,
        mock_get_adapter,
        mock_storage_adapter,
        reset_template_service_singleton
    ):
        """Testet das Laden von Templates bei leerer Liste"""
        # Mock StorageFactory
        mock_get_adapter.return_value = mock_storage_adapter
        mock_storage_adapter.get_templates.return_value = []
        
        # TemplateService initialisieren
        service = TemplateService()
        
        # Templates laden
        result = await service.get_templates()
        
        # Verifizieren
        assert isinstance(result, list)
        assert len(result) == 0
        mock_storage_adapter.get_templates.assert_called_once()


class TestGetTemplateById:
    """Tests für die get_template Methode"""
    
    @pytest.mark.asyncio
    @patch('services.template_service.StorageFactory.get_adapter')
    async def test_get_template_by_id(
        self,
        mock_get_adapter,
        mock_storage_adapter,
        sample_template_data,
        reset_template_service_singleton
    ):
        """Testet das Laden eines einzelnen Templates anhand der ID"""
        # Mock StorageFactory
        mock_get_adapter.return_value = mock_storage_adapter
        mock_storage_adapter.get_templates.return_value = [sample_template_data]
        
        # TemplateService initialisieren
        service = TemplateService()
        
        # Template laden
        result = await service.get_template(sample_template_data["id"])
        
        # Verifizieren
        assert isinstance(result, Template)
        assert result.id == sample_template_data["id"]
        assert result.name == sample_template_data["name"]
        assert result.content == sample_template_data["content"]
        mock_storage_adapter.get_templates.assert_called()
    
    @pytest.mark.asyncio
    @patch('services.template_service.StorageFactory.get_adapter')
    async def test_get_template_not_found(
        self,
        mock_get_adapter,
        mock_storage_adapter,
        reset_template_service_singleton
    ):
        """Testet das Verhalten bei nicht gefundenem Template"""
        # Mock StorageFactory
        mock_get_adapter.return_value = mock_storage_adapter
        mock_storage_adapter.get_templates.return_value = []
        
        # TemplateService initialisieren
        service = TemplateService()
        
        # Template mit nicht existierender ID laden
        result = await service.get_template("non-existent-id")
        
        # Verifizieren
        assert result is None
        mock_storage_adapter.get_templates.assert_called()


class TestUpdateTemplate:
    """Tests für die update_template Methode"""
    
    @pytest.mark.asyncio
    @patch('services.template_service.StorageFactory.get_adapter')
    async def test_update_template(
        self,
        mock_get_adapter,
        mock_storage_adapter,
        sample_template_data,
        reset_template_service_singleton
    ):
        """Testet das Aktualisieren eines Templates"""
        # Mock StorageFactory
        mock_get_adapter.return_value = mock_storage_adapter
        mock_storage_adapter.get_templates.return_value = [sample_template_data]
        
        # Aktualisierte Template-Daten
        updated_data = sample_template_data.copy()
        updated_data["name"] = "Updated Template Name"
        updated_data["content"] = "Updated Content"
        mock_storage_adapter.update_template.return_value = updated_data
        
        # TemplateService initialisieren
        service = TemplateService()
        
        # Template aktualisieren
        template_update = TemplateUpdate(
            name="Updated Template Name",
            content="Updated Content"
        )
        result = await service.update_template(
            sample_template_data["id"],
            template_update
        )
        
        # Verifizieren
        assert isinstance(result, Template)
        assert result.id == sample_template_data["id"]
        assert result.name == "Updated Template Name"
        assert result.content == "Updated Content"
        mock_storage_adapter.get_templates.assert_called()
        mock_storage_adapter.update_template.assert_called_once()
        call_args = mock_storage_adapter.update_template.call_args
        assert call_args[1]["template_id"] == sample_template_data["id"]
        assert "name" in call_args[1]["updates"]
        assert "content" in call_args[1]["updates"]
    
    @pytest.mark.asyncio
    @patch('services.template_service.StorageFactory.get_adapter')
    async def test_update_template_not_found(
        self,
        mock_get_adapter,
        mock_storage_adapter,
        reset_template_service_singleton
    ):
        """Testet das Update-Verhalten bei nicht existierendem Template"""
        # Mock StorageFactory
        mock_get_adapter.return_value = mock_storage_adapter
        mock_storage_adapter.get_templates.return_value = []
        
        # TemplateService initialisieren
        service = TemplateService()
        
        # Template-Update erstellen
        template_update = TemplateUpdate(name="Updated Name")
        
        # Verifizieren, dass TemplateNotFoundError geworfen wird
        with pytest.raises(TemplateNotFoundError) as exc_info:
            await service.update_template("non-existent-id", template_update)
        
        assert "nicht gefunden" in str(exc_info.value)
        mock_storage_adapter.get_templates.assert_called()
        mock_storage_adapter.update_template.assert_not_called()


class TestDeleteTemplate:
    """Tests für die delete_template Methode"""
    
    @pytest.mark.asyncio
    @patch('services.template_service.StorageFactory.get_adapter')
    async def test_delete_template(
        self,
        mock_get_adapter,
        mock_storage_adapter,
        sample_template_data,
        reset_template_service_singleton
    ):
        """Testet das Löschen eines Templates"""
        # Mock StorageFactory
        mock_get_adapter.return_value = mock_storage_adapter
        mock_storage_adapter.get_templates.return_value = [sample_template_data]
        mock_storage_adapter.delete_template.return_value = True
        
        # TemplateService initialisieren
        service = TemplateService()
        
        # Template löschen
        await service.delete_template(sample_template_data["id"])
        
        # Verifizieren
        mock_storage_adapter.get_templates.assert_called()
        mock_storage_adapter.delete_template.assert_called_once_with(
            sample_template_data["id"]
        )
    
    @pytest.mark.asyncio
    @patch('services.template_service.StorageFactory.get_adapter')
    async def test_delete_template_not_found(
        self,
        mock_get_adapter,
        mock_storage_adapter,
        reset_template_service_singleton
    ):
        """Testet das Lösch-Verhalten bei nicht existierendem Template"""
        # Mock StorageFactory
        mock_get_adapter.return_value = mock_storage_adapter
        mock_storage_adapter.get_templates.return_value = []
        
        # TemplateService initialisieren
        service = TemplateService()
        
        # Verifizieren, dass TemplateNotFoundError geworfen wird
        with pytest.raises(TemplateNotFoundError) as exc_info:
            await service.delete_template("non-existent-id")
        
        assert "nicht gefunden" in str(exc_info.value)
        mock_storage_adapter.get_templates.assert_called()
        mock_storage_adapter.delete_template.assert_not_called()


class TestSingletonPattern:
    """Tests für das Singleton-Pattern"""
    
    @patch('services.template_service.StorageFactory.get_adapter')
    def test_singleton_pattern(
        self,
        mock_get_adapter,
        mock_storage_adapter,
        reset_template_service_singleton
    ):
        """Testet das Singleton-Verhalten der TemplateService-Klasse"""
        # Mock StorageFactory
        mock_get_adapter.return_value = mock_storage_adapter
        
        # Erstelle zwei Instanzen
        service1 = TemplateService()
        service2 = TemplateService()
        
        # Verifizieren, dass beide Instanzen identisch sind
        assert service1 is service2
        
        # Verifizieren, dass _init nur einmal aufgerufen wurde
        # (StorageFactory.get_adapter sollte nur einmal aufgerufen werden)
        assert mock_get_adapter.call_count == 1
        
        # Verifizieren, dass beide Instanzen denselben Storage-Adapter haben
        assert service1.storage is service2.storage

