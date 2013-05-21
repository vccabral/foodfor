from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from product.models import MealPlan, Product
from product.forms import MealPlanForm
import json
import urllib2 
import re

def update_votes(object):
    object.votes = object.up_votes.all().count() - object.down_votes.all().count()
    object.save()

@login_required
def product_count(request):
    response_data = {"success": "OK"}
    
    form = MealPlanForm(request.GET)
    desired = request.GET.getlist("desired_tags")
    excludes = request.GET.getlist("excluded_tags")
    musts = request.GET.getlist("must_have_tags")
    product_queryset = Product.objects.filter(votes__gte=-1, tags__in=desired).exclude(tags__in=excludes)
    if product_queryset.exists():
        for must_tag in musts:
            product_queryset = product_queryset.filter(tags=must_tag)
    response_data["count"] = product_queryset.distinct().count()
    response_data["percent"] = int(response_data["count"] * 100 / Product.objects.all().count())
    return HttpResponse(json.dumps(response_data), content_type="application/json")    
    

@login_required
def vote_for(request, model, pk, direction):
    response_data = {"success": "OK"}
    try:
        if True:
            model = MealPlan if model == "mealplan" else Product
            object = model.objects.get(pk=int(pk))
            if direction=="up":
                if object.down_votes.filter(pk=request.user.pk).exists():
                    object.down_votes.remove(request.user)
                else:
                    object.up_votes.add(request.user)
            else:
                if object.up_votes.filter(pk=request.user.pk).exists():
                    object.up_votes.remove(request.user)
                else:
                    object.down_votes.add(request.user)
        object.save()
        update_votes(object)
        response_data["votes"] = object.votes
    except:
        response_data = {"success": "FAIL"}
    return HttpResponse(json.dumps(response_data), content_type="application/json")    

def getinfo(request):
    response_data = {}
    response_data["name"] = ""
    response_data["price"] = ""
    try:
        url = request.GET["url"]
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()    
        html = the_page
        matchObj = re.search( r'(<span\s+id="btAsinTitle"\s+>)([^<]+)(</span>)', html, re.M|re.I)
        if matchObj:
            response_data["name"] = matchObj.group(2)
        matchObj = re.search( r'(<b class="priceLarge">\s*\$)([^<]+)(</b>)', html, re.M|re.I)
        if matchObj:
            response_data["price"] = matchObj.group(2)
    except:
        pass
    return HttpResponse(json.dumps(response_data), content_type="application/json")