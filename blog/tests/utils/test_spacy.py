import pytest
from unittest.mock import patch, MagicMock
from blog.utils.spacy_utils import get_spacy_model, get_sentence_importance
from spacy.tokens import Doc, Span, Token

# Mock spaCy model for testing
@pytest.fixture
def mock_spacy_model():
    """Fixture to mock spaCy model."""
    mock_nlp = MagicMock()
    mock_doc = MagicMock(spec=Doc)
    
    # Mock sentences and entities
    mock_sent = MagicMock()
    mock_sent.ents = [MagicMock()]
    mock_sent.noun_chunks = [MagicMock()]
    
    # Create mock tokens
    mock_token = MagicMock(spec=Token)
    mock_token.pos_ = 'NOUN'
    
    mock_sent.__iter__.return_value = [mock_token]
    mock_doc.sents = [mock_sent]
    
    mock_nlp.return_value = mock_doc
    return mock_nlp

class TestSpacyUtils:
    
    @patch('blog.utils.spacy_utils.spacy.load')
    def test_get_spacy_model(self, mock_spacy_load):
        """Test get_spacy_model function."""
        # Mock the spaCy model load function
        mock_spacy_load.return_value = MagicMock()

        # Call the function
        model = get_spacy_model()

        # Check that the model was loaded
        mock_spacy_load.assert_called_once_with('en_core_web_sm')  # Use your model's name from SPACY_SETTINGS

        # Call the function again and verify that the model is cached
        model2 = get_spacy_model()
        assert model is model2  # They should be the same (cached)

    def test_get_sentence_importance(self, mock_spacy_model):
        """Test get_sentence_importance function."""
        # Patch spaCy model loading
        with patch('blog.utils.spacy_utils.get_spacy_model', return_value=mock_spacy_model):
            doc = mock_spacy_model("Test sentence with some entities and noun chunks.")
            
            # Call the function
            scores = get_sentence_importance(doc)
            
            # Test the result
            assert isinstance(scores, dict)
            assert len(scores) == 1  # Only one sentence
            assert list(scores.values())[0] > 0  # The score should be positive since we have entities, noun chunks, and important tokens

    @patch('blog.utils.spacy_utils.get_spacy_model')
    def test_get_sentence_importance_no_entities(self, mock_get_spacy_model):
        """Test get_sentence_importance with no entities."""
        # Create a doc with no entities
        mock_doc = MagicMock(spec=Doc)
        mock_sent = MagicMock()
        mock_sent.ents = []
        mock_sent.noun_chunks = [MagicMock()]
        mock_token = MagicMock(spec=Token)
        mock_token.pos_ = 'NOUN'
        mock_sent.__iter__.return_value = [mock_token]
        mock_doc.sents = [mock_sent]
        
        mock_get_spacy_model.return_value = mock_doc
        
        # Call the function
        scores = get_sentence_importance(mock_doc)
        
        # Test the result
        assert isinstance(scores, dict)
        assert list(scores.values())[0] > 0  # The score should still be positive based on noun chunks and POS tags

