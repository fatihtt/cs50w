
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new-post", views.new_post, name="new-post"),
    path("edit-post/<int:post_id>", views.edit_post, name="edit-post"),
    path("favorite-toggle-post/<int:post_id>", views.favorite_toggle, name="favorite-toggle-post"),
    path("u/<str:user_name>", views.view_profile, name="u"),
    path("edit-fallow/<int:user_id>", views.toggle_fallow, name="edit-fallow")
]
