# blog/tests/utils/test_image.py
import pytest
import os
from django.conf import settings
from blog.models import Category
from blog.utils.image_utils import resize_and_compress_image
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

