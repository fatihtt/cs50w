from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new-entry", views.new_entry, name="new-entry"),
    path("edit-entry", views.edit_entry, name="edit-entry"),
    path("get-random", views.get_random, name="get-random"),
    path("<str:title>", views.entry, name="entry")
]
