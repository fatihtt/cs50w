from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from django.template.response import TemplateResponse

from .models import User, Listing, Category, Bid, Watch, Comment, WinnerBid


def get_cur_price(listing):
    current_bids = Bid.objects.filter(listing=listing).order_by('-price').values()

    if len(current_bids) < 1:
        return listing.starting_bid
    else:
        return current_bids.first()["price"]
    
def watchlist_count(request):
    watchlist_count = -1
    if request.user.is_authenticated:
        watchlist_count = Watch.objects.filter(user=request.user).count()
    return watchlist_count

def index(request):
    # Take all not ended (active) listings
    current_listings = Listing.objects.filter(ended=False)

    # Take current price for every listing item
    current_prices = []
    for listing in current_listings:
        current_prices.append(get_cur_price(listing))
        # # If no bid -> current_price = starting_bid
        # # Else -> current_price = max_bid(price of bids)
        # current_bids = Bid.objects.filter(listing=listing).order_by('-price').values()

        # if len(current_bids) < 1:
        #     current_prices.append(listing.starting_bid)
        # else:
        #     current_prices.append(current_bids.first().price())
    return render(request, "auctions/index.html", {
        "listings": zip(current_listings, current_prices),
        "watchlist_count": watchlist_count(request)
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
                "watchlist_count": watchlist_count(request),
                "message": f"Error while creating new listing. {e}"
            })
    else:
        return render(request, "auctions/new-listing.html", {
            "categories": categories,
            "watchlist_count": watchlist_count(request)
        })

def listing(request):
    try:
        # Get list id
        listing_id = int(request.GET.get("l"))
        
        # Find list
        listings = Listing.objects.filter(id=listing_id).annotate(total_bids=Count('bid'))

        if len(listings) != 1:
            raise ValueError("No list with given id!")
        
        my_listing = listings.first()
        
        # Check added watchlist or not
        in_the_list = False

        if request.user.is_authenticated:
            watch_entry_count = Watch.objects.filter(listing=my_listing, user=request.user).count()

            if watch_entry_count > 0:
                in_the_list = True

        # Check current user favorite or not
        you_are_favorite = False

        if request.user.is_authenticated:
            current_bids = Bid.objects.filter(listing=my_listing, user=request.user).order_by('-price').values()

            if current_bids.count() > 0 and current_bids.first()["price"] == get_cur_price(my_listing):
                you_are_favorite = True

        # Take comments
        comments = Comment.objects.filter(listing=my_listing).order_by('-time')

        # Check wether this user can close or not
        can_close = False

        if request.user.is_authenticated and my_listing.user == request.user:
            can_close = True

        if request.method == "POST":
            # Take price for new bid
            price = float(request.POST.get('bid-amount'))
            
            # Check price
            if price <= get_cur_price(my_listing):
                raise ValueError("Your bid must greater than current price")
            
            # Create new bid
            new_bid = Bid(listing=my_listing, user=request.user, price=price)
            new_bid.save()

            return HttpResponseRedirect(f"listing?l={listing_id}")

    except Exception as e:
        return render(request, "auctions/listing.html", {
            "listing": my_listing,
            "cur_price": get_cur_price(my_listing),
            "in_the_list": in_the_list,
            "you_are_favorite": you_are_favorite,
            "comments": comments,
            "can_close": can_close,
            "watchlist_count": watchlist_count(request),
            "message": f"Error while finding list. {e}"
        })
    return render(request, "auctions/listing.html", {
        "listing": my_listing,
        "cur_price": get_cur_price(my_listing),
        "in_the_list": in_the_list,
        "you_are_favorite": you_are_favorite,
        "comments": comments,
        "can_close": can_close,
        "watchlist_count": watchlist_count(request)
    })

def add_to_watchlist(request):
    try:
        # Get list_id from querystring
        listing_id = int(request.GET.get("l"))

        # Find list
        listings = Listing.objects.filter(id=listing_id).annotate(total_bids=Count('bid'))

        if len(listings) != 1:
            raise ValueError("No list with given id!")
        
        my_listing = listings.first()

        # Check user has watchlist entry for this listing or has not
        watch_entries = Watch.objects.filter(user=request.user, listing=my_listing)

        if watch_entries.count() > 0:
            for watch_entry in watch_entries:
                watch_entry.delete()
        else:
            # Create watchlist entry
            new_watch = Watch(listing=my_listing, user=request.user)
            new_watch.save()

        # Redirect to listing
        return HttpResponseRedirect(f"listing?l={listing_id}")
    except Exception as e:
        return HttpResponseRedirect("./")
    
def add_comment(request):
    try:
        # Get list_id from querystring
        listing_id = int(request.GET.get("l"))

        # Find list
        listings = Listing.objects.filter(id=listing_id).annotate(total_bids=Count('bid'))

        if len(listings) != 1:
            raise ValueError("No list with given id!")
        
        my_listing = listings.first()

        # Get comment text from POST
        comment_text = request.POST.get('comment_text')
        if len(comment_text) < 1:
            raise ValueError("no comment text")
        
        # Save new comment
        new_comment = Comment(listing=my_listing, user=request.user, message=comment_text)
        new_comment.save()

        return HttpResponseRedirect(f"listing?l={listing_id}")

    except Exception as e:
        return HttpResponseRedirect(f"./")

def close_auction(request):
    try:
        # Get list_id from querystring
        listing_id = int(request.GET.get("l"))

        # Find list
        listings = Listing.objects.filter(id=listing_id).annotate(total_bids=Count('bid'))

        if len(listings) != 1:
            raise ValueError("No list with given id!")
        
        my_listing = listings.first()

        # Check wether can close or not
        if my_listing.user == request.user:
            # Find winner bid
            bids = Bid.objects.filter(listing=my_listing).order_by("-price")

            if bids.count() > 0:
                # Save winner bid
                winner = WinnerBid(listing=my_listing, bid=bids.first())
                winner.save()

            # Close auction
            my_listing.ended = True
            my_listing.save()
            # Redirect to listing
            return HttpResponseRedirect(f"listing?l={listing_id}")
        else:
            raise ValueError("This user can not close this auction")
    except:
        return HttpResponseRedirect(f"./")

def watchlist(request):
    try:
        # Take user's watchlist listings
        watches = Watch.objects.filter(user=request.user)

        listings = []
        prices = []

        for watch in watches:
            listings.append(watch.listing)
            prices.append(get_cur_price(watch.listing))

        return render(request, "auctions/watchlist.html", {
            "listings": listings,
            "watchlist_count": watchlist_count(request)
        })
    except Exception as e:
        return render(request, "auctions/watchlist.html", {
            "listings": zip(listings, prices),
            "watchlist_count": watchlist_count(request),
        })

def categories(request):
    # take categories with count of listings
    all_categories = Category.objects.all().annotate(listings_count=Count('listing'))
    return render(request, "auctions/categories.html", {
        "categories": all_categories,
        "watchlist_count": watchlist_count(request),
    })

def category(request):
    try:
        # get category id
        category_id = request.GET.get("c")
        # get category
        categories = Category.objects.filter(id=category_id)
        if categories.count() != 1:
            raise ValueError("No category with this id")
        
        category = categories.first()
        listings = Listing.objects.filter(category=category, ended=False)
        prices = []
        for listing in listings:
            prices.append(get_cur_price(listing))
        return render(request, "auctions/category.html", {
            "watchlist_count": watchlist_count(request),
            "cur_category": category,
            "listings": zip(listings, prices)
        })
    except Exception as e:
        print(e)
        return HttpResponseRedirect("categories")

