from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import viewsets
from .serializers import PostSerializer

import core.blog_settings
from blog.models import Category, Comment, Post, User
from users.forms import EditUserForm

from .forms import CommentForm, PostForm


def get_list(request):

    context = {}
    posts = Post.objects.all().select_related('category')
    for post in posts:
        post.tags = [post.category,]
    context['documents'] = posts
    return render(request, 'blog/list.html', context=context)


class PostViewSet(viewsets.ModelViewSet):
    """Endpoint для API запросов."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer


def get_filtered_posts(
        category_slug=None,
        profile=None,
        published_only=True
):
    """Получает офильтрованный и отсортированный список постов из БД.
    Args:
        category_slug: slug категории для фильтрации постов.
        profile: имя пользователя для фильтрации постов.
        published_only: флаг отображения только опубликованных постов.

    Returns:
        QuerySet с постами, отсортированный по дате публикации (новые сначала).
    """
    posts = Post.objects.annotate(comment_count=Count('comments'))

    posts = posts.select_related(
        'author',
        'category',
        'location'
    )

    if published_only:
        current_datetime = timezone.now()
        posts = posts.filter(
            pub_date__lte=current_datetime,
            is_published=True,
            category__is_published=True
        )
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if profile:
        posts = posts.filter(author=profile)

    return posts.order_by('-pub_date')


def get_page_objects(
    request,
    posts,
    page_param='page',
    default_page=1
):
    """Возвращает список объектов страницы просмотра постов.

    Args:
        request: HttpRequest объект.
        posts: QuerySet, содержащий посты.
        page_param: имя GET-параметра для номера страницы.
        default_page: номер страницы по умолчанию.

    Returns:
        Page object
    """
    paginator = Paginator(posts, core.blog_settings.VIEWED_POSTS)
    page_number = request.GET.get(page_param, default_page)

    return paginator.get_page(page_number)


def index(request):
    """Отображает главную страницу Блогикума."""
    posts = get_filtered_posts()
    page_obj = get_page_objects(request, posts)
    context = {'page_obj': page_obj}

    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Отображает страницу отдельной публикации с комментариями."""
    post = get_object_or_404(
        get_filtered_posts(published_only=False),
        pk=post_id
    )

    is_author = request.user.is_authenticated and post.author == request.user
    is_displayed = (
        post.is_published
        and post.category.is_published
        and post.pub_date <= timezone.now()
    )

    if not (is_author or is_displayed):
        raise Http404("Пост не найден.")

    context = {
        'post': post,
        'comments': post.comments.order_by('created_at'),
        'form': CommentForm(),
    }

    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Отображает страницу с постами указанной категории."""
    category = get_object_or_404(
        Category.objects.filter(slug=category_slug, is_published=True)
    )
    posts = get_filtered_posts(category_slug=category_slug)

    context = {
        'category': category,
        'page_obj': get_page_objects(request, posts),
    }

    return render(request, 'blog/category.html', context)


def author_profile(request, author):
    """Страница с публикациями автора."""
    user_profile = get_object_or_404(User, username=author)

    if request.user.is_authenticated and request.user == user_profile:
        reversed_posts = get_filtered_posts(profile=user_profile,
                                            published_only=False)
    else:
        reversed_posts = get_filtered_posts(profile=user_profile)
    page_obj = get_page_objects(request, reversed_posts)
    context = {'page_obj': page_obj, 'profile': user_profile}
    return render(request, 'blog/profile.html', context)


@login_required
def comment(request, post_id, comment_id=None):
    """Обрабатывает создание и редактирование комментария."""
    redirect_to_post = 'blog:post_detail'
    post = get_object_or_404(Post, id=post_id)
    if comment_id is not None:
        comment = get_object_or_404(Comment, pk=comment_id, post=post)
        if comment.author != request.user:
            return redirect(redirect_to_post, post_id=post_id)
    else:
        comment = None

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(redirect_to_post, post_id=post_id)

    context = {'form': form,
               'comment': comment,
               'post': post
               }

    return render(request, 'blog/comment.html', context)


@login_required
def edit_profile(request):
    """Страница редактирования профиля."""
    user = request.user
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', user)
    else:
        form = EditUserForm(instance=user)
    context = {'form': form}
    return render(request, 'blog/user.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)

    if request.method == 'GET' and request.user == comment.author:
        context = {'comment': comment}
        return render(request, template, context)

    if request.method == 'POST' and request.user == comment.author:
        comment.delete()

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def post(request, post_id=None):
    """Страница создания и редактирования поста."""
    template = 'blog/create.html'
    user = request.user

    if post_id is not None:
        current_post = get_object_or_404(Post, pk=post_id)
        if current_post.author != user:
            return redirect('blog:post_detail', post_id=post_id)
    else:
        current_post = None

    if request.method == 'POST':
        form = PostForm(request.POST,
                        files=request.FILES,
                        instance=current_post
                        )
        if form.is_valid():
            current_post = form.save(commit=False)
            current_post.author = request.user
            current_post.save()
            return redirect('blog:profile', author=user)
    else:
        form = PostForm(instance=current_post)

    context = {'form': form}
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    """Страница удаления поста."""
    template = 'blog/create.html'
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect('blog:index')

    if request.method == 'POST' and post.author == request.user:
        post.delete()
        return redirect('blog:profile', author=user)

    context = {'form': form}
    return render(request, template, context)


@login_required
def custom_logout(request):
    """Страница выхода из профиля."""
    template = 'registration/logged_out.html'
    logout(request)
    return render(request, template)




from .tasks import run_rag_process, run_statistical_analysis
from .tasks_dispatcher import run_task
def run_celery_task(request):
    """запуск celery task"""

    context = dict()

    task_name = request.GET.get('task_name')
    pid = request.GET.get('pid')

    print(task_name, pid)
    if task_name == 'rag':
        task = run_task.delay(
            'blog.tasks.run_rag_process',
            args=[pid],
            kwargs={}
        )
        # task = run_rag_process.delay('2345')
        context['task'] = task
    elif task_name == 'stat':
        task = run_task.delay(
            'blog.tasks.run_statistical_analysis',
            args=['stat', 'test'],
            kwargs={}
        )
        # task = run_rag_process.delay('2345')
        context['task'] = task

    return render(request, 'blog/graph.html', context=context)


