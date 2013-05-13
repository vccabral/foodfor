from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50)

class Nutrient(models.Model):
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    url = models.URLField()
    up_votes = models.ManyToManyField(User, related_name="product_up")
    down_votes = models.ManyToManyField(User, related_name="product_down")
    tags = models.ManyToManyField(Tag)

class ProductNutrient(models.Model):
    product = models.ForeignKey(Product)
    nutrient = models.ForeignKey(Nutrient)
    quantity = models.DecimalField(decimal_places=2, max_digits=10)
    
class MealPlan(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User)
    up_votes = models.ManyToManyField(User, related_name="mealplan_up")
    down_votes = models.ManyToManyField(User, related_name="mealplan_down")
    desired_tags = models.ManyToManyField(Tag)    

class MealPlanProduct(models.Model):
    meal_plan = models.ForeignKey(MealPlan)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
    
class MealPlanNutrient(models.Model):
    meal_plan = models.ForeignKey(MealPlan)
    nutrient = models.ForeignKey(Nutrient)
    minimum = models.DecimalField(decimal_places=2, max_digits=10)
    maximum = models.DecimalField(blank=True, decimal_places=2, max_digits=10)
    
    