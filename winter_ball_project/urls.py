"""
URL configuration for winter_ball_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# --- ЕДИНЫЙ, ЧИСТЫЙ И ЯВНЫЙ ИМПОРТ ВСЕХ VIEWS ---
from mainapp.views import (
    # Основные страницы
    index_view,
    auction_list_view,
    policy_view,
    post_detail_view,
    history_view,
    media_gallery_view,
    lot_detail_view,

    # API для постов
    create_post_api,
    update_post_api,

    # API для заявок
    create_lot_request_view,
    get_lot_request_details_api,
    process_lot_request_api,

    # API для ставок
    create_bid_view
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Основные страницы
    path('', index_view, name='index'),
    path('auction/', auction_list_view, name='auction'),
    path('policy/', policy_view, name='policy'),
    path('post/<int:pk>/', post_detail_view, name='post-detail'),
    path('history/', history_view, name='history'),
    path('media-gallery/', media_gallery_view, name='media-gallery'),
    path('lot/<int:lot_id>/', lot_detail_view, name='lot-detail'),

    # API
    path('api/post/create/', create_post_api, name='api-create-post'),
    path('api/post/<int:post_id>/update/', update_post_api, name='api-update-post'),
    path('api/lot-request/create/', create_lot_request_view, name='api-create-lot-request'),
    path('api/lot-request/<int:request_id>/details/', get_lot_request_details_api, name='api-get-lot-request-details'),
    path('api/lot-request/<int:request_id>/process/', process_lot_request_api, name='api-process-lot-request'),
    path('api/lot/<int:lot_id>/bid/create/', create_bid_view, name='api-create-bid'),
]

# Добавляем обработку медиа и статики для режима разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)