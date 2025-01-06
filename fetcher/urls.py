from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardDataViewSet, PriceDataViewSet

router = DefaultRouter()
router.register(r'cards', CardDataViewSet, basename='carddata')
router.register(r'prices', PriceDataViewSet, basename='pricedata')

urlpatterns = [
    path('', include(router.urls)),
]
