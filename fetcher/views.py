from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now, timedelta
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from .models import CardData, PriceData
from .serializers import CardDataSerializer, PriceDataSerializer
from .filters import CardDataFilter, PriceDataFilter
from .utils import TCGPlayerFetcher

# Create your views here.
def card_search_view(request):
    return render(request, 'card_search.html')

class CardDataViewSet(viewsets.ModelViewSet):
    queryset = CardData.objects.all()
    serializer_class = CardDataSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product_line_name', 'set_name', 'product_name']

    def create(self, request, *args, **kwargs):
        query = request.data.get('product_name')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        fetcher = TCGPlayerFetcher(query)
        fetcher.fetch_data()
        
        lowest_price = fetcher.get_lowest_price()
        market_price = fetcher.get_market_price()
        card_data = fetcher.get_card_data()
        if card_data.empty:
            return Response({'error': 'No card found for the given query'}, status=status.HTTP_404_NOT_FOUND)
        else:
            matched_card = card_data.iloc[0]
        
        card_instance, created = CardData.objects.update_or_create(
            product_name=matched_card['productName'],
            defaults={
                'product_line_name': matched_card['productLineName'],
                'set_name': matched_card['setName']
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
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        card_id = self.request.query_params.get('uuid')
        if (card_id):
            return PriceData.objects.filter(carddata__uuid=card_id).order_by('-created_at')[:1]
        return super().get_queryset()

    def retrieve(self, request, *args, **kwargs):
        card_id = kwargs.get('pk')
        card = get_object_or_404(CardData, uuid=card_id)
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