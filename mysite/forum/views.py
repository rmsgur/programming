from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Post, MyUser, UserItem
from .forms import PostForm, ReplyForm, UserItemForm
from django.db.models import Q
from decimal import *

def index(request):
    posts = Post.objects.order_by('-created_at')
    return render(request, 'index.html', {'posts': posts})

def search(request):
    schWords = request.GET.get('schWord')
    if len(schWords) == 0:
         return render(request, 'notfound.html')

    schWord = schWords.split()
    posts = Post.objects.filter(Q(title__icontains=schWord[0]) | Q(content__icontains=schWord[0]) |  Q(type__icontains=schWord[0])).distinct()
    
    for word in schWord:
        posts = (posts | Post.objects.filter(Q(title__icontains=word) | Q(content__icontains=word) |  Q(type__icontains=word)).distinct()).distinct()

    shops = MyUser.objects.filter(id = 0)
    for post in posts:
        shops = (shops | MyUser.objects.filter(id = post.author_id))

    is_exist = False
    for post in posts:
        is_exist = True
        break

    if is_exist == False:
       return render(request, 'notfound.html')

    return render(request, 'search.html', {'posts': posts, 'schWord': schWords, 'shops': shops, 'item_type': '', 'sorting': '', 'shop_id': 0})

def filter(request, schWords, shop_id, item_type, sorting):
    if len(schWords) == 0:
        return render(request, 'notfound.html')

    schWord = schWords.split()
    posts = Post.objects.filter(Q(title__icontains=schWord[0]) | Q(content__icontains=schWord[0]) |  Q(type__icontains=schWord[0])).distinct()

    for word in schWord:
        posts = (posts | Post.objects.filter(Q(title__icontains=word) | Q(content__icontains=word) |  Q(type__icontains=word)).distinct()).distinct()

    if int(shop_id) > 0:
        posts = (posts & Post.objects.filter(Q(author_id=int(shop_id))).distinct()).distinct()

    if len(item_type) > 0:
        posts = (posts & Post.objects.filter(Q(type=item_type)).distinct()).distinct()

    shops = MyUser.objects.filter(id = 0)
    for post in posts:
        shops = (shops | MyUser.objects.filter(id = post.author_id))

    if sorting == 'score':
        posts = posts.order_by('-avg_score')

    elif sorting == 'uptodown':
        posts = posts.order_by('-price')

    elif sorting == 'downtoup':
        posts = posts.order_by('price')

    is_exist = False
    for post in posts:
        is_exist = True
        break

    if is_exist == False or len(schWords) == 0:
        return render(request, 'notfound.html')

    return render(request, 'search.html', {'posts': posts, 'schWord': schWords, 'shops': shops, 'item_type': item_type, 'sorting': sorting, 'shop_id': shop_id})

def menu(request, menu_name):
    schWord = ''
    if menu_name == 'fish':
        schWord = '鱼类'
    elif menu_name == 'crustacea':
        schWord = '甲壳类'
    elif menu_name == 'mammalia':
        schWord = '哺乳纲'
    elif menu_name == 'mollusca':
        schWord = '软体动物'
    elif menu_name == 'coelenterate':
        schWord = '腔肠动物'

    posts = Post.objects.filter(Q(type__icontains=schWord)).distinct()

    shops = MyUser.objects.filter(id = 0)
    for post in posts:
        shops = (shops | MyUser.objects.filter(id = post.author_id))

    is_exist = False
    for pp in posts:
        is_exist = True
        break

    if is_exist == False or len(schWord) == 0:
        return render(request, 'notfound.html', {'posts': posts})
    return render(request, 'search.html', {'posts': posts, 'shops': shops, 'item_type': menu_name, 'sorting': ''})


@login_required
def create(request):
    if request.user.is_seller == False:
        return redirect('index')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
    else:
        form = PostForm(None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.type = request.POST.get('type')
        if not post.type:
            post.type = ''
        post.image = form.cleaned_data['image']
        post.total_score = 0.
        post.total_customer = 0
        post.avg_score = 0.
        post.save()
        form = PostForm()
        return redirect('create_complete')

    return render(request, 'create.html', {'form': form})

def post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user =request.user
    useritems = UserItem.objects.filter(item_id = post_id, user_id = user.id)
    is_exist = False
    for useritem in useritems:
        is_exist = True
        if useritem.is_scored == True:
             return render(request, 'post.html', {'post': post, 'reply_form': ReplyForm(), 'is_scored': True})
    if is_exist == False:
        return render(request, 'post.html', {'post': post, 'reply_form': ReplyForm(), 'is_scored': True})

    return render(request, 'post.html', {'post': post, 'reply_form': ReplyForm(), 'is_scored': False})

@login_required
@require_POST
def reply(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = ReplyForm(request.POST)
    is_scored = False
    is_exist = False
    user =request.user
    p_user = get_object_or_404(MyUser, pk=post.author_id)
    useritems = UserItem.objects.filter(item_id = post_id, user_id = user.id)
    for useritem in useritems:
        is_exist = True
        if useritem.is_scored == True:
            is_scored = True
            break
    for useritem in useritems:
        useritem.is_scored = True
        useritem.save()
    if form.is_valid():
        reply = form.save(commit=False)
        reply.author = request.user
        reply.post = post
        if is_scored == False and is_exist == True:
            post.total_score += float(request.POST.get('input-star'))
            post.total_customer += 1
            post.avg_score = post.total_score / post.total_customer
            reply.score = float(request.POST.get('input-star'))
            p_user = get_object_or_404(MyUser, pk=post.author_id)
            p_user.total_score += float(request.POST.get('input-star'))
            p_user.total_customer += 1
            p_user.avg_score = p_user.total_score / p_user.total_customer
        else:
            reply.score = 10.0
        post.save()
        reply.save()
        p_user.save()
    else:
        print('not valid')

    return redirect('post', post.id)

def purchase(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = UserItemForm(request.POST)
    else:
        form = UserItemForm(None)
    if form.is_valid():
        useritem = form.save(commit=False)
        useritem.user_id = request.user
        user = get_object_or_404(MyUser, pk=useritem.user_id_id)
        if user.money < (post.price * useritem.quantity):
            return redirect('purchase_fail')
        useritem.user_id = request.user
        useritem.item_id = post_id
        useritem.item_title = post.title
        useritem.price = post.price
        useritem.is_purchased = True
        useritem.product_author = post.author
        useritem.total_price = useritem.quantity * useritem.price
        user = get_object_or_404(MyUser, pk=useritem.user_id_id)
        user.money -= useritem.total_price
        post.quantity -= useritem.quantity
        post.save()
        user.save()
        useritem.save()
        return redirect('purchase_success')
    return render(request, 'purchase.html', {'post': post, 'form': form})

def shoppingcart(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = UserItemForm(request.POST)
    else:
        form = UserItemForm(None)
    if form.is_valid():
        useritem = form.save(commit=False)
        useritem.user_id = request.user
        useritem.item_id = post_id
        useritem.item_title = post.title
        useritem.price = post.price
        useritem.total_price = useritem.quantity * useritem.price
        useritem.is_in_cart = True
        user = get_object_or_404(MyUser, pk=useritem.user_id_id)
        user.total_price += post.price * useritem.quantity
        useritem.save()
        user.save()
        return redirect('mycart')
    return render(request, 'shopping_cart.html', {'post': post, 'form': form})

def my_cart(request):
    if request.user.is_seller == True:
        return redirect('index')
    useritems = UserItem.objects.filter(user_id=request.user)
    useritems = useritems.order_by('-date_added')
    return render(request, 'my_cart.html', {'useritems': useritems} )

def shop_info(request, shop_id):
    user = get_object_or_404(MyUser, pk=shop_id)
    posts = Post.objects.filter(author_id=user.id)
    return render(request, 'shop_info.html', {'user': user, 'posts': posts})

def shop_evaluate(request, shop_id):
    user = get_object_or_404(MyUser, pk=shop_id)
    if request.method == 'POST':
        user.total_score += float(request.POST.get('input-star'))
        user.total_customer += 1
        user.avg_score = user.total_score / user.total_customer
        user.save()
    else:
        print("shop_evaluate Error")

    return redirect('shop_info', user.id)

def create_complete(request):
    return render(request, 'create_complete.html')

def post_change(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author_id != request.user.id:
        return redirect('index')

    if request.method == 'POST' and request.FILES:
        form = PostForm(request.POST, request.FILES)
    elif request.method == 'POST':
        post.quantity = int(request.POST.get('quantity'))
        post.content = request.POST.get('content')
        post.price = Decimal(request.POST.get('price'))
        post.type = request.POST.get('type')
        post.save()
        return redirect('post', post_id)
    else:
        form = PostForm(None)

    if form.is_valid():
        post.type = request.POST.get('type')
        if not post.type:
            post.type = ''
        post.image = form.cleaned_data['image']
        post.save()
        form = PostForm()
        return redirect('post', post_id)
    return render(request, 'post_change.html', {'post': post, 'form': form})

def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author_id == request.user.id :
        Post.objects.filter(id=post_id).delete()
    useritems = UserItem.objects.filter(item_id = post_id)
    for useritem in useritems:
        UserItem.objects.filter(id=useritem.id).delete()
    return redirect('index')

def my_order(request, user_id):
    myuser = request.user
    if myuser.is_seller == True:
        useritems = UserItem.objects.filter(product_author=request.user)
    else:
        useritems = UserItem.objects.filter(user_id=request.user)
    useritems = useritems.order_by('-date_added')
    return render(request, 'my_order.html', {'useritems': useritems})

def purchase_success(request):
    return render(request, 'purchase_success.html')

def send_clicked(request, useritem_id):
    print("SEND_CLICKED")
    useritem = get_object_or_404(UserItem, pk=useritem_id)
    useritem.is_sended = True
    useritem.save()

    myuser = request.user
    if myuser.is_seller == True:
        useritems = UserItem.objects.filter(product_author=request.user)
    else:
        useritems = UserItem.objects.filter(user_id=request.user)
    useritems = useritems.order_by('-date_added')

    return render(request, 'my_order.html', {'useritems': useritems})


def receive_clicked(request, useritem_id):
    print("RECEIVE_CLICKED")
    useritem = get_object_or_404(UserItem, pk=useritem_id)
    useritem.is_received = True
    useritem.save()

    myuser = request.user
    seller = get_object_or_404(MyUser, username=useritem.product_author)
    seller.money += useritem.total_price
    seller.save()

    if myuser.is_seller == True:
        useritems = UserItem.objects.filter(product_author=request.user)
    else:
        useritems = UserItem.objects.filter(user_id=request.user)
    useritems = useritems.order_by('-date_added')

    return render(request, 'my_order.html', {'useritems': useritems})

def purchase_fail(request):
    return render(request,'needcharge.html')

def mycart_delete(request):
    list=request.POST.getlist('check1')
    for id in list:
        UserItem.objects.filter(id=id).delete()
    return redirect('mycart')

def mycart_purchase(request):
    list=request.POST.getlist('check1')
    for id in list:
        return redirect('index')
    return redirect('index')

