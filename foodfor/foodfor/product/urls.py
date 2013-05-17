from django.conf.urls.defaults import *
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView
from django.forms.models import inlineformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, Http404
from product.models import MealPlan, Product, Nutrient, MealPlanNutrient, ProductNutrient
from product.forms import NutrientForm, ProductForm, MealPlanForm, MealPlanNutrientForm, ProductNutrientForm
from product.views import getinfo
from decimal import Decimal
from pulp import *
import re

class MealPlanCreateView(CreateView):
    def get_context_data(self, **kwargs):
        NutrientFormSet = inlineformset_factory(MealPlan, MealPlanNutrient, form=MealPlanNutrientForm, max_num=Nutrient.objects.count(), extra=Nutrient.objects.count(), can_delete=False)
        context = super(MealPlanCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formsets'] = NutrientFormSet(self.request.POST)
        else:
            context['formsets'] = NutrientFormSet()
            for form, nutrient in zip(context['formsets'], Nutrient.objects.all()):
                if not form.initial:
                    form.initial = {"nutrient": nutrient, "minimum": nutrient.recommended_min_intake, "maximum": nutrient.recommended_max_intake}
        return context
    def get_initial(self):
        return {"user": self.request.user}
    def form_valid(self, form):
        context = self.get_context_data()
        formsets = context['formsets']
        if formsets.is_valid():
            self.object = form.save()
            formsets.instance = self.object
            formsets.save()
            return HttpResponseRedirect('/product/mealplan/')
        else:
            return self.render_to_response(self.get_context_data(form=form))

class MealPlanUpdateView(UpdateView):
    def get_object(self, *args, **kwargs):
        object = super(MealPlanUpdateView, self).get_object(**kwargs) 
        if object.user != self.request.user:
            raise Http404
        return object
    def get_context_data(self, **kwargs):
        NutrientFormSet = inlineformset_factory(MealPlan, MealPlanNutrient, form=MealPlanNutrientForm, max_num=Nutrient.objects.count(), extra=Nutrient.objects.count(), can_delete=False)
        context = super(MealPlanUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formsets'] = NutrientFormSet(self.request.POST, instance=self.object)
        else:
            context['formsets'] = NutrientFormSet(instance=self.object)
            for form, nutrient in zip(context['formsets'], Nutrient.objects.all()):
                if not form.initial:
                    form.initial = {"nutrient": nutrient}
        return context
    def form_valid(self, form):
        context = self.get_context_data()
        formsets = context['formsets']
        if formsets.is_valid():
            self.object = form.save()
            formsets.instance = self.object
            formsets.save()
            return HttpResponseRedirect('/product/mealplan/%d/details/' % self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ProductUpdateView(UpdateView):
    def get_context_data(self, **kwargs):
        ProductNutrientFormSet = inlineformset_factory(Product, ProductNutrient, form=ProductNutrientForm, max_num=Nutrient.objects.count(), extra=Nutrient.objects.count(), can_delete=False)
        context = super(ProductUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formsets'] = ProductNutrientFormSet(self.request.POST, instance=self.object)
        else:
            context['formsets'] = ProductNutrientFormSet(instance=self.object)
            for form, nutrient in zip(context['formsets'], Nutrient.objects.all()):
                if not form.initial:
                    form.initial = {"nutrient": nutrient}
        return context
    def form_valid(self, form):
        context = self.get_context_data()
        formsets = context['formsets']
        if formsets.is_valid():
            self.object = form.save()
            formsets.instance = self.object
            formsets.save()
            return HttpResponseRedirect('/product/product/')
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ProductCreateView(CreateView):
    def get_context_data(self, **kwargs):
        ProductNutrientFormSet = inlineformset_factory(Product, ProductNutrient, form=ProductNutrientForm, max_num=Nutrient.objects.count(), extra=Nutrient.objects.count(), can_delete=False)
        context = super(ProductCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formsets'] = ProductNutrientFormSet(self.request.POST)
        else:
            context['formsets'] = ProductNutrientFormSet()
            for form, nutrient in zip(context['formsets'], Nutrient.objects.all()):
                if not form.initial:
                    form.initial = {"nutrient": nutrient, "quantity": 0}
        return context
    def form_valid(self, form):
        context = self.get_context_data()
        formsets = context['formsets']
        if formsets.is_valid():
            self.object = form.save()
            formsets.instance = self.object
            formsets.save()
            return HttpResponseRedirect('/product/product/')
        else:
            return self.render_to_response(self.get_context_data(form=form))


def solve_soylent(A, b, p, b_max, p_servings, error_to_min=True):
    prob = LpProblem("soylentcost", LpMinimize)
    x = []
    x_serving = []
    for index in range(0,len(b)):
        x.append(LpVariable("x_"+str(index),0, None, "Integer"))
        x_serving.append(LpVariable("x_"+str(index)+"_servings",0, None, "Integer"))
    if error_to_min:
        prob += reduce(lambda x,y: x+y, [x_var * float(p_constant) + 0.0000001 * x_serve for x_var, p_constant, x_serve in zip(x, p, x_serving)]) 
    else:
        prob += reduce(lambda x,y: x+y, [x_var * float(p_constant) - 0.0000001 * x_serve for x_var, p_constant, x_serve in zip(x, p, x_serving)]) 

    for row, b_constant, b_max_constant in zip(A, b, b_max):
        prob += reduce(lambda x,y: x+y, [x_var * rc_constant for x_var, rc_constant in zip(x, row)]) >= b_constant
        prob += reduce(lambda x,y: x+y, [x_serv * rc_constant / p_serve for x_serv, rc_constant, p_serve in zip(x_serving, row, p_servings)]) >= b_constant
        prob += reduce(lambda x,y: x+y, [x_serv * rc_constant / p_serve for x_serv, rc_constant, p_serve in zip(x_serving, row, p_servings)]) <= (b_max_constant * Decimal(1))
    
    for x_serv, x_var, p_serve in zip(x_serving, x, p_servings):
        prob += x_serv / p_serve - x_var <= 0 
    
    GLPK().solve(prob)
    return prob.variables(), value(prob.objective), re.split(r"(MINIMIZE|SUBJECT TO|_C|VARIABLES|Integer)", str(prob))

def nutrient_is_undermax(daytotal, nutrient, solution_vars, products):
    speculative_answer = not nutrient.maximum or daytotal<=nutrient.maximum+Decimal(.1)
    if not speculative_answer:
        for solved_var, product in zip(solution_vars, products):
            if solved_var.varValue > 0 and ProductNutrient.objects.filter(product=product.pk, quantity__gt=0).count() in [1,2] and ProductNutrient.objects.filter(product=product.pk, nutrient=nutrient.nutrient.pk, quantity__gt=0).count()==1:
                return True
        return False
    else:
        return True

def get_object_context(self_object, multiplier):
    products = Product.objects.filter(tags__in=self_object.desired_tags.values_list("pk", flat=True)).exclude(tags__in=self_object.excluded_tags.values_list("pk", flat=True)).distinct().order_by("name")
    nutrients = self_object.mealplannutrient_set.all().order_by("pk")
    p = [product.price for product in products] 
    p_servings = [product.serving_per_container for product in products]
    b = [self_object.number_of_days * nutrient.minimum for nutrient in nutrients] 
    b_max = [self_object.number_of_days * nutrient.maximum * multiplier for nutrient in nutrients]
    A = [[ProductNutrient.objects.get(nutrient=nutrient.nutrient.pk,product=product.pk).quantity if ProductNutrient.objects.filter(nutrient=nutrient.nutrient.pk,product=product.pk).exists() else 0 for product in products] for nutrient in nutrients]
    solution, cost, output = solve_soylent(A, b, p, b_max, p_servings)
    
    solution_vars = sorted([solved for solved in solution if solved.name.endswith("_servings")], key=lambda x: int(x.name.split('_')[1]))
    solution_vars_ints = sorted([solved for solved in solution if not solved.name.endswith("_servings")], key=lambda x: int(x.name.split('_')[1]))
    solution_vars_percent = [solved.varValue if solved_int.varValue != 0 else 0 for solved, solved_int, p_serve in zip(solution_vars, solution_vars_ints, p_servings)]
    
    totals = [reduce(lambda x,y: x+y[0]*Decimal(y[1].varValue/y[2]), zip(x,solution_vars, p_servings),0) for x in A]
    day_totals = [reduce(lambda x,y: x+y[0]*Decimal(y[1].varValue/y[2])/self_object.number_of_days, zip(x,solution_vars, p_servings),0) for x in A]
    
    day_totals_int = [reduce(lambda x,y: x+y[0]*Decimal(y[1].varValue)/self_object.number_of_days, zip(x,solution_vars_ints),0) for x in A]
    
    meets_min = [daytotal >= (nutrient.minimum-Decimal(.1)) for daytotal,nutrient in zip(day_totals,nutrients)] 
    meets_max = [nutrient_is_undermax(daytotal, nutrient, solution_vars, products) for daytotal,nutrient in zip(day_totals,nutrients)]
    meets_both = [a and b for a, b in zip(meets_min, meets_max)]
    A_p = map(lambda p: [[ProductNutrient.objects.get(nutrient=nutrient.nutrient.pk,product=p.pk) if ProductNutrient.objects.filter(nutrient=nutrient.nutrient.pk,product=p.pk).exists() else 0, meets] for nutrient, meets in zip(nutrients, meets_both)], products)
    total_met = sum(meets_min)+sum(meets_max)
    return int(100*total_met / (len(meets_min)*2.0)), all(meets_min) and all(meets_max), zip(nutrients, A, totals, day_totals, meets_min, meets_max, meets_both), zip(products, solution_vars, A_p, solution_vars_ints, solution_vars_percent), cost, cost/self_object.number_of_days, output

class MealPlanDetailView(DetailView):
    def get_context_data(self, **kwargs):
        context = super(MealPlanDetailView, self).get_context_data(**kwargs)
        if Product.objects.filter(tags__in=self.object.desired_tags.values_list("pk", flat=True)).exclude(tags__in=self.object.excluded_tags.values_list("pk", flat=True)).exists():
            context['count'], context["balanced"], context["nutrients"], context["solution"], context["cost"], context["cost_ppd"], context["output"] = get_object_context(self.object, 1)
            if not context["balanced"]:
                context['count'], context["balanced"], context["nutrients"], context["solution"], context["cost"], context["cost_ppd"], context["output"] = get_object_context(self.object, 10)
            context['has_products'] = True
            self.object.price = context["cost_ppd"]
            self.object.balanced = context["balanced"]
            self.object.save()
        else:
            context['has_products'] = False
        return context

staff_required = user_passes_test(lambda u: u.is_staff)

urlpatterns = patterns('',
                       #mealplans
                       url(r'^mealplan/$', ListView.as_view(model=MealPlan, template_name="mealplan_list.html"), name="read_mealplans"),
                       url(r'^mealplan/create/$', login_required(MealPlanCreateView.as_view(form_class=MealPlanForm, template_name="mealplan_form.html")), name="create_mealplan"),
                       url(r'^mealplan/(?P<pk>\d+)/details/$',  MealPlanDetailView.as_view(model=MealPlan, template_name="mealplan_detail.html"), name="read_mealplan"),
                       url(r'^mealplan/(?P<pk>\d+)/edit/$', login_required(MealPlanUpdateView.as_view(model=MealPlan,form_class=MealPlanForm, template_name="mealplan_form.html")), name="update_mealplan"),
                       #products
                       url(r'^product/getinfo/', getinfo, name="getinfo"),
                       url(r'^product/$', ListView.as_view(model=Product, template_name="product_list.html"), name="read_products"),
                       url(r'^product/create/$', login_required(ProductCreateView.as_view(form_class=ProductForm, template_name="product_form.html")), name="create_product"),
                       url(r'^product/(?P<pk>\d+)/details/$',  DetailView.as_view(model=Product, template_name="product_detail.html"), name="read_product"),
                       url(r'^product/(?P<pk>\d+)/edit/$', login_required(ProductUpdateView.as_view(model=Product, form_class=ProductForm, template_name="product_form.html")), name="update_product"),
                      #nutrients
                       url(r'^nutrient/$', ListView.as_view(model=Nutrient, template_name="nutrient_list.html"), name="read_nutrients"),
                       url(r'^nutrient/create/$', staff_required(CreateView.as_view(form_class=NutrientForm, template_name="nutrient_form.html")), name="create_nutrient"),
                       url(r'^nutrient/(?P<pk>\d+)/details/$',  DetailView.as_view(model=Nutrient, template_name="nutrient_detail.html"), name="read_nutrient"),
                       url(r'^nutrient/(?P<pk>\d+)/edit/$', staff_required(UpdateView.as_view(model=Nutrient,form_class=NutrientForm, template_name="nutrient_form.html")), name="update_nutrient"),
)