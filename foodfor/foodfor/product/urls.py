from django.conf.urls.defaults import *
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView
from django.forms.models import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from product.models import MealPlan, Product, Nutrient, MealPlanNutrient, ProductNutrient
from product.forms import NutrientForm, ProductForm, MealPlanForm, MealPlanNutrientForm, ProductNutrientForm

class MealPlanCreateView(CreateView):
    def get_context_data(self, **kwargs):
        NutrientFormSet = inlineformset_factory(MealPlan, MealPlanNutrient, form=MealPlanNutrientForm, max_num=Nutrient.objects.count(), can_delete=False)
        context = super(MealPlanCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formsets'] = NutrientFormSet(self.request.POST)
        else:
            context['formsets'] = NutrientFormSet()
            for form, nutrient in zip(context['formsets'], Nutrient.objects.all()):
                if not form.initial:
                    form.initial = {"nutrient": nutrient, "minimum": nutrient.recommended_intake}
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
            return HttpResponseRedirect('/product/mealplan/%s/details/' % self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class MealPlanUpdateView(UpdateView):
    def dispatch(self, request, *args, **kwargs):
        return  super(MealPlanUpdateView, self).dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        NutrientFormSet = inlineformset_factory(MealPlan, MealPlanNutrient, form=MealPlanNutrientForm, max_num=Nutrient.objects.count(), can_delete=False)
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
            return HttpResponseRedirect('/product/mealplan/%s/details/' % self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ProductUpdateView(UpdateView):
    def get_context_data(self, **kwargs):
        ProductNutrientFormSet = inlineformset_factory(Product, ProductNutrient, form=ProductNutrientForm, max_num=Nutrient.objects.count(), can_delete=False)
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
            return HttpResponseRedirect('/product/product/%s/details/' % self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ProductCreateView(CreateView):
    def get_context_data(self, **kwargs):
        ProductNutrientFormSet = inlineformset_factory(Product, ProductNutrient, form=ProductNutrientForm, max_num=Nutrient.objects.count(), can_delete=False)
        context = super(ProductCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formsets'] = ProductNutrientFormSet(self.request.POST)
        else:
            context['formsets'] = ProductNutrientFormSet()
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
            return HttpResponseRedirect('/product/product/%s/details/' % self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class MealPlanDetailView(DetailView):
    def get_context_data(self, **kwargs):
        context = super(MealPlanDetailView, self).get_context_data(**kwargs)
        context['object_extra'] = self.object
        return context

urlpatterns = patterns('',
                       #mealplans
                       url(r'^mealplan/$', ListView.as_view(model=MealPlan, template_name="mealplan_list.html"), name="read_mealplans"),
                       url(r'^mealplan/create/$', login_required(MealPlanCreateView.as_view(form_class=MealPlanForm, template_name="mealplan_form.html")), name="create_mealplan"),
                       url(r'^mealplan/(?P<pk>\d+)/details/$',  MealPlanDetailView.as_view(model=MealPlan, template_name="mealplan_detail.html"), name="read_mealplan"),
                       url(r'^mealplan/(?P<pk>\d+)/edit/$', login_required(MealPlanUpdateView.as_view(model=MealPlan,form_class=MealPlanForm, template_name="mealplan_form.html")), name="update_mealplan"),
                       #products
                       url(r'^product/$', ListView.as_view(model=Product, template_name="product_list.html"), name="read_products"),
                       url(r'^product/create/$', login_required(ProductCreateView.as_view(form_class=ProductForm, template_name="product_form.html")), name="create_product"),
                       url(r'^product/(?P<pk>\d+)/details/$',  DetailView.as_view(model=Product, template_name="product_detail.html"), name="read_product"),
                       url(r'^product/(?P<pk>\d+)/edit/$', login_required(ProductUpdateView.as_view(model=Product, form_class=ProductForm, template_name="product_form.html")), name="update_product"),
                      #nutrients
                       url(r'^nutrient/$', ListView.as_view(model=Nutrient, template_name="nutrient_list.html"), name="read_nutrients"),
                       url(r'^nutrient/create/$', login_required(CreateView.as_view(form_class=NutrientForm, template_name="nutrient_form.html")), name="create_nutrient"),
                       url(r'^nutrient/(?P<pk>\d+)/details/$',  DetailView.as_view(model=Nutrient, template_name="nutrient_detail.html"), name="read_nutrient"),
                       url(r'^nutrient/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Nutrient,form_class=NutrientForm, template_name="nutrient_form.html")), name="update_nutrient"),
)