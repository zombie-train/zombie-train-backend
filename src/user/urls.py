"""
URL configuration for zombie_train_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from user import views
router = DefaultRouter()


router.register(r'users', views.UserViewSet)

urlpatterns = [
    re_path('profile/?$', views.UserProfileView.as_view(), name='user-profile'),
    re_path('profile/save/?$', views.UserSaveView.as_view(), name='user-save'),
    re_path('tg_users/?$', views.TelegramUserView.as_view(), name='telegram-users'),
    re_path('referrals/?$', views.ReferralView.as_view(), name='referral'),
    path('', include(router.urls)),
]
