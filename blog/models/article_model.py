from django.db import models
from django.utils.translation import gettext_lazy as _
from .category_model import Category
from .tag_model import Tag
from django.urls import reverse
from .featured_image_model import FeaturedImageModel
from .base_model import BaseModelWithSlug
from django.utils.text import Truncator
import spacy
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup
import re
from html import unescape
from blog.settings import SPACY_SETTINGS

class Article(BaseModelWithSlug, FeaturedImageModel):
    title = models.CharField(max_length=255, unique=True, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))
    excerpt = models.TextField(blank=True, verbose_name=_('Excerpt'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles', verbose_name=_('Category'))
    tags = models.ManyToManyField(Tag, related_name='articles', verbose_name=_('Tags'))
    is_published = models.BooleanField(default=False, verbose_name=_('Is Published'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Is Featured'))

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

    source_field = 'title'  # Define the source field for the slug

    def get_absolute_url(self):
        return reverse('article-detail', args=[self.slug])

    def update_search_index(self):
        # Logic to update search index goes here
        pass

    @property
    def seo_meta_description(self):
        """
        Use `meta_description` if defined; otherwise, generate a default description.
        """
        return self.meta_description or f"Read about {self.title} and explore related insights."

    def __str__(self):
        return self.title

    def clean_html_content(self, content):
        """Remove HTML tags and clean up text"""
        # Remove HTML tags
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator=' ')
        
        # Unescape HTML entities
        text = unescape(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def generate_excerpt(self, max_words=55):
        """Generate excerpt using spaCy"""
        if not self.content:
            return ""

        try:
            # Load spaCy model
            nlp = spacy.load(SPACY_SETTINGS['MODEL_NAME'])
            
            # Clean content
            clean_text = self.clean_html_content(self.content)
            
            # Process the text
            doc = nlp(clean_text)
            
            # Get sentences and their importance scores
            sentences = list(doc.sents)
            if not sentences:
                return ""

            # Take first few sentences that fit within word limit
            excerpt = []
            word_count = 0
            
            for sent in sentences:
                sent_words = len(sent.text.split())
                if word_count + sent_words <= SPACY_SETTINGS['EXCERPT_MAX_WORDS']:
                    excerpt.append(sent.text)
                    word_count += sent_words
                else:
                    break
            
            return ' '.join(excerpt).strip()

        except Exception as e:
            raise ValidationError(f"Error generating excerpt: {str(e)}")

    def generate_meta_description(self, max_chars=160):
        """Generate meta description using spaCy"""
        if not self.content:
            return ""

        try:
            # Load spaCy model
            nlp = spacy.load(SPACY_SETTINGS['MODEL_NAME'])
            
            # Clean content
            clean_text = self.clean_html_content(self.content)
            
            # Process the text
            doc = nlp(clean_text)
            
            # Get the most important sentence based on token importance
            sentences = list(doc.sents)
            if not sentences:
                return ""

            # Use the first sentence that's under the character limit
            for sent in sentences:
                if len(sent.text) <= SPACY_SETTINGS['META_DESCRIPTION_MAX_CHARS']:
                    return sent.text.strip()
            
            # If no sentence is short enough, truncate the first sentence
            first_sent = sentences[0].text.strip()
            if len(first_sent) > SPACY_SETTINGS['META_DESCRIPTION_MAX_CHARS'] - 3:
                return first_sent[:SPACY_SETTINGS['META_DESCRIPTION_MAX_CHARS'] - 3] + "..."

                
            return first_sent

        except Exception as e:
            raise ValidationError(f"Error generating meta description: {str(e)}")

    def save(self, *args, **kwargs):
        # Generate excerpt if not provided
        if not self.excerpt:
            self.excerpt = self.generate_excerpt()
        
        # Generate meta description if not provided
        if not self.meta_description:
            self.meta_description = self.generate_meta_description()
            
        super().save(*args, **kwargs)
