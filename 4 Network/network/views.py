import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post


def index(request):
    # Get querystring to determine requested all post or fallowing
    try:
        m_querystring = request.GET.get("p")
        posts = Post.objects.all().order_by("-time")

        if m_querystring and m_querystring == "f":
            my_fallowings = request.user.fallower.all()

            # Scan posts and if not in fallowing list of current user, exclude post
            for post in posts:
                fallowing_detect = False

                for fallowing in my_fallowings:
                    print("if state:", fallowing.user, post.user)
                    if fallowing.user == post.user:
                        fallowing_detect = True
                        
                if not fallowing_detect:
                    posts = posts.exclude(id = post.id)
                    

        return render(request, "network/index.html", {
            "posts": posts
        })
    except Exception as e:
        print("Error, ", e)
        return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
@csrf_exempt
def new_post(request):
    try:
        # Check user authenticated
        if not request.user.is_authenticated:
            raise Exception("User not authenticated")

        # Check request method
        if request.method != "POST":
            raise Exception("Method should be post!")
        
        # Get data
        data = json.loads(request.body)
        title = data.get("title", "")
        text = data.get("text", "")

        # Check data
        if len(title) < 1 or len(text) < 1:
            raise Exception("Title or text blank")
        
        post = Post(
            user=request.user,
            title=title,
            text=text
        )
        post.save()

        return JsonResponse({"message": "Post saved."}, status=201)
    except Exception as e:
        print(e)
        return JsonResponse({"error": e}, status=400)

