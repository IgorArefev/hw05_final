from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def paginator(request, queryset):
    page = Paginator(queryset, settings.PAGINATOR_VALUE)
    page_number = request.GET.get('page')
    page_obj = page.get_page(page_number)
    return page_obj


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    page_obj = paginator(request, post_list)
    template = 'posts/index.html'
    context = {'page_obj': page_obj, }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(request, post_list)
    template = 'posts/group_list.html'
    context = {'group': group, 'page_obj': page_obj, }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = paginator(request, post_list)
    following = False
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    template = 'posts/profile.html'
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    following = False
    if request.user.is_authenticated:
        following = post.author.following.filter(user=request.user).exists()
    form = CommentForm()
    comments_list = post.comments.all()
    comments_obj = paginator(request, comments_list)
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'form': form,
        'page_obj': comments_obj,
        'following': following,
        'author': post.author
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    template = 'posts/create_post.html'
    context = {'form': form, }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not post.author == request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    template = 'posts/create_post.html'
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    )
    page_obj = paginator(request, posts)
    template = 'posts/follow.html'
    context = {'page_obj': page_obj, }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect('posts:profile', username=username)
    return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    user = request.user
    if Follow.objects.filter(user=user, author__username=username).exists():
        Follow.objects.get(user=user, author__username=username).delete()
        return redirect('posts:profile', username=username)
    return redirect('posts:index')
