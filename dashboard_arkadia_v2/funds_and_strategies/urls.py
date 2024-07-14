from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('save-fund/', views.save_fund, name='save_fund'),
    path('save-strategy/', views.save_strategy, name='save_strategy'),
    path('save-api-keys/', views.save_api_keys, name='save_api_keys'),
    path('update-assets/', views.update_assets, name='update_assets'),
    path('save-wallet/', views.save_wallet, name='save_wallet'),
]