from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50)
    __str__ = lambda x: x.str_with_product_count()
    def str_with_product_count(self):
        from product.models import Product
        count = Product.objects.filter(tags__in=[self.pk]).count()
        return "%s (%d products)" % (self.name, count) 

class Nutrient(models.Model):
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=50, choices=(("grams","grams"),("milligrams","milligrams"), ("ugrams", "ugrams"), ("IU", "IU"),))
    recommended_min_intake = models.DecimalField(decimal_places=5, max_digits=12)
    recommended_max_intake = models.DecimalField(decimal_places=5, max_digits=12, blank=True)
    __str__ = lambda x: "%s (%s)" % (x.name, x.unit)
    get_absolute_url = lambda x: "/product/nutrient/"

class Product(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=200)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    serving_per_container = models.DecimalField(decimal_places=5, max_digits=12)
    up_votes = models.ManyToManyField(User, related_name="product_up", blank=True)
    down_votes = models.ManyToManyField(User, related_name="product_down", blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    __str__ = lambda x: x.name
    get_absolute_url = lambda x: "/product/product/"

class ProductNutrient(models.Model):
    product = models.ForeignKey(Product)
    nutrient = models.ForeignKey(Nutrient)
    serving_quantity = models.DecimalField(decimal_places=5, max_digits=12)
    quantity = models.DecimalField(decimal_places=5, max_digits=12)
    
class MealPlan(models.Model):
    name = models.CharField(max_length=50)
    number_of_days = models.IntegerField()
    balanced = models.BooleanField()
    price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    user = models.ForeignKey(User)
    up_votes = models.ManyToManyField(User, related_name="mealplan_up", blank=True)
    down_votes = models.ManyToManyField(User, related_name="mealplan_down", blank=True)
    desired_tags = models.ManyToManyField(Tag, blank=True)    
    __str__ = lambda x: x.name
    get_absolute_url = lambda x: "/product/mealplan/%s/details/" % x.pk

class MealPlanProduct(models.Model):
    meal_plan = models.ForeignKey(MealPlan)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
    
class MealPlanNutrient(models.Model):
    meal_plan = models.ForeignKey(MealPlan)
    nutrient = models.ForeignKey(Nutrient)
    minimum = models.DecimalField(decimal_places=2, max_digits=10)
    maximum = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=10)
    
    