import django_filters
from .models import CardData, PriceData

class CardDataFilter(django_filters.FilterSet):
    class Meta:
        model = CardData
        fields = '__all__'
        
class PriceDataFilter(django_filters.FilterSet):
    class Meta:
        model = PriceData
        fields = '__all__'