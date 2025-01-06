from django.urls import path
from .views import CardDataView

urlpatterns = [
    path('card_data/', CardDataView.as_view(), name='card_data'),
]
