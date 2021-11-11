from django.urls import path
from django.conf.urls import include
from django.conf.urls import url
from . import views
from django.conf import settings  
from django.conf.urls.static import static  

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("myprofile", views.myprofile, name="myprofile"),
    path("change_password", views.change_password, name="change_password"),
    url(r'^password/$', views.change_password, name='change_password'),

    path("createproject", views.createproject, name="createproject"),
    path("projects", views.projects, name="projects"),
    path("projects/<str:category>", views.projects, name="projects"),
    path("projects/<int:id>/", views.processproject, name="processproject"),
    path("projects/<int:id>/donate/", views.donate, name="donate"),

    path("projects/<int:id>/createrequest/", views.createrequest, name="createrequest"),
    path("projects/createrequest/", views.createrequest, name="createrequest"),
    path("projects/<int:id>/requests/", views.requests, name="requests"),
    path("requests/<int:id>/", views.processrequest, name="processrequest"),
    path("requests/<int:id>/vote/", views.vote, name="vote"),
    path("requests/<int:id>/makepayment/", views.makepayment, name="makepayment"),

    path("category", views.category, name="category"),
    
]