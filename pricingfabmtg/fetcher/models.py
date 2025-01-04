from django.db import models
import uuid
# Create your models here.

class CardData(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, unique=True, auto_created=True, default=uuid.uuid4)
    product_line_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    set_name = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2)
    market_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product_name
