from django.db import models
import json

class Settings():
    def __init__(self):
        try:
            with open("staff/settings.json", "r") as settings_file: 
                settings = json.load(settings_file)
                self.shop_name = settings['shop_name']
                self.primary_colour = settings['primary_colour']
                self.secondary_colour = settings['secondary_colour']
        except:
            self.shop_name = "No Name"
            self.primary_colour = "#c1c1c1"
            self.secondary_colour = "#c1c1c1"

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

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()

class Promotion(models.Model):
    PERCENTAGE = 'Percentage'
    FIXED_PRICE = 'Fixed Price'
    TYPE_CHOICES = [(PERCENTAGE, 'Percentage'), (FIXED_PRICE, 'Fixed Price')]

    code = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    max_uses = models.IntegerField(null=True)
    amount = models.IntegerField()
    max_discount = models.IntegerField(null=True)
    min_spend = models.IntegerField(null=True)
    customer_limit = models.IntegerField(null=True)
    active = models.BooleanField(default=True)
    expiry = models.DateTimeField(null=True)
    used = models.IntegerField(default=0)