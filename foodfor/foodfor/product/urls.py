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


def solve_soylent(A,b,p):
    prob = LpProblem("soylentcost", LpMinimize)
    x = []
    for index in range(0,len(b)):
        x.append(LpVariable("x_"+str(index),0, None, "Integer"))
    prob += reduce(lambda x,y: x+y, [x_var*p_constant for x_var,p_constant in zip(x,p)])
    for row, b_constant in zip(A, b):
        prob += reduce(lambda x,y: x+y, [x_var*rc_constant for x_var,rc_constant in zip(x,row)]) >= b_constant
    GLPK().solve(prob)
    return prob.variables(), value(prob.objective), re.split(r"(MINIMIZE|SUBJECT TO|_C|VARIABLES|Integer)", str(prob))

class MealPlanDetailView(DetailView):
    def get_context_data(self, **kwargs):
        context = super(MealPlanDetailView, self).get_context_data(**kwargs)
        products = Product.objects.filter(tags__in=self.object.desired_tags.values_list("pk", flat=True)).distinct()
        nutrients = self.object.mealplannutrient_set.all().order_by("pk")
        p = map(lambda x: x.price, products)
        b = map(lambda x: self.object.number_of_days * x.minimum, nutrients)
        A = map(lambda x: map(lambda y: ProductNutrient.objects.get(nutrient=x.pk,product=y.pk).quantity if ProductNutrient.objects.filter(nutrient=x.pk,product=y.pk).exists() else 0, products), nutrients)
        solution, cost, output = solve_soylent(A, b, p)
        solution_vars = sorted(solution, key=lambda x: int(x.name.split('_')[1]))
        totals = map(lambda x: reduce(lambda x,y: x+y[0]*y[1].varValue, zip(x,solution_vars),0),A)
        day_totals = map(lambda x: reduce(lambda x,y: x+y[0]*y[1].varValue/self.object.number_of_days, zip(x,solution_vars),0),A)
        meets_min = [daytotal>=nutrient.minimum for daytotal,nutrient in zip(day_totals,nutrients)] 
        meets_max = [not nutrient.maximum or daytotal<=nutrient.maximum for daytotal,nutrient in zip(day_totals,nutrients)]
        meets_both = [a and b for a, b in zip(meets_min, meets_max)]
        A_p = map(lambda p: [[ProductNutrient.objects.get(nutrient=nutrient.pk,product=p.pk),meets] for nutrient, meets in zip(nutrients, meets_both)], products)
        context['count'] = int((sum(meets_min)+sum(meets_max) / (len(meets_min)*2.0)))
        context["balanced"] = all(meets_min) and all(meets_max)
        context["nutrients"] = zip(nutrients, A, totals, day_totals, meets_min, meets_max, meets_both)
        context["solution"] = zip(products, solution_vars, A_p)
        context["cost"] = cost
        context["cost_ppd"] = cost/self.object.number_of_days
        context["output"] = output
        self.object.price = cost/self.object.number_of_days
        self.object.balanced = context["balanced"]
        self.object.save()
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