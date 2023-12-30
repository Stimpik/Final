import json

from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse

from requests import get, post
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import load, Loader
from rest_framework.decorators import (
    permission_classes,
)
from rest_framework import permissions

from dbackend.Permissions import OwnerPermission
from dbackend.models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter, Order, OrderItem
from dbackend.serializers import ShopSerializer, CategorySerializer, ProductSerializer, ProductInfoSerializer, \
    OrderItemSerializer, OrderSerializer


class BaseUpdate(APIView):
    '''
    Обновление базы
    '''

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Authorization is required'}, status=403)

        if request.user.user_type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Only with the "shop" status'}, status=403)

        url = request.data.get('url')

        if url == None:
            return JsonResponse({'error': 'No URL'})
        stream = get(url).content
        read_data = load(stream, Loader=Loader)
        for item in read_data.get('shop'):
            shop, created = Shop.objects.get_or_create(name=item['name'], url=item['url'], status=item['status'],
                                                       user_id=request.user.id)
        for category in read_data['categories']:
            category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()
        ProductInfo.objects.filter(shop_id=shop.id).delete()
        for item in read_data['goods']:
            product, created = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

            product_info = ProductInfo.objects.create(product_id=product.id,
                                                      name=item['model'],
                                                      price=item['price'],
                                                      price_rrc=item['price_rrc'],
                                                      quantity=item['quantity'],
                                                      shop_id=shop.id)
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(product_info_id=product_info.id,
                                                parameter_id=parameter_object.id,
                                                value=value)
        return JsonResponse({'status': 'created'})


class ShopsList(ListAPIView):
    '''
    Список магазинов
    '''
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    filterset_fields = ['status', ]


class CategoryView(ListAPIView):
    '''
    Список категорий
    '''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductView(ListAPIView):
    '''
    Список всех товаров
    '''
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductInShop(APIView):
    '''
    Список товаров в конкретном магазине
    '''

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        query = Q(shop_id=pk)
        try:
            queryset = ProductInfo.objects.filter(query)
            serializer = ProductInfoSerializer(queryset, many=True)
            return Response(serializer.data)
        except:
            return JsonResponse({'error': 'Shop not found'})


@permission_classes([permissions.AllowAny])
class UserActivationView(APIView):
    '''
    Активация пользователя через почту
    '''

    def get(self, request, uid, token):
        protocol = 'https://' if request.is_secure() else 'http://'
        web_url = protocol + request.get_host()
        post_url = web_url + "/auth/users/activation/"
        post_data = {'uid': uid, 'token': token}
        result = post(post_url, data=post_data)
        content = result.text
        return Response(content)


@permission_classes([permissions.AllowAny])
class UserResetPasswordView(APIView):
    '''
    Подтверждение восстановления пароля
    '''

    def get(self, request, uid, token):
        protocol = 'https://' if request.is_secure() else 'http://'
        web_url = protocol + request.get_host()
        post_url = web_url + "/auth/users/reset_password_confirm/"
        post_data = {'uid': uid, 'token': token}
        result = post(post_url, data=post_data)
        content = result.text
        return Response(content)


@permission_classes([IsAuthenticated, OwnerPermission, ])
class ChangeShopStatus(generics.UpdateAPIView):
    queryset = Shop
    serializer_class = ShopSerializer


class AboutProduct(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        queryset = ProductInfo.objects.filter(product_id=pk)
        if len(queryset) == 0:
            return JsonResponse({'error': f'Товар с id={pk} не найден'})
        serializer = ProductInfoSerializer(queryset, many=True)
        return Response(serializer.data)


class Basket(APIView):

    def post(self, request, *args, **kwargs):

        items_string = request.data.get('items')
        items_dict = json.loads(items_string)
        basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
        objects_created = 0
        for order_item in items_dict:
            order_item.update({'order': basket.id})
            serializer = OrderItemSerializer(data=order_item)
            if serializer.is_valid():
                try:
                    serializer.save()
                except IntegrityError as error:
                    return JsonResponse({'Status': False, 'Errors': str(error)})
                else:
                    objects_created += 1

            else:

                return JsonResponse({'Status': False, 'Errors': serializer.errors})
            return JsonResponse({'Status': True, 'Создано объектов': objects_created})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def delete(self, request, *args, **kwargs):

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def get(self, request, *args, **kwargs):
        basket = Order.objects.filter(
            user_id=request.user.id, status='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = json.loads(items_sting)
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, status='basket')
                objects_updated = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']).update(
                            quantity=order_item['quantity'])

                return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


@permission_classes([IsAuthenticated, OwnerPermission])
class GetMyOrder(ListAPIView):
    queryset = Order
    serializer_class = OrderSerializer


class PartnerOrders(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.user_type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(status='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)
