from django.urls import path
from .views import TokenObtainPairView, TokensRefreshView

urlpatterns = [
    path('token/get/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokensRefreshView.as_view(), name='token_refresh'),
]