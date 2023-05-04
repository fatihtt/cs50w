import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, PostLike


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
        
        # Create a list for user's likes and zip it to the post list
        like_list = []
        for post in posts:
            if post.likes.filter(user = request.user):
                like_list.append(True)
            else:
                like_list.append(False)


        return render(request, "network/index.html", {
            "posts": zip(posts, like_list)
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
    
@csrf_exempt
@login_required
def edit_post(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(user=request.user, pk=post_id)
    except Exception as e:
        return JsonResponse({"error": "Post not found."}, status=404)
    
    try:
        if request.method == "PUT":
            data = json.loads(request.body)
            if data.get("text") is not None:
                post.text = data["text"]
                post.save()
                return HttpResponse(status=204)
        else:
            raise Exception("No text")
    except Exception as e:
        return JsonResponse({"error": e}, status=404)
    
@csrf_exempt
@login_required
def favorite_toggle(request, post_id):
    # Query for requested post
    try:
        m_post = Post.objects.get(pk=post_id)
    except Exception as e:
        return JsonResponse({"error": "Post not found."}, status=404)
    
    try:
        if request.method == "PUT":

            # Get json data

            data = json.loads(request.body)
            if data.get("favorite") is not None:
                
                # If action favorite, create a new PostLike
                if data["favorite"] == "favorite_border" and PostLike.objects.filter(user=request.user, post=m_post).count() == 0:
                    new_post_like = PostLike(user=request.user, post=m_post)
                    new_post_like.save()
                
                # If action unfavorite, Find Postlike and Delete
                elif data["favorite"] == "favorite" and PostLike.objects.filter(user=request.user, post=m_post).count() > 0:
                    likes = PostLike.objects.filter(user=request.user, post=m_post)
                    likes.all().delete()

                # Response all is well
                return HttpResponse(status=204)
            else:
                raise Exception("Favorite none.")
        else:
            raise Exception("No favorite")
    except Exception as e:
        return JsonResponse({"error": e}, status=500)