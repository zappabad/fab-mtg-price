from rest_framework import serializers
from .models import CardData, PriceData

class CardDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardData
        fields = '__all__'

class PriceDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PriceData
        fields = '__all__'
