from django.contrib import auth, messages 
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import MyUser
from decimal import *

def login(request):
    return render(request, 'login.html')

def authenticate(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = auth.authenticate(request, username=username, password=password)

    if not user:
        return redirect('login')

    auth.login(request, user)
    return redirect('index')

def signup(request):
    return render(request, 'signup.html')

def signup_submit(request):
    if request.FILES:
        image = request.FILES.get()
    else:
        image = './media/images/default_image.jpg' 
    username = request.POST.get('username')
    password = request.POST.get('password')
    realname = request.POST.get('realname')
    email = request.POST.get('email')
    phonenumber = request.POST.get('phonenumber')
    address = request.POST.get('address')

    try:
        user = MyUser.objects.create_user(username=username, realname=realname, email=email, phonenumber=phonenumber, address=address, password=password)
        return redirect('login')
    except:
        messages.error(request, '注册失败')
        return redirect('signup')

def open(request):
    return render(request, 'open.html')

def open_submit(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    phonenumber = request.POST.get('phonenumber')
    email = request.POST.get('email')
    address = request.POST.get('address')
    introduce = request.POST.get('introduce')

    try:
        user = MyUser.objects.create_seller(username=username, email=email, phonenumber=phonenumber, address=address, introduce = introduce, password=password)
        return redirect('login')
    except:
        return redirect('open')

@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required
def modify(request):
    return render(request, 'modify.html')

@login_required
def changepwd(request):
    return render(request, 'changepwd.html')


@login_required
def modify_seller(request, user_id):
    user = get_object_or_404(MyUser, pk=user_id)
    if request.FILES:
        user.image = request.FILES.get('image')     
    if request.method == 'POST':
        user.phonenumber = request.POST.get('phonenumber')
        user.email = request.POST.get('email')
        user.address = request.POST.get('address')
        user.introduce = request.POST.get('introduce')
        user.save()
    return redirect('modify')

@login_required
def modify_buyer(request, user_id):
    user = get_object_or_404(MyUser, pk=user_id)
    if request.FILES:
        user.image = request.FILES.get('image')
    if request.method == 'POST':
        user.phonenumber = request.POST.get('phonenumber')
        user.email = request.POST.get('email')
        user.address = request.POST.get('address')
        user.realname = request.POST.get('realname')
        user.save()
    return redirect('modify')

@login_required
def change_pwd(request, user_id):
    new_pwd = request.POST.get('new_pwd')
    again_pwd = request.POST.get('again_pwd')
    user = MyUser.objects.get(id = user_id)
    if new_pwd != again_pwd:
        return redirect('changepwd')
    user.set_password(new_pwd)
    user.save()
    return redirect('index')

@login_required
def recharge(request):
    return render(request, 'recharge.html')

@login_required
def recharge_complete(request, user_id):
    print(request.POST.get('money'))
    money = Decimal(request.POST.get('money'))
    user = MyUser.objects.get(id = user_id)
    user.money = user.money + money
    user.save()
    return redirect('modify')

@login_required
def withdraw(request):
    return render(request, 'withdraw.html')

@login_required
def withdraw_complete(request, user_id):
    print(request.POST.get('money'))
    money = Decimal(request.POST.get('money'))
    user = MyUser.objects.get(id = user_id)
    if money > user.money :
        return redirect('withdraw')
    user.money = user.money - money
    user.save()
    return redirect('modify')
