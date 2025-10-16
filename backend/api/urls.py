from django.urls import path
from .views import (
    RegisterView, LoginView, RecoverAccountView, 
    PhotoUploadView, PhotoListView, PhotoDeleteView, UserTagView,
    PhotoUpdateView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('recover/', RecoverAccountView.as_view(), name='recover'),
    path('upload_photo/', PhotoUploadView.as_view(), name='upload_photo'),
    path('photos/', PhotoListView.as_view(), name='photo_list'),
    path('photos/<int:pk>/', PhotoDeleteView.as_view(), name='photo_delete'),
    path('photos/<int:pk>/update/', PhotoUpdateView.as_view(), name='photo_update'),
    path('user_tags/', UserTagView.as_view(), name='user_tags'),
]