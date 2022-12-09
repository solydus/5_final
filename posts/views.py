from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.views.generic import DeleteView
from django.shortcuts import render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator


POST_V = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POST_V)
    page_number = request.GET.get('page')
    template = 'posts/index.html'
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group(request):
    template = 'posts/group_list.html'
    return render(request, template)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POST_V)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "posts/group_list.html",
                  {"group": group, "page_obj": page_obj})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    page_obj = paginator(request, posts)
    template = 'posts/profile.html'
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author).exists
    else:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts': posts,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница одной записи."""
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related('author')
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if post.author != request.user:
        return redirect("posts:posts_detail", post_id)
    if form.is_valid():
        form.save()
        return redirect("posts:posts_detail", post_id)
    context = {
        "form": form,
        "is_edit": is_edit,
    }
    return render(request, "posts/create.html", context)


class postdelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/delete.html'
    fields = ['text', 'group', 'author']
    context_object_name = 'post_delete'
    success_url = '/'


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
    form = PostForm()
    data_form = {'form': form}
    return render(request, 'posts/create.html', data_form)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'form': form,
    }
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:posts_detail', post_id=post_id)
    return render(request, 'posts/post_detail.html', context)


@login_required
def follow_index(request):
    posts = (
        Post.objects
        .select_related('author', 'group')
        .filter(author__following__user=request.user))
    page_obj = paginator(request, posts)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if request.user != author:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=author)


def page_not_found(request, exception):
    return render(request, 'includes/404.html', status=404)
