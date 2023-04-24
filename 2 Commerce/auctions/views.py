from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Category, Bid


def index(request):
    # Take all not ended (active) listings
    current_listings = Listing.objects.filter(ended=False)

    # Take current price for every listing item
    current_prices = []
    for listing in current_listings:
        # If no bid -> current_price = starting_bid
        # Else -> current_price = max_bid(price of bids)
        current_bids = Bid.objects.filter(listing=listing).order_by('-price').values()

        if len(current_bids) < 1:
            current_prices.append(listing.starting_bid)
        else:
            current_prices.append(current_bids.first().price())
    return render(request, "auctions/index.html", {
        "listings": zip(current_listings, current_prices)
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def new_listing(request):
    categories = Category.objects.all()
    if request.method == "POST":
        try:
            # Take inputs
            category = request.POST["categories"]
            print("category: ", category)
            user = request.user
            title = request.POST["title"]
            description = request.POST["description"]
            starting_bid = request.POST["starting_bid"] 
            image_url = request.POST["image_url"]

            # Check inputs
            if len(title) < 1 or len(description) < 1 or len(starting_bid) < 1:
                return render(request, "auctions/new-listing.html", {
                "message": "Input expectations not satisfied!",
                "categories": categories
            }) 

            # Create listing
            new_listing = Listing(category=Category.objects.get(id=int(category)), user=user, title=title, description=description, starting_bid=float(starting_bid), image_url=image_url)
            print("came to save")
            new_listing.save()

            # Redirect if successfully created
            return HttpResponseRedirect(reverse("index"))
            
        except Exception as e:
            return render(request, "auctions/new-listing.html", {
                "categories": categories,
                "message": f"Error while creating new listing. {e}"
            })
    else:
        return render(request, "auctions/new-listing.html", {
            "categories": categories
        })

def listing(request):
    if request.method == "POST":
        ...
    else:
        try:
            # Get list id
            listing_id = int(request.GET.get("l"))
            
            # Find list
            listings = Listing.objects.filter(id=listing_id)

            if len(listings) != 1:
                raise ValueError("No list with given id!")
            
            my_listing = listings.first()

        except Exception as e:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": f"Error while finding list. {e}"
            })
    return render(request, "auctions/listing.html", {
        "listing": my_listing
    })