from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page


#@cache_page(1 * 20)
def index(request):
    add_com = True
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page')  
    page = paginator.get_page(page_number) 
    return render(
                  request,
                  'index.html',
                  {'page': page, 'paginator': paginator, 'add_com': add_com}
                 )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    paginator = Paginator(posts, 10) 
    page_number = request.GET.get('page')  
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 
                                          'page': page, 
                                          'paginator': paginator, 
                                          'add_com': True})    


@login_required
def new_post(request):
    is_edit = False
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new.html', {'form': form, 'is_edit': is_edit})


def profile(request, username):
    user_name = get_object_or_404(User, username=username)
    user_posts = user_name.posts.all()
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=user_name).exists()
    else:
        following = False   
    paginator = Paginator(user_posts, 10) 
    page_number = request.GET.get('page')  
    page = paginator.get_page(page_number) 
    return render(request, 'profile.html', {'page': page, 
                                            'paginator': paginator,
                                            'user_name': user_name, 
                                            'add_com': True,
                                            'following': following
                                            })
 
 
def post_view(request, username, post_id):
        post = get_object_or_404(Post, pk=post_id, author__username=username)
        user_name =  post.author
        post_com = post.comments.all() 
        com_form = CommentForm()
        com_edit = False
        if request.user.is_authenticated:
            following = Follow.objects.filter(user=request.user,
                                              author=user_name).exists()
        else:
            following = False
        return render(request, 'post_view.html', {'post': post,
                                                  'user_name': user_name,
                                                  'post_com': post_com,
                                                  'com_form': com_form,
                                                  'add_com': False,
                                                  'following':following,})
                                                  #'comment':comment


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect('post_view', username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, 
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('post_view', username=username, post_id=post_id)
    return render(request, 'new.html', {'form': form, 'post': post, 
                                        'is_edit': True})

@login_required
def post_delete(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect('post_view', username=username, post_id=post_id)
    if Post.objects.filter(pk=post_id, author__username=username).exists():
        post.delete()
        return redirect('profile', username=username)    


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    com_form = CommentForm(request.POST or None)
    if com_form.is_valid():
        comment = com_form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post_view', username=username, post_id=post_id)

@login_required
def edit_comment(request, username, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    comment = get_object_or_404(Comment, id=comment_id)
    user_name =  post.author
    com_edit = True
    post_com = post.comments.all() 
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                              author=user_name).exists()
    else:
        following = False
    com_form = CommentForm(request.POST or None, instance=comment)
    if request.user != comment.author:
        return redirect('post_view', username=username, post_id=post_id)
    if com_form.is_valid():
        com_form.save()
        com_edit = False
        return redirect('post_view', username=username, post_id=post_id)
    return render(request, 'post_view.html', {'post': post,
                                              'user_name': user_name,
                                              'post_com': post_com,
                                              'com_form': com_form,
                                              'add_com': False,
                                              'following':following,
                                              'comment': comment,
                                              'com_edit': com_edit}) 
   

@login_required
def delete_comment(request, username, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('post_view', username=username, post_id=post_id)
    if Comment.objects.filter(author=request.user, post=post_id,
                             id=comment_id).exists():
        com_delete = get_object_or_404(Comment, author=request.user,
                                                post=post_id,
                                                id=comment_id).delete()
    return redirect('post_view', username=username, post_id=post_id)   

@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page')  
    page = paginator.get_page(page_number) 
    return render(
                  request,
                  'follow.html',
                  {'page': page, 'paginator': paginator, 'add_com': True}
                 )
   

@login_required
def profile_follow(request, username):
    follow_profile = get_object_or_404(User, username=username)
    if request.user != follow_profile:
        follow = Follow.objects.get_or_create(user=request.user, 
                                              author=follow_profile)
    return redirect('profile', username=username)

@login_required
def profile_unfollow(request, username):
    follow_profile = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user,
                             author=follow_profile).exists():
        unfollow = get_object_or_404(Follow, user=request.user,
                                             author=follow_profile).delete()
    return redirect('profile', username=username)

def page_not_found(request, exception):
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )

def server_error(request):
    return render(request, "misc/500.html", status=500)
