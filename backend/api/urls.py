from django.urls import path
from .views import (
    RegisterView, LoginView, RecoverAccountView, 
    PhotoUploadView, PhotoListView, PhotoDeleteView, UserTagView,
    PhotoUpdateView,
    PhotoEditView,
    update_photo_tags,
    AnalyzeTagsView,
    mcp_search
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('recover/', RecoverAccountView.as_view(), name='recover'),
    path('upload_photo/', PhotoUploadView.as_view(), name='upload_photo'),
    path('photos/', PhotoListView.as_view(), name='photo_list'),
    path('photos/<int:pk>/', PhotoDeleteView.as_view(), name='photo_delete'),
    path('photos/<int:pk>/update/', PhotoUpdateView.as_view(), name='photo_update'),
    path('photos/<int:pk>/edit-image/', PhotoEditView.as_view(), name='photo_edit_image'),
    path('photos/<int:pk>/analyze-tags/', AnalyzeTagsView.as_view(), name='photo_analyze_tags'),
    path('user_tags/', UserTagView.as_view(), name='user_tags'),
    path('update_photo_tags/', update_photo_tags, name='update_photo_tags'),
    path('search/mcp', mcp_search, name='mcp_search'),
]