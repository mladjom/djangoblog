import os
from django.conf import settings
from django.db import models
from blog.utils.image_utils import resize_and_compress_image, image_upload_path
from django.utils.text import slugify

class FeaturedImageModel(models.Model):
    featured_image = models.ImageField(
        upload_to=image_upload_path,
        blank=True,
        null=True,
        verbose_name="Featured Image"
    )

    class Meta:
        abstract = True

    def handle_old_featured_image(self):
        """
        Handle deletion of the old featured image if it is being replaced or cleared.
        """
        if self.pk:
            old_instance = type(self).objects.get(pk=self.pk)
            if old_instance.featured_image and old_instance.featured_image != self.featured_image:
                try:
                    os.remove(old_instance.featured_image.path)
                except FileNotFoundError:
                    pass  # File already removed

    def process_featured_image(self):
        """
        Rename, resize, and convert the uploaded image to .webp format.
        """
        if self.featured_image:
            original_image_path = self.featured_image.path
            slug_source = getattr(self, 'name', None) or getattr(self, 'title', None)
            new_filename = f"{slugify(slug_source)}.webp"
            new_image_path = os.path.join(os.path.dirname(original_image_path), new_filename)

            resize_and_compress_image(original_image_path, new_image_path)

            # Remove the original image if the path has changed
            if original_image_path != new_image_path and os.path.exists(original_image_path):
                os.remove(original_image_path)

            # Update the field to use the new image path
            self.featured_image.name = os.path.relpath(new_image_path, settings.MEDIA_ROOT)

    def save(self, *args, **kwargs):
        """
        Save the model, process the image, and handle image replacement or clearance.
        """
        is_new_instance = self.pk is None

        # Handle old image replacement or clearance
        if not is_new_instance:
            self.handle_old_featured_image()

        # Save the instance first to apply `upload_to` logic for new images
        super().save(*args, **kwargs)

        # Process the featured image after the initial save
        if self.featured_image:
            self.process_featured_image()
            super().save(update_fields=['featured_image'])

    def delete(self, *args, **kwargs):
        """
        Delete the associated image file when the model instance is deleted.
        """
        if self.featured_image and self.featured_image.name:  # Ensure the field is populated
            try:
                image_path = self.featured_image.path  # Get the file path
                if os.path.exists(image_path):
                    os.remove(image_path)  # Delete the file
            except Exception as e:
                print(f"Error deleting image: {e}")

        # Call the superclass delete method to remove the instance
        super().delete(*args, **kwargs)
