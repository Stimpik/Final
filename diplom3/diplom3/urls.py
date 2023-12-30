"""
URL configuration for diplom3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include, re_path

from dbackend.views import BaseUpdate, ShopsList, CategoryView, ProductView, ProductInShop, UserActivationView, \
    UserResetPasswordView, ChangeShopStatus, AboutProduct, Basket, PartnerOrders

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    # /users регистрация пользователя. /me информация о пользователе, изменение информации.


    re_path(r'^auth/', include('djoser.urls.authtoken')),
    # re_path(r'^/auth/token/login/', include('djoser.urls.authtoken')),  # получение токена

    re_path(r'^auth/request_activate/(?P<uid>[\w-]+)/(?P<token>[\w-]+)/$', UserActivationView.as_view()),
    # Подтверждение и активация пользователя по ссылке из письма.

    re_path(r'^auth/password-reset/(?P<uid>[\w-]+)/(?P<token>[\w-]+)/$', UserResetPasswordView.as_view()),
    # сброс пароля (необходимо передавать "new_password").

    path('update/', BaseUpdate.as_view()),  # обновить базу
    path('shops/', ShopsList.as_view()),  # все магазины
    path('shops/?status=True', ShopsList.as_view()),  # все магазины принимающие заказы
    path('categories/', CategoryView.as_view()),  # все категории
    path('products/', ProductView.as_view()),  # все продукты
    path('shop/<int:pk>/', ProductInShop.as_view()),  # все продукты в магазине
    path('shop_status/<int:pk>', ChangeShopStatus.as_view()),  # все продукты в магазине
    path('about_product/<int:pk>', AboutProduct.as_view()), # Информация о конкретном товаре
    path('basket/', Basket.as_view()),  # Корзина
    path('my_orders/', Basket.as_view()),  # Мои заказы
    path('byers_orders/', PartnerOrders.as_view()) # Получить заказы



]
