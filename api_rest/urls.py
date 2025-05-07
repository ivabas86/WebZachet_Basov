from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import restaurantViewSet, tableViewSet, BookingViewSet, RegisterView

router = DefaultRouter()
router.register(r'restaurant', restaurantViewSet, basename='restaurant')
router.register(r'tables', tableViewSet, basename='table')
router.register(r'bookings', BookingViewSet, basename='booking')


urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
