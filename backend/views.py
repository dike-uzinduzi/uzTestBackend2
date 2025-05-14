from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    
    html = '<html lang="en"><body>UZINDUZI AFRICA API </body></html>'
    return HttpResponse(html)
