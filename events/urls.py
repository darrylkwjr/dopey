from django.urls import path
from .views import ComedyEventsView

urlpatterns = [
    path('comedy-events/<str:state_code>/', ComedyEventsView.as_view(), name='comedy-events'),
]
