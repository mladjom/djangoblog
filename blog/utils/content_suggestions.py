# blog/utils/content_suggestions.py
from django.core.exceptions import ValidationError
from collections import Counter
import spacy
from django.utils.text import slugify
from blog.models.category_model import Category
from blog.models.tag_model import Tag
from django.db.models import Q
from blog.settings import SPACY_SETTINGS

class ContentSuggestionSystem:
    def __init__(self, content, existing_tags=None, existing_categories=None):
        self.nlp = spacy.load(SPACY_SETTINGS['MODEL_NAME'])
        self.content = content
        self.existing_tags = existing_tags or []
        self.existing_categories = existing_categories or []
        self.doc = None
        
    def process_content(self):
        """Process the content with spaCy"""
        if not self.content:
            return
        
        # Clean and process the content
        clean_text = self._clean_text(self.content)
        self.doc = self.nlp(clean_text)
    
    def _clean_text(self, text):
        """Clean text before processing"""
        # Similar to the clean_html_content method from earlier
        from bs4 import BeautifulSoup
        from html import unescape
        import re
        
        # Remove HTML tags
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text(separator=' ')
        
        # Unescape HTML entities
        text = unescape(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def suggest_tags(self, max_suggestions=5, min_frequency=2):
        """Suggest tags based on content analysis"""
        if not self.doc:
            self.process_content()
            
        suggested_tags = []
        
        # Extract potential tags from different sources
        potential_tags = []
        
        # Add named entities
        potential_tags.extend([
            ent.text.lower() 
            for ent in self.doc.ents 
            if ent.label_ in ['ORG', 'PRODUCT', 'PERSON', 'GPE', 'TECH']
        ])
        
        # Add noun phrases
        potential_tags.extend([
            chunk.text.lower()
            for chunk in self.doc.noun_chunks
            if 2 <= len(chunk.text.split()) <= 3  # 2-3 word phrases
        ])
        
        # Add important single words (nouns, proper nouns)
        potential_tags.extend([
            token.text.lower()
            for token in self.doc
            if token.pos_ in ['NOUN', 'PROPN'] 
            and not token.is_stop
            and len(token.text) > 3
        ])
        
        # Count frequencies
        tag_counter = Counter(potential_tags)
        
        # Filter and sort suggestions
        for tag, freq in tag_counter.most_common():
            if freq < min_frequency:
                continue
                
            # Check if similar tag exists
            similar_existing = Tag.objects.filter(
                Q(name__iexact=tag) | 
                Q(name__icontains=tag) |
                Q(slug=slugify(tag))
            ).first()
            
            if similar_existing:
                if similar_existing not in self.existing_tags:
                    suggested_tags.append(('existing', similar_existing))
            else:
                suggested_tags.append(('new', {'name': tag, 'slug': slugify(tag)}))
                
            if len(suggested_tags) >= max_suggestions:
                break
                
        return suggested_tags
    
    def suggest_categories(self, max_suggestions=3):
        """Suggest categories based on content analysis"""
        if not self.doc:
            self.process_content()
            
        # Get main topics from the content
        topic_scores = {}
        
        # Analysis based on key sections of the text
        title_weight = 2.0
        first_para_weight = 1.5
        
        sentences = list(self.doc.sents)
        if not sentences:
            return []
            
        # Analyze title (first sentence) with higher weight
        title = sentences[0]
        self._score_sentence_topics(title, topic_scores, title_weight)
        
        # Analyze first paragraph with medium weight
        first_para = ' '.join(str(sent) for sent in sentences[1:3])
        first_para_doc = self.nlp(first_para)
        self._score_sentence_topics(first_para_doc, topic_scores, first_para_weight)
        
        # Analyze rest of content with normal weight
        for sent in sentences[3:]:
            self._score_sentence_topics(sent, topic_scores, 1.0)
            
        # Sort topics by score
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        
        suggested_categories = []
        
        for topic, score in sorted_topics[:max_suggestions]:
            # Check if similar category exists
            similar_existing = Category.objects.filter(
                Q(name__iexact=topic) |
                Q(name__icontains=topic) |
                Q(slug=slugify(topic))
            ).first()
            
            if similar_existing:
                if similar_existing not in self.existing_categories:
                    suggested_categories.append(('existing', similar_existing))
            else:
                suggested_categories.append(('new', {
                    'name': topic,
                    'slug': slugify(topic),
                    'description': f'Articles related to {topic}'
                }))
                
        return suggested_categories
    
    def _score_sentence_topics(self, doc, topic_scores, weight=1.0):
        """Score topics in a sentence"""
        # Score based on entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'PERSON', 'GPE', 'TECH']:
                topic = ent.text.lower()
                topic_scores[topic] = topic_scores.get(topic, 0) + (1 * weight)
        
        # Score based on noun phrases
        for chunk in doc.noun_chunks:
            if 1 <= len(chunk.text.split()) <= 2:  # 1-2 word phrases for categories
                topic = chunk.text.lower()
                topic_scores[topic] = topic_scores.get(topic, 0) + (0.5 * weight)