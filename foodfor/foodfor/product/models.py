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
    recommended_max_intake = models.DecimalField(decimal_places=5, max_digits=12, blank=True, null=True)
    __str__ = lambda x: "%s (%s)" % (x.name, x.unit)
    get_absolute_url = lambda x: "/product/nutrient/"

class Product(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=200)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    serving_per_container = models.DecimalField(decimal_places=5, max_digits=12)
    up_votes = models.ManyToManyField(User, related_name="product_up", blank=True)
    down_votes = models.ManyToManyField(User, related_name="product_down", blank=True)
    votes = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True)
    __str__ = lambda x: x.name
    get_absolute_url = lambda x: "/product/product/"

class ProductNutrient(models.Model):
    product = models.ForeignKey(Product)
    nutrient = models.ForeignKey(Nutrient)
    serving_quantity = models.DecimalField(decimal_places=5, max_digits=12)
    quantity = models.DecimalField(decimal_places=5, max_digits=12)
    def percent(self):
        return round(100*self.serving_quantity/self.nutrient.recommended_min_intake,2) if self.serving_quantity!=0 and self.nutrient.recommended_min_intake!=0 else 0
    
class MealPlan(models.Model):
    is_cached = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    number_of_days = models.IntegerField()
    require_at_least_one_serving_per_day = models.BooleanField(default=False)
    balanced = models.BooleanField()
    price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    user = models.ForeignKey(User)
    up_votes = models.ManyToManyField(User, related_name="mealplan_up", blank=True)
    down_votes = models.ManyToManyField(User, related_name="mealplan_down", blank=True)
    votes = models.IntegerField(default=0)
    must_have_tags = models.ManyToManyField(Tag, blank=True, related_name="must_tags")
    desired_tags = models.ManyToManyField(Tag, blank=True, related_name="tags")    
    excluded_tags = models.ManyToManyField(Tag, blank=True, related_name="excluded_tags")
    __str__ = lambda x: x.name
    get_absolute_url = lambda x: "/product/mealplan/%s/details/" % x.pk

class MealPlanProduct(models.Model):
    meal_plan = models.ForeignKey(MealPlan)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
    servings_to_use = models.IntegerField()
    
class MealPlanNutrient(models.Model):
    meal_plan = models.ForeignKey(MealPlan)
    nutrient = models.ForeignKey(Nutrient)
    minimum = models.DecimalField(decimal_places=2, max_digits=10)
    maximum = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=10)
    
class Feedback(models.Model):
    email = models.EmailField()
    title = models.CharField(max_length=100) 
    body = models.CharField(max_length=2000) 
    get_absolute_url = lambda x: "/product/feedback/create/"

    