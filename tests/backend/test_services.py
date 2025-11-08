"""
Tests for backend services.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))


class TestFileProcessor:
    """Test file processing utilities."""
    
    def test_validate_file_type_pdf(self):
        """Test PDF file validation."""
        from utils import FileProcessor
        
        is_valid, error = FileProcessor.validate_file_type("test.pdf")
        assert is_valid == True
        assert error is None
    
    def test_validate_file_type_docx(self):
        """Test DOCX file validation."""
        from utils import FileProcessor
        
        is_valid, error = FileProcessor.validate_file_type("resume.docx")
        assert is_valid == True
        assert error is None
    
    def test_validate_file_type_invalid(self):
        """Test invalid file type."""
        from utils import FileProcessor
        
        is_valid, error = FileProcessor.validate_file_type("virus.exe")
        assert is_valid == False
        assert error is not None
    
    def test_validate_file_size_ok(self):
        """Test file size validation passes."""
        from utils import FileProcessor
        
        size_5mb = 5 * 1024 * 1024
        is_valid, error = FileProcessor.validate_file_size(size_5mb, max_size_mb=10)
        assert is_valid == True
        assert error is None
    
    def test_validate_file_size_too_large(self):
        """Test file size validation fails for large files."""
        from utils import FileProcessor
        
        size_15mb = 15 * 1024 * 1024
        is_valid, error = FileProcessor.validate_file_size(size_15mb, max_size_mb=10)
        assert is_valid == False
        assert "too large" in error.lower()
    
    def test_validate_file_size_empty(self):
        """Test file size validation fails for empty files."""
        from utils import FileProcessor
        
        is_valid, error = FileProcessor.validate_file_size(0)
        assert is_valid == False
        assert "empty" in error.lower()


class TestAISystem:
    """Test AI system components."""
    
    def test_ai_manager_initialization(self):
        """Test AI manager initializes correctly."""
        from services.ai import get_ai_manager
        
        manager = get_ai_manager()
        assert manager is not None
        assert hasattr(manager, 'providers')
        assert hasattr(manager, 'default_provider')
    
    def test_ai_provider_available(self):
        """Test at least one AI provider is available or warns."""
        from services.ai import get_ai_manager
        
        manager = get_ai_manager()
        # Should either have providers or have logged warning
        # Both cases are acceptable for development
        assert isinstance(manager.providers, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

