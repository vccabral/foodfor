from django.http import HttpResponse
import json
import urllib2
import re

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