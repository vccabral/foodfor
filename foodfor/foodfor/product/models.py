from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50)
    __str__ = lambda x: x.name

class Nutrient(models.Model):
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)
    recommended_intake = models.DecimalField(decimal_places=2, max_digits=10)
    __str__ = lambda x: x.name
    get_absolute_url = lambda x: "/product/nutrient/%s/details/" % x.pk

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    url = models.URLField()
    up_votes = models.ManyToManyField(User, related_name="product_up", blank=True)
    down_votes = models.ManyToManyField(User, related_name="product_down", blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    __str__ = lambda x: x.name
    get_absolute_url = lambda x: "/product/product/%s/details/" % x.pk

class ProductNutrient(models.Model):
    product = models.ForeignKey(Product)
    nutrient = models.ForeignKey(Nutrient)
    quantity = models.DecimalField(decimal_places=2, max_digits=10)
    
class MealPlan(models.Model):
    name = models.CharField(max_length=50)
    number_of_days = models.IntegerField()
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
    
    