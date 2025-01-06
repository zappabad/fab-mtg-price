from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now, timedelta
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import CardData, PriceData
from .serializers import CardDataSerializer, PriceDataSerializer
from .utils import TCGPlayerFetcher

# Create your views here.
class CardDataViewSet(viewsets.ModelViewSet):
    queryset = CardData.objects.all()
    serializer_class = CardDataSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        query = request.data.get('query')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        fetcher = TCGPlayerFetcher(query)
        fetcher.fetch_data()
        
        lowest_price = fetcher.get_lowest_price()
        market_price = fetcher.get_market_price()
        card_data = fetcher.get_card_data().to_dict(orient='records')
        
        for card in card_data:
            card_instance, created = CardData.objects.update_or_create(
                product_name=card['productName'],
                defaults={
                    'product_line_name': card['productLineName'],
                    'set_name': card['setName']
                }
            )
            PriceData.objects.create(
                card=card_instance,
                price=lowest_price
            )
        
        return Response({'message': 'Data fetched and saved successfully'}, status=status.HTTP_201_CREATED)

class PriceDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PriceData.objects.all()
    serializer_class = PriceDataSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        card_id = self.request.query_params.get('card_id')
        if card_id:
            return PriceData.objects.filter(card_id=card_id).order_by('-created_at')[:1]
        return super().get_queryset()

    def retrieve(self, request, *args, **kwargs):
        card_id = kwargs.get('pk')
        card = get_object_or_404(CardData, id=card_id)
        latest_price_data = PriceData.objects.filter(card=card).order_by('-created_at').first()

        # Check if the data is older than a week
        if not latest_price_data or latest_price_data.created_at < now() - timedelta(days=7):
            # Fetch and update data
            fetcher = TCGPlayerFetcher(card.product_name)
            fetcher.fetch_data()

            # Update card data and price
            lowest_price = fetcher.get_lowest_price()
            card_data = fetcher.get_card_data().to_dict(orient='records')[0]  # Assuming one record
            card.product_line_name = card_data['productLineName']
            card.set_name = card_data['setName']
            card.save()

            # Add a new price entry
            PriceData.objects.create(card=card, price=lowest_price)

        # Return the latest price data
        serializer = self.get_serializer(latest_price_data)
        return Response(serializer.data)