import graphene
from graphene_django.types import DjangoObjectType
from graphene.relay import Connection, ConnectionField
from .models import Category, Tag, Article

# Define GraphQL types for each model
class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'slug')  # Expose these fields


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'description', 'slug', 'meta_title', 'meta_description', 'featured_image')

class Query(graphene.ObjectType):
    all_tags = graphene.List(TagType)
    tag_by_slug = graphene.Field(TagType, slug=graphene.String(required=True))

    def resolve_all_tags(root, info):
        return Tag.objects.all()

    def resolve_tag_by_slug(root, info, slug):
        try:
            return Tag.objects.get(slug=slug)
        except Tag.DoesNotExist:
            return None


class ArticleType(DjangoObjectType):
    class Meta:
        model = Article
        fields = (
            'id',
            'title',
            'content',
            'slug',
            'category',
            'tags',
            'is_published',
            'is_featured',
            'created_at',
            'modified_at',
        )

# Define a connection for Articles to enable pagination
class ArticleConnection(Connection):
    class Meta:
        node = ArticleType

# Define the Query class with pagination for Articles
class Query(graphene.ObjectType):
    # Define paginated query for articles
    all_categories = graphene.List(CategoryType)
    all_tags = graphene.List(TagType)
    all_articles = ConnectionField(ArticleConnection)  # Using ConnectionField for pagination
    # all_articles = graphene.List(
    #     ArticleType,
    #     first=graphene.Int(),
    #     skip=graphene.Int(),
    # )
    
    article_by_slug = graphene.Field(ArticleType, slug=graphene.String(required=True))

    # Resolvers
    def resolve_all_categories(root, info):
        return Category.objects.all()

    def resolve_all_tags(root, info):
        return Tag.objects.all()

    def resolve_all_articles(self, info, **kwargs):
        return  Article.objects.filter(is_published=True)  # Only fetch published articles


    def resolve_article_by_slug(root, info, slug):
        print(f'Received slug: {slug}')  # Debugging
        try:
            # Fetch the article based on the slug
            return Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return None  # Return None if article with slug doesn't exist


# Define the schema
schema = graphene.Schema(query=Query)
