import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import IntegrityError
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post


def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": posts,
        "page_obj": page_obj
    })


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
    

def new_post(request):
    if request.method == "POST":
        poster = request.user
        content = request.POST["new_post"]
        if not content:
            return JsonResponse({"error": "Content is required."}, status=400)
        time = timezone.now()
        
        new_post = Post(poster=poster, content=content, timestamp=time, likes=0)
        new_post.save()
        new_post.liked_by.set([])

        return HttpResponseRedirect(reverse("index"))
    

def profile(request, name):
    user_profile = User.objects.get(username=name)
    user_posts = Post.objects.filter(poster=user_profile).order_by("-timestamp")
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    follower_count = user_profile.followers.count()
    following_count = user_profile.following.count()
    message = "Unfollow" if user_profile.followers.filter(username=request.user.username).exists() else "Follow"

    return render(request, "network/profile.html", {
        "user_profile": user_profile,
        "posts": user_posts, 
        "followers": follower_count,
        "following": following_count,
        "message": message,
        "page_obj": page_obj
    })


@login_required
def following(request):
    user = request.user
    user_following = user.following.all()
    posts = Post.objects.filter(poster__in=user_following).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts": posts,
        "page_obj": page_obj
    })


@csrf_exempt
@login_required
def edit(request, post_id):
    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return post contents
    if request.method == "GET":
        return JsonResponse(post.serialize())
    
    else:
        data = json.loads(request.body)
        content = data.get("content", "")
        post.content = content
        post.save()
        return JsonResponse(post.serialize())


@csrf_exempt
def follow(request, follow_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    current_user = request.user
    who_to_follow = User.objects.get(pk=follow_id)

    if who_to_follow.followers.filter(username=current_user.username).exists():
        who_to_follow.followers.remove(current_user)
        followers = who_to_follow.followers.count()
        return JsonResponse({"buttonText": "Follow", "followers": followers}, status=201)
    else:
        who_to_follow.followers.add(current_user)
        followers = who_to_follow.followers.count()
        return JsonResponse({"buttonText": "Unfollow", "followers": followers}, status=201)


@csrf_exempt
def like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
     
    user = request.user
    post = Post.objects.get(pk=post_id)
    if user not in post.liked_by.all():
        post.liked_by.add(user)
        post.likes += 1
        post.save()
        likes = post.likes
        return JsonResponse({
            "likes": likes,
            "buttonText": "Unlike"
        }, status=201)

    else:
        post.liked_by.remove(user)
        post.likes -= 1
        post.save()
        likes = post.likes
        return JsonResponse({
            "likes": likes,
            "buttonText": "Like"
        }, status=201)


