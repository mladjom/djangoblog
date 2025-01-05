# blog/utils/spacy_utils.py
import spacy
from django.core.cache import cache
from functools import lru_cache
from blog.settings import SPACY_SETTINGS

@lru_cache(maxsize=1)
def get_spacy_model():
    """Get or load spaCy model with caching"""
    return spacy.load(SPACY_SETTINGS['MODEL_NAME'])

def get_sentence_importance(doc):
    """Calculate importance score for each sentence based on token importance"""
    scores = {}
    
    for sent in doc.sents:
        # Calculate score based on named entities, noun phrases, and other important tokens
        score = 0
        
        # Add score for named entities
        score += len([ent for ent in sent.ents])
        
        # Add score for noun chunks
        score += len([chunk for chunk in sent.noun_chunks])
        
        # Add score for important POS tags
        important_pos = {'NOUN', 'PROPN', 'VERB'}
        score += len([token for token in sent if token.pos_ in important_pos])
        
        scores[sent] = score
    
    return scores