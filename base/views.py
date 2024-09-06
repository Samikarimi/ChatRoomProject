from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Room, Topic, User, Message
from .forms import RoomForm, UserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


def loginPage(request):
    page="login"
    if request.user.is_authenticated:
        return redirect("home")     
    
    if request.method=="POST":
        username=request.POST.get("username").lower()
        password=request.POST.get("password")

        try:
            user=User.objects.get(username=username)
        except:  
            messages.error(request, "user does not exist")  

        user=authenticate(request, username=username, password=password)    

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "username or password is wrong")   



    return render(request, "base/login_register.html",{"page":page})


def logoutPage(request):
    logout(request)
    return redirect("home")


def registerPage(request):
    page="register"
    form=UserCreationForm()
    
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect("home")
            

    return render(request, "base/login_register.html", {
        "page":page,
        "form":form
    })    


def home(request):
    q=request.GET.get("q") if request.GET.get("q") != None else ""
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_count=len(rooms)
    topics=Topic.objects.all()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q)).order_by("-created")[:3]
    return render(request, "base/home.html",{
        "rooms":rooms,
        "topics":topics,
        "room_count":room_count,
        "room_messages":room_messages,

    })


def room(request,pk):
    room=Room.objects.get(id=pk)
    room_messages=room.message_set.all().order_by("-created")
    participants=room.participants.all()

    if request.method== "POST":
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    return render(request, "base/room.html",{
        "room":room,
        "room_messages":room_messages,
        "participants":participants
    })




@login_required(login_url="login")
def createRoom(request):
    form=RoomForm()
    topics=Topic.objects.all()
    if request.method== "POST":
        topic_name=request.POST.get("topic")
        topic, created=Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")

    return render(request, "base/room_form.html", {
        "form":form,
        "topics":topics
    })


@login_required(login_url="login")
def updateRoom(request, pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)
    topics=Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("YOU ARE NOT ALLOWED HERE!")

    if request.method=="POST":
        topic_name=request.POST.get("topic")
        topic, created=Topic.objects.get_or_create(name=topic_name)
        room.name=request.POST.get("name")
        room.description=request.POST.get("description")
        room.topic=topic
        room.save()
        return redirect("home")


    return render(request, "base/room_form.html",{
        "room":room,
        "form":form,
        "topics":topics
    })    



@login_required(login_url="login")
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.method=='POST':
        room.delete()
        return redirect("home")

    
    if request.user != room.host:
        return HttpResponse("YOU ARE NOT ALLOWED HERE!")    
    
    return render(request, "base/delete.html",{
        "obj":room
    })       



def userProfile(request, pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    return render(request, "base/profile.html" ,{
        "user":user,
        "rooms":rooms,
        "room_messages":room_messages,
        "topics":topics,
    })


@login_required(login_url="login")
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)
    if request.method == "POST":
        form=UserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile", pk=user.id)

    return render(request, "base/update-user.html",{
        "form":form
    })    