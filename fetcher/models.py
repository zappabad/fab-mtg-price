from django.db import models
import uuid
# Create your models here.


class CardData(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, unique=True, auto_created=True, default=uuid.uuid4)
    product_line_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    set_name = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    
    def __str__(self):
        return f"[{self.game.nickname}] {self.product_name}"

class PriceData(models.Model):
    card = models.ForeignKey(CardData, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card} - {self.price}"
