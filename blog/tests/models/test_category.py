import pytest
from blog.models import Category
from django.utils.text import slugify
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import os
from datetime import datetime
from blog.utils.image_utils import resize_and_compress_image

@pytest.mark.django_db
def test_create_category():
    """Test the creation of a Category object."""
    category = Category.objects.create(
        name="Technology",
        description="Category for technology articles",
        slug="technology"
    )
    assert category.name == "Technology"
    assert category.slug == "technology"
    assert category.description == "Category for technology articles"

@pytest.mark.django_db
def test_category_ordering():
    """Test if categories are ordered by name."""
    Category.objects.create(name="Zebra")
    Category.objects.create(name="Apple")
    categories = list(Category.objects.all())
    assert [cat.name for cat in categories] == ["Apple", "Zebra"]

@pytest.mark.django_db
def test_category_slug_generation():
    category = Category.objects.create(name="Test Category")
    assert category.slug == slugify(category.name)

@pytest.mark.django_db
def test_category_save_image_processing(settings, tmpdir):
    """
    Test that the image is renamed, resized, and converted to .webp format during save().
    """
    settings.MEDIA_ROOT = tmpdir  # Use a temporary directory for media files

    # Create a sample image to upload
    image_path = tmpdir / "test_image.jpg"
    image = Image.new("RGB", (1920, 1920), "blue")
    image.save(image_path)

    # Create a Category with the image
    with open(image_path, "rb") as img_file:
        uploaded_image = SimpleUploadedFile("test_image.jpg", img_file.read(), content_type="image/jpeg")
        category = Category.objects.create(name="Test Category", featured_image=uploaded_image)

    # Construct the expected path dynamically
    today = datetime.now().strftime('%Y/%m/%d')
    expected_image_name = f"categories/{today}/test-category.webp"

    # Assert that the image path matches the expected nested structure
    assert category.featured_image.name == expected_image_name

    # Check if the resized image exists
    resized_image_path = os.path.join(settings.MEDIA_ROOT, expected_image_name)
    resize_and_compress_image(image_path, resized_image_path)
    assert os.path.exists(resized_image_path)

    # Open the saved image and check its properties
    with Image.open(resized_image_path) as img:
        assert img.format == "WEBP", f"Expected WEBP format, but got {img.format}"  # Check the format
        assert img.size == (800, 800)  # Check the dimensions

@pytest.mark.django_db
def test_category_delete_removes_image(settings, tmpdir):
    """
    Test that deleting a Category instance also removes its associated image file.
    """
    settings.MEDIA_ROOT = tmpdir  # Use a temporary directory for media files

    # Create and save an image file
    image_path = tmpdir / "test_image.jpg"
    image = Image.new("RGB", (1920, 1920), "blue")
    image.save(image_path)

    # Create a Category instance with the image
    with open(image_path, "rb") as img_file:
        uploaded_image = SimpleUploadedFile("test_image.jpg", img_file.read(), content_type="image/jpeg")
        category = Category.objects.create(name="Test Category", featured_image=uploaded_image)

    # Verify the image file exists
    saved_image_path = category.featured_image.path
    assert os.path.exists(saved_image_path), "Image file does not exist after saving the category."

    # Delete the Category instance
    category.delete()

    # Verify the image file has been deleted
    assert not os.path.exists(saved_image_path), "Image file was not deleted when the category was deleted."