from django.shortcuts import render
from . import clicker
from . import profile_operations
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from cernyrobin_app.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.serializers import serialize
from django.db.models import IntegerField
from django.db.models.fields.related import ForeignKey

import json

# Utils
def go_back(request):
    next_url = request.POST.get('next', request.GET.get('next', ''))
    response_data = {'redirect_url': next_url}

    return JsonResponse(response_data) if next_url else HttpResponse("200 OK")

# Pages

def home(request):
    context = {}

    return render(request, "cernyrobin/home.html", context)

def clicker_page(request):
    context = {}

    return render(request, "cernyrobin/clicker.html", context)
   
def login_page(request):
    context = {
        "page": "login",
    }

    return render(request, "cernyrobin/login.html", context)

# API

def login_submit(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # add checks for username and password format

        try:
            user = User.objects.get(username=username.lower())
        except User.DoesNotExist:
            if request.user.is_authenticated or request.user.is_anonymous:
                logout(request)

            user = User.objects.create_user(username=username, password=password)
            user_profile = UserProfile.objects.create(user=user)

            user_profile.save()
            user.save()

            login(request, user)

            return go_back(request)

        if user.check_password(password):
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)

                return go_back(request)
            else:
                return HttpResponse("401 Unauthorized")
        else:
            return HttpResponse("401 Unauthorized")
    else:
        return HttpResponse("405 Method Not Allowed")

def add_click(request):
    if request.method == "POST":
        return clicker.add_click(request)
    else:
        return HttpResponse("405 Method Not Allowed")
    
def get_user_data(request):
    if request.method == "GET":
        scope = request.GET.get("scope")

        user_profile, created = profile_operations.get_profile(request)

        data = profile_operations.get_data(user_profile, scope)

        if data:
            return JsonResponse(data=data, safe=False)
        else:
            return HttpResponse("400 Bad Request")
    else:
        return HttpResponse("405 Method Not Allowed")
    
def get_all_data(request):
    if request.method == "GET":
        scope = request.GET.get("scope")

        if not scope:
            return HttpResponse("400 Bad Request")
        
        all_user_profiles = profile_operations.get_all_profiles()
        
        all_users_data = []
        
        for user_profile in all_user_profiles:
            user_data = profile_operations.get_data(user_profile, scope)
            
            if not user_data:
                continue
            
            all_users_data.append(user_data)

        return JsonResponse(data=all_users_data, safe=False)
    else:
        return HttpResponse("405 Method Not Allowed")