from django.shortcuts import render
from django.http import HttpRequest
from django.templates import loader

def home(request):
    return HttpResponse(loader.get_template("cernyrobin/home.html").render())