from django.urls import path
from .views import RegisterView, LoginView, RecoverAccountView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('recover/', RecoverAccountView.as_view(), name='recover'),
]