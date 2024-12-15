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

    def process_featured_image(self):
        """
        Rename, resize, and convert the uploaded image to .webp format.
        """
        if self.featured_image:
            original_image_path = self.featured_image.path
            
            # Generate the new filename based on the model name or title
            slug_source = getattr(self, 'name', None) or getattr(self, 'title', None)
            new_filename = f"{slugify(slug_source)}.webp"
            new_image_path = os.path.join(os.path.dirname(original_image_path), new_filename)

            # Resize and compress image
            resize_and_compress_image(original_image_path, new_image_path)

            # Remove the original image if the path has changed
            if original_image_path != new_image_path and os.path.exists(original_image_path):
                os.remove(original_image_path)

            # Update the field to use the new image path
            self.featured_image.name = os.path.relpath(new_image_path, settings.MEDIA_ROOT)

    def save(self, *args, **kwargs):
        """
        Save the model and process the image.
        """
        # Check if this is an update (not a new instance)
        is_new_instance = self.pk is None
        old_featured_image_path = None

        # Handle the replacement of an existing image
        if not is_new_instance:
            old_instance = type(self).objects.get(pk=self.pk)
            old_featured_image_path = old_instance.featured_image.path if old_instance.featured_image else None

        # Save the instance first (to apply `upload_to` logic if new image is uploaded)
        super().save(*args, **kwargs)

        # Process the featured image if it's uploaded or replaced
        if self.featured_image:
            self.process_featured_image()
            super().save(update_fields=['featured_image'])  # Save again to persist changes

        # Remove the old image file if a new image was uploaded
        if old_featured_image_path and old_featured_image_path != self.featured_image.path:
            if os.path.exists(old_featured_image_path):
                os.remove(old_featured_image_path)

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
