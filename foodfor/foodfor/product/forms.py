from django.forms import ModelForm
from product.models import Nutrient, Product, MealPlan, MealPlanNutrient, ProductNutrient
from django.forms.widgets import HiddenInput, TextInput

class NutrientForm(ModelForm):
    class Meta:
        model = Nutrient
        
class ProductForm(ModelForm):
    class Meta:
        model = Product
        exclude = ('up_votes', 'down_votes')
        widgets = {"user": HiddenInput}

class ProductNutrientForm(ModelForm):
    class Meta:
        model = ProductNutrient
        widgets = {"nutrient": HiddenInput, "quantity": TextInput(attrs={"class":"span1"})}

class MealPlanNutrientForm(ModelForm):
    class Meta:
        model = MealPlanNutrient
        widgets = {"minimum": TextInput(attrs={"class":"span1"}), "maximum": TextInput(attrs={"class":"span1"}),"nutrient": HiddenInput()}
      
class MealPlanForm(ModelForm):
    class Meta:
        model = MealPlan
        exclude = ('up_votes', 'down_votes', 'balanced', 'price')
        widgets = {"user": HiddenInput, "number_of_days": TextInput(attrs={"class":"span1"})}  
    