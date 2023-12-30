from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),

)

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Адрес почты')
    username = models.CharField(unique=True, verbose_name='Имя пользователя', max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, verbose_name='Тип пользователя',
                                 default='buyer')

    REQUIRED_FIELDS = ['username','first_name', 'last_name']
    objects = UserManager()
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"

    def __str__(self):
        return f'{self.first_name} {self.last_name}, магазин {self.username}'


class Shop(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    url = models.URLField(blank=True, null=True, verbose_name='ссылка')
    status = models.BooleanField(default=True, verbose_name='Статус приема заказов')
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"

    def __str__(self):
        return self.name


class Category(models.Model):
    shops = models.ManyToManyField(Shop, blank=True, verbose_name='categories', related_name='shop')
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE, related_name='product_infos',
                                blank=True)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', blank=True,
                             on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, verbose_name='Название')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Список информации о продукте"

    def __str__(self):
        return self.name


class Parameter(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название параметра')

    class Meta:
        verbose_name = 'Название параметра'
        verbose_name_plural = 'Список названий параметров'

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте', blank=True,
                                     on_delete=models.CASCADE, related_name='product_parameters')
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', on_delete=models.CASCADE, blank=True,
                                  related_name='product_parameters')
    value = models.CharField(max_length=100, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Список параметров'
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]

    def __str__(self):
        return f'{self.product_info.product.name} {self.parameter.name} {self.value}'


class Contact(models.Model):
    user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.city} {self.street}'


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='orders', blank=True,
                             on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATE_CHOICES, verbose_name='Статус')
    contact = models.ForeignKey(Contact, verbose_name='Контакт', blank=True, null=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказов'

    def __str__(self):
        return str(self.dt)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE, blank=True,
                              related_name='ordered_items')

    quantity = models.PositiveIntegerField(verbose_name='Количество')

    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте', related_name='ordered_items',
                                     blank=True,
                                     on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"

    def __str__(self):
        return f'{self.product_info.product.name} количество {self.quantity}'

