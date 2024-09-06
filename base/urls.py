from django.urls import path
from . import views


urlpatterns=[
    path("", views.home, name="home"),
    path("room/<str:pk>/", views.room, name="room"),
    path("profile/<str:pk>/", views.userProfile, name="profile"),
    path("updateroom/<str:pk>/", views.updateRoom, name="updateroom"),
    path("deleteroom/<str:pk>/", views.deleteRoom, name="deleteroom"),
    path("createroom/", views.createRoom, name="createroom"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutPage, name="logout"),
    path("register/", views.registerPage, name="register"),
    path("update-user/", views.updateUser, name="update-user")
    
]