from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import CardData
from .utils import TCGPlayerFetcher

# Create your views here.

class CardDataView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        cards = CardData.objects.all().values()
        return Response(cards, status=status.HTTP_200_OK)

    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        fetcher = TCGPlayerFetcher(query)
        fetcher.fetch_data()
        
        lowest_price = fetcher.get_lowest_price()
        market_price = fetcher.get_market_price()
        card_data = fetcher.get_card_data().to_dict(orient='records')
        
        for card in card_data:
            CardData.objects.update_or_create(
                product_name=card['productName'],
                defaults={
                    'product_line_name': card['productLineName'],
                    'set_name': card['setName'],
                    'lowest_price': lowest_price,
                    'market_price': market_price
                }
            )
        
        return Response({'message': 'Data fetched and saved successfully'}, status=status.HTTP_201_CREATED)
