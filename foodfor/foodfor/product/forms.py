from django.forms import ModelForm
from product.models import Nutrient, Product, MealPlan, MealPlanNutrient, ProductNutrient
from django.forms.widgets import HiddenInput, TextInput, CheckboxSelectMultiple

class NutrientForm(ModelForm):
    class Meta:
        model = Nutrient
        
class ProductForm(ModelForm):
    class Meta:
        model = Product
        exclude = ('up_votes', 'down_votes', 'votes')
        widgets = {
                   "user": HiddenInput, 
                   "url": TextInput(attrs={"class":"span8"}), 
                   "name": TextInput(attrs={"class":"span8"}), 
                   "price": TextInput(attrs={"class":"span1"}), 
                   "tags": CheckboxSelectMultiple()
                   }

class ProductNutrientForm(ModelForm):
    class Meta:
        model = ProductNutrient
        widgets = {
                   "nutrient": HiddenInput, 
                   "quantity": TextInput(attrs={"class":"span1 total"}), 
                   "serving_quantity": TextInput(attrs={"class":"span1 serving"})
                   }

class MealPlanNutrientForm(ModelForm):
    class Meta:
        model = MealPlanNutrient
        widgets = {
                   "minimum": TextInput(attrs={"class":"span1"}), 
                   "maximum": TextInput(attrs={"class":"span1"}),
                   "nutrient": HiddenInput()
                   }
      
class MealPlanForm(ModelForm):
    class Meta:
        model = MealPlan
        exclude = ('up_votes', 'down_votes', 'balanced', 'price', 'votes')
        widgets = {
                   "user": HiddenInput, 
                   "number_of_days": TextInput(attrs={"class":"span1"}), 
                   "desired_tags": CheckboxSelectMultiple(), 
                   "excluded_tags": CheckboxSelectMultiple(),
                   "must_have_tags": CheckboxSelectMultiple()}  
    