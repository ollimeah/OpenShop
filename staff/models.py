from storefront.forms import AddCollectionToBasketForm, AddProductToBasketForm
from django.db import models
import json
from django.utils import timezone
from decimal import Decimal
from django.forms.models import model_to_dict
from datetime import date

class Settings():
    def __init__(self):
        try:
            with open("staff/settings.json", "r") as settings_file: 
                settings = json.load(settings_file)
                self.shop_name = settings['shop_name']
                self.primary_colour = settings['primary_colour']
                self.secondary_colour = settings['secondary_colour']
                self.logo = settings['logo']
                self.carousel = settings['carousel']
        except:
            self.shop_name = "No Name"
            self.primary_colour = "#c1c1c1"
            self.secondary_colour = "#c1c1c1"
            self.logo = False
            self.carousel = False

    def update(self, new_settings):
        try:
            with open("staff/settings.json", "w") as settings_file: 
                json.dump(new_settings, settings_file)
        except:
            return "Could not update"
    
    def as_dict(self):
        try:
            with open("staff/settings.json", "r") as settings_file: 
                return json.load(settings_file)
        except:
            return None
    
    @classmethod
    def to_rgb(settings, colour):
        r = int(colour[0:2], 16); # hexToR
        g = int(colour[2:4], 16); # hexToG
        b = int(colour[4:6], 16); # hexToB
        return r, g, b

    def get_text_colour_primary(self):
        r, g, b = Settings.to_rgb(self.primary_colour[1:])
        return "#000000" if (((r * 0.299) + (g * 0.587) + (b * 0.114)) > 186) else "#FFFFFF"
    
    def is_primary_light_or_dark(self):
        return "light" if self.get_text_colour_primary() == "#000000" else "dark"

    def get_text_colour_secondary(self):
        r, g, b = Settings.to_rgb(self.secondary_colour[1:])
        return "#000000" if (((r * 0.299) + (g * 0.587) + (b * 0.114)) > 186) else "#FFFFFF"

class CarouselImage(models.Model):
    image = models.ImageField()
    label = models.CharField(max_length=30, null=True)

class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        for item in self.items(): item.delete()
        super().delete(*args, **kwargs)
    
    def items(self):
        return Product.objects.filter(category=self)

    def add_products(self, products):
        for product in products:
            product.category = self
            product.save()

    @property
    def item_count(self):
        return self.items().count()
    
    @classmethod
    def get_visible(category):
        return Category.objects.all()

class Product(models.Model):
    name = models.CharField(max_length=75, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)
    hidden = models.BooleanField(default=False)
    min = models.IntegerField()
    max = models.IntegerField()
    
    def __str__(self):
        return self.name
    
    def hide(self):
        self.hidden = True
        self.save()

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)
    
    def set_available(self):
        self.available = True
        self.hidden = False
        self.save()
    
    def set_unavailable(self):
        self.available = False
        self.save()
    
    @property
    def num_sold(self):
        order_products = OrderProduct.objects.filter(product_name=self.name).values_list('quantity', flat=True)
        return sum(order_products)
    
    @property
    def num_sold_today(self):
        orders = Order.objects.filter(date_ordered__date=date.today())
        total = 0
        for order in orders:
            op = OrderProduct.objects.filter(order=order, product_name=self.name)
            if op: total += op.quantity
        return total
    
    @staticmethod
    def best_sellers(limit):
        return sorted(Product.objects.all(), key=lambda x: -(x.num_sold))[:limit]
    
    @classmethod
    def num_available(product):
        return Product.objects.filter(available=True, hidden=False).count()
    
    def get_add_to_basket_form(self):
        return AddProductToBasketForm({'product_name' : self.name, 'quantity' : self.min})
    
    def get_remove_form(self):
        return AddProductToBasketForm({'product_name' : self.name, 'quantity' : 0})

    @classmethod
    def hide_products(product, products):
        for product in products: product.hide()
    
    @classmethod
    def delete_products(product, products):
        for product in products: product.delete()
    
    @classmethod
    def make_products_available(product, products):
        for product in products: product.set_available()

    @classmethod
    def make_products_unavailable(product, products):
        for product in products: product.set_unavailable()

class Collection(models.Model):
    name = models.CharField(max_length=40, unique=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    available = models.BooleanField(default=True)
    hidden = models.BooleanField(default=False)
    products = models.ManyToManyField(Product)

    def add_products(self, products):
        for product in products:
            self.products.add(product)
        
    def get_add_to_basket_form(self):
        return AddCollectionToBasketForm({'collection_name' : self.name, 'quantity' : 1})
    
    def get_remove_form(self):
        return AddCollectionToBasketForm({'collection_name' : self.name, 'quantity' : 0})
    
    @classmethod
    def get_visible(collection):
        return Collection.objects.filter(hidden=False)

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()

class Promotion(models.Model):
    PERCENTAGE = 'Percentage'
    FIXED_PRICE = 'Fixed Price'
    TYPE_CHOICES = [(PERCENTAGE, 'Percentage'), (FIXED_PRICE, 'Fixed Price')]

    code = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    max_uses = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField()
    max_discount = models.IntegerField(null=True, blank=True)
    min_spend = models.IntegerField(null=True, blank=True)
    # customer_limit = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)
    expiry = models.DateTimeField(null=True, blank=True)
    used = models.IntegerField(default=0)

    def is_eligible(self, total):
        if self.used >= self.max_uses or self.expiry <= timezone.now():
            self.active = False
            self.save()
        if not self.active:
            return False
        elif self.min_spend and total < self.min_spend:
            return False
        else:
            return True
    
    def set_used(self):
        self.used += 1
    
    def get_discount(self, cost):
        if self.type == Promotion.PERCENTAGE:
            discount_cost = Decimal(self.amount/100) * cost
            max_discount_cost = Decimal(self.max_discount/100) * cost
            if discount_cost > max_discount_cost:
                return round(max_discount_cost, 2)
            else:
                return round(discount_cost, 2)
        else:
            return self.amount
    
    @property
    def total_saved(self):
        return sum(Order.objects.filter(promotion_code=self.code).values_list('discount_amount', flat=True))
    
    @classmethod
    def disable_all(cls):
        Promotion.objects.all().update(active=False)

class Address(models.Model):
    name = models.CharField(max_length=127)
    line_1 = models.CharField(max_length=255)
    line_2 = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=35)
    county = models.CharField(max_length=35, null=True)
    postcode = models.CharField(max_length=8)

class Delivery(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    available = models.BooleanField(default=True)
    # per_item = models.BooleanField(default=False)
    # max_price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name
    
    @property
    def num_used(self):
        return OrderShipping.objects.filter(delivery_name=self.name).count()

class Order(models.Model):
    promotion_code = models.CharField(max_length=30, null=True)
    discount_amount = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    # products = models.ManyToManyField(Product, through='OrderProduct')
    # collections = models.ManyToManyField(Collection, through='OrderCollection')

    @staticmethod
    def recent_orders(limit):
        return Order.objects.all().order_by('-date_ordered')[:limit]
    
    @property
    def num_items(self):
        items = 0
        for op in self.orderproduct_set.all():
            items += op.quantity
        for oc in self.ordercollection_set.all():
            items += oc.quantity
        return items

    @property
    def item_total_cost(self):
        total = 0
        for op in self.orderproduct_set.all():
            total += op.total_cost
        for oc in self.ordercollection_set.all():
            total += oc.total_cost
        return total

    @property
    def item_total_with_discount(self):
        if self.discount_amount:
            return self.item_total_cost - self.discount_amount
        else: return self.item_total_cost
    
    @property
    def final_price(self):
        return self.item_total_with_discount + self.ordershipping.delivery_price
    
    @classmethod
    def sales_today(order):
        total = 0
        for order in Order.objects.filter(date_ordered__date=date.today()):
            total += order.item_total_with_discount
        return total

    @classmethod
    def num_orders_today(order):
        return Order.objects.filter(date_ordered__date=date.today()).count()

    @classmethod
    def create_order_and_empty_basket(order, basket):
        if basket.promotion:
            order = Order.objects.create(promotion_code=basket.promotion.code, discount_amount=basket.promotion_amount)
        else:
            order = Order.objects.create()
        order.add_shipping(basket.address, basket.delivery)
        order.add_products(basket.basketproduct_set.all())
        order.add_collections(basket.basketcollection_set.all())
        basket.address.delete()
        basket.delete()
        return order

    def add_shipping(self, address, delivery):
        address_dict = model_to_dict(address)
        address_dict['address_name'] = address_dict.pop('name')
        address_dict.pop('id')
        OrderShipping.objects.create(order=self, delivery_name=delivery.name, delivery_price=delivery.price, **address_dict)
    
    def add_products(self, basket_products):
        for bp in basket_products:
            OrderProduct.objects.create(order=self, product_name=bp.product.name, price=bp.product.price, quantity=bp.quantity)

    def add_collections(self, basket_collections):
        for bc in basket_collections:
            order_collection = OrderCollection.objects.create(order=self, collection_name=bc.collection.name, quantity=bc.quantity, price=bc.collection.price)
            for product in bc.collection.products.all():
                OrderCollectionProduct.objects.create(order_collection=order_collection, product_name=product.name)
    
    def toggle_shipped(self):
        self.shipped = not self.shipped
        self.save()

class OrderShipping(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    address_name = models.CharField(max_length=127)
    line_1 = models.CharField(max_length=255)
    line_2 = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=35)
    county = models.CharField(max_length=35, null=True)
    postcode = models.CharField(max_length=8)
    delivery_name = models.CharField(max_length=255)
    delivery_price = models.DecimalField(max_digits=7, decimal_places=2)

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)

    @property
    def total_cost(self):
        return self.price * self.quantity

class OrderCollection(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    collection_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)

    @property
    def total_cost(self):
        return self.price * self.quantity

class OrderCollectionProduct(models.Model):
    order_collection = models.ForeignKey(OrderCollection, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    # quantity = models.IntegerField()