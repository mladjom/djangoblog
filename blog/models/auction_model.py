# auctions/models.py
from django.db import models

class Auction(models.Model):
    auction_id = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=20)
    status = models.CharField(max_length=50)
    title = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    detail_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['auction_id']),
            models.Index(fields=['start_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.code} - {self.title[:50]}"