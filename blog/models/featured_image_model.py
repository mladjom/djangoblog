# blog/models/featured_image_model.py
import os
from django.conf import settings
from blog.utils.image_utils import resize_and_compress_image, image_upload_path
from django.utils.text import slugify
from django.db import models

class FeaturedImage(models.Model):
    featured_image = models.ImageField(
        upload_to=image_upload_path,
        blank=True,
        null=True,
        verbose_name="Featured Image"
    )

    def process_featured_image(self):
        if self.featured_image:
            original_image_path = self.featured_image.path
            new_filename = f"{slugify(self.name)}.webp"
            new_image_path = os.path.join(os.path.dirname(original_image_path), new_filename)

            resize_and_compress_image(original_image_path, new_image_path)

            # Remove the original image
            if os.path.exists(original_image_path) and original_image_path != new_image_path:
                os.remove(original_image_path)

            # Update the image field with the new path
            self.featured_image.name = os.path.relpath(new_image_path, settings.MEDIA_ROOT)

    class Meta:
        abstract = True  # Ensure this model is not created in the database
