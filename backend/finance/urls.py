from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TransactionViewSet

# DRF Router automatically generates all CRUD URLs
router = DefaultRouter()
router.register(r'categories',   CategoryViewSet,   basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]