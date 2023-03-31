from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.paginator import Paginator
from .models import Post, Group
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import PostForm


User = get_user_model()
QUANTITY_OF_POSTS_ON_PAGE = 10


def authorized_only(func):
    '''
    Проверка авторизации.
    '''
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/auth/login/')
    return check_user


def index(request):
    '''
    Главная страница.
    '''
    post_list = get_list_or_404(Post.objects.order_by('-pub_date'))
    paginator = Paginator(post_list, QUANTITY_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def groups(request, slug):
    '''
    Посты Группы.
    '''
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().order_by('-pub_date')
    paginator = Paginator(post_list, QUANTITY_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    '''
    Профиль.
    '''
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    post_count = Post.objects.filter(author=author).count()
    paginator = Paginator(post_list, QUANTITY_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/profile.html'
    context = {
        'author': author,
        'post_list': post_list,
        'page_obj': page_obj,
        'post_count': post_count
    }
    return render(request, template, context)


def post_detail(request, post_id):
    '''
    Посты автора.
    '''
    template = 'posts/post_detail.html'
    post = Post.objects.get(id=post_id)
    post_count = post.author.posts.count()
    author = post.author
    date_of_post = post.pub_date
    context = {
        'author': author,
        'post_count': post_count,
        'post': post,
        'date_of_post': date_of_post,
    }
    return render(request, template, context)


@authorized_only
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user.username)
    form = PostForm()
    template = 'posts/create_post.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@authorized_only
def post_edit(request, post_id):
    '''
    Редактирование поста.
    '''
    is_edit = True
    post = Post.objects.get(id=post_id)
    group = post.group
    if post.author == request.user:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save()
                return redirect('posts:post_detail', post_id=post.id)
        else:
            form = PostForm(instance=post)
            context = {'form': form,
                       'post': post,
                       'group': group,
                       'is_edit': is_edit, }
            return render(request, 'posts/create_post.html', context)
    form = PostForm(instance=post)
    return render(request, 'posts/create_post.html', context, {'form': form})
