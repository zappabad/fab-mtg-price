from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardDataViewSet, PriceDataViewSet, card_search_view

router = DefaultRouter()
router.register(r'cards', CardDataViewSet, basename='carddata')
router.register(r'prices', PriceDataViewSet, basename='pricedata')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', card_search_view, name='card_search'),
]
