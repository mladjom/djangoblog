# blog/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.utils.text import slugify
from blog.models.category_model import Category
from blog.models.tag_model import Tag
from blog.models.article_model import Article
from blog.models.featured_image_model import FeaturedImage
import logging
import random
import string
from django.db import transaction

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **kwargs):
        self.seed_categories()
        tags = self.seed_tags()
        self.seed_articles(tags)
        self.stdout.write(self.style.SUCCESS("Successfully seeded the database!"))

    def seed_categories(self):
        """Create sample categories"""
        self.stdout.write("Creating Categories...")
        categories = []
        for _ in range(5):  # Create 5 categories
            try:
                category = Category.objects.create(
                    name=fake.unique.word().capitalize(),
                    description=fake.sentence(),
                    slug=fake.unique.slug(),
                )
                categories.append(category)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating category: {e}"))
        return categories

    def seed_tags(self):
        """Create sample tags"""
        self.stdout.write("Creating Tags...")
        tags = []
        for _ in range(10):  # Create 10 tags
            try:
                tag = Tag.objects.create(
                    name=fake.unique.word().capitalize(),
                    description=fake.sentence(),
                    slug=fake.unique.slug(),
                )
                tags.append(tag)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating tag: {e}"))
        return tags

    def seed_articles(self, tags):
        """Create sample articles and associate with tags and categories"""
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(self.style.ERROR("No categories found. Cannot create articles."))
            return

        self.stdout.write("Creating Articles...")
        for _ in range(20):  # Create 20 articles
            try:
                article = Article.objects.create(
                    title=fake.sentence(),
                    content=fake.paragraph(nb_sentences=10),
                    category=random.choice(categories),
                    is_published=random.choice([True, False]),
                    is_featured=random.choice([True, False]),
                )
                article.tags.set(random.sample(tags, random.randint(1, 5)))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating article: {e}"))
