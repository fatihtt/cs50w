from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new-listing", views.new_listing, name="new-listing"),
    path("listing", views.listing, name="listing"),
    path("add-to-watchlist", views.add_to_watchlist, name="add-to-watchlist"),
    path("add-comment", views.add_comment, name="add-comment"),
    path("close-auction", views.close_auction, name="close-auction")
]
