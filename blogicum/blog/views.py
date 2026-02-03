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





###############################################################################
    """
    Помоги решить следующую задачу.
Есть приложение на Django (Python).
В нем обрабатываются документы по определенным маршрутам.
При этом функция обработки документов отбирает ряд документов (может быть от десятка до 200- максимум 300) и далее поэтапно обрабатывает их.
На каждом этапе генерируются новые документы.
В результате прохождения всего цикла обработки у нас накапливаются данные следующего вида:

statistic_data = [
{
	"stage": "name of stage",
	"processed_documents": [{'id':'02342234', 'ref': ['02342234', ]}},  {'id':'f456', 'ref': ['02342234', ]}} ... ],
	"processing_time": 45.455
	},
	...
]

Кроме того есть словарь, который содержит вложенный словарь с полями документа, а ключом является ID документа:
docs_data = {
	'id': { 'name': '',
			'category': '',
			'color': '',
			'text': '',
			'year': '',
			...
			}
}

В списке statistic_data последовательно хранятся сведения об этапе обработки документов в виде словарей.
В каждом словаре:
- ключ stage содержит название этапа.
- ключ processed_documents содержит список обработанных документов. Каждая запись в этом списке - словарь, содержащий ID выходного документа и ref - ссылки на исходный документ (список).
- ключ processing_time содержит время, которое ушло на выполнение этапа разработки.

Необходимо написать view функцию и необходимые функции обработки данных для решения задачи визуализации на странице всей получившейся схемы обработки документов в виде графа.
Требования:
1. Граф должен отрисовываться на странице с применением библиотеки Vis.js
2. Граф должен быть многоуровневым в виде Hierarchical Layout - Scale-Free-Network
3. Начиная сверху каждый уровень - это этап обработки документов.
4. На каждом уровне отображаются документы, которые были подготовлены на данном этапе (id из списка processed_documents).
5. Ребра графа - это связи между документами (от документа id к документу ref).
6. Вершины - круглые. label для вершины - id документа. Если category = 'doc' то цвет вершины - белый. Если другое значение то цвет заливки верщины берется из color
7. при нажатии на вершину справа от графа на странице должна в столбик отобразиться информация о документе: name, category, year (поля не более 100 символов)

Дополнительные пояснения.
Все ID у документов - строковые значения.
Один документ может появляться на каком-то уровне (у него ref будет пустой строкой) и проходить через несколько уровней. Из одного документа может быть ветвления на несколько и наоборот (один документ может ссылаться на несколько).

Нужны ли какие-то уточняющие детали или задание понятное и однозначное?
    """
import json
# from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def visualize_graph(request):
    """Основная view для отображения страницы с графом"""
    return render(request, 'blog/graph.html')


@csrf_exempt
def get_graph_data(request):
    """API endpoint для получения данных графа в формате Vis.js"""
    if request.method == 'GET':
        # Здесь получаем statistic_data и docs_data
        # В реальном приложении это будет из базы данных или кэша
        statistic_data = get_statistic_data()  # Ваша функция получения данных
        docs_data = get_docs_data()           # Ваша функция получения данных

        graph_data = process_graph_data(statistic_data, docs_data)
        return JsonResponse(graph_data)

    return JsonResponse({'error': 'Invalid method'}, status=400)


def process_graph_data(statistic_data, docs_data):
    """Обработка данных для формирования графа"""
    nodes = []
    edges = []
    level_y_positions = {}

    # Определяем позиции по Y для каждого уровня (этапа)
    stages = [stage['stage'] for stage in statistic_data]
    stage_height = 5  # Расстояние между уровнями

    for i, stage in enumerate(stages):
        level_y_positions[stage] = i * stage_height

    # Обрабатываем каждый этап
    for stage_idx, stage_data in enumerate(statistic_data):
        stage_name = stage_data['stage']
        processed_docs = stage_data['processed_documents']

        # Создаем узлы для документов этого этапа
        for doc in processed_docs:
            doc_id = doc['id']

            # Получаем данные документа
            doc_info = docs_data.get(doc_id, {})

            # Определяем цвет узла
            color = 'white'
            if doc_info.get('category') != 'doc':
                color = doc_info.get('color', '#97C2FC')

            # Создаем узел
            node = {
                'id': f"{stage_name}_{doc_id}",
                'label': doc_id,
                'group': stage_name,
                'level': level_y_positions[stage_name],
                'color': color,
                'title': f"ID: {doc_id}<br>Stage: {stage_name}",
                'data': {
                    'original_id': doc_id,
                    'stage': stage_name,
                    'name': doc_info.get('name', ''),
                    'category': doc_info.get('category', ''),
                    'year': doc_info.get('year', ''),
                    'color': doc_info.get('color', ''),
                    'text': doc_info.get('text', '')[:100] if doc_info.get('text') else ''
                }
            }
            nodes.append(node)

            # Создаем ребра к документам-источникам
            for ref_doc_id in doc.get('ref', []):
                if ref_doc_id:  # Пропускаем пустые ссылки
                    # Ищем узел-источник на предыдущих этапах
                    for prev_stage_idx in range(stage_idx):
                        prev_stage = statistic_data[prev_stage_idx]
                        for prev_doc in prev_stage['processed_documents']:
                            if prev_doc['id'] == ref_doc_id:
                                edge = {
                                    'id': f"{ref_doc_id}_{doc_id}",
                                    'from': f"{prev_stage['stage']}_{ref_doc_id}",
                                    'to': f"{stage_name}_{doc_id}",
                                    'arrows': 'to',
                                    'color': {'color': '#848484'}
                                }
                                edges.append(edge)
                                break

    return {
        'nodes': nodes,
        'edges': edges,
        'stages': stages
    }


# Заглушки функций (в реальном приложении будут получать данные из БД/кэша)
def get_statistic_data():
    """Получение статистических данных обработки"""
    # Пример данных - в реальном приложении берется из базы

    data =  [
        {
            "stage": "init",
            "processed_documents": [
                {'id': '8', 'ref': []}, {'id':'13', 'ref': []}, ],
            "processing_time": 45.455
	    },
        {
            "stage": "search",
            "processed_documents": [
                {'id':'801', 'ref': ['8', ]}, {'id':'813', 'ref': ['8', ]}, {'id':'130', 'ref': ['13', ]}],
            "processing_time": 3.2
	    },
        {
            "stage": "extract_entities",
            "processed_documents": [
                {'id':'e1', 'ref': ['801', ]}, {'id':'e2', 'ref': ['801', ]}, {'id':'e3', 'ref': ['130', ]}],
            "processing_time": 3.2
	    },
    ]
    for i in range(0, 50):
        data[1]['processed_documents'].append({'id':str(i)+'d', 'ref': ['8']})
    return data


def get_docs_data():
    """Получение данных документов"""
    # Пример данных - в реальном приложении берется из базы
    data = {
        '8': {
            'name': 'Cat 8',
            'category': 'inftype',
            'color': 'red',
            'text': 'Patents',
            'year': '2025',
        },
        '13': {
            'name': 'Cat 13',
            'category': 'TR',
            'color': 'yellow',
            'text': 'tompson',
            'year': '2025',
        },
        '801': {
            'name': 'd801_',
            'category': 'doc',
            'color': 'white',
            'text': 'first doc',
            'year': '2022',
        },
        '813': {
            'name': 'd_813',
            'category': 'doc',
            'color': 'white',
            'text': 'second doc from patent',
            'year': '2023',
        },
        '130': {
            'name': 'd_130',
            'category': 'doc',
            'color': 'white',
            'text': 'doc from TR',
            'year': '2024',
        },
        'e1': {
            'name': 'ENTITY 1',
            'category': 'ent',
            'color': 'grey',
            'text': 'doc from TR',
            'year': '2024',
        },
        'e2': {
            'name': 'ENTITY 2',
            'category': 'ent',
            'color': 'grey',
            'text': 'doc from TR',
            'year': '2024',
        },
        'e3': {
            'name': 'ENTITY d_130',
            'category': 'ent',
            'color': 'grey',
            'text': 'doc from TR',
            'year': '2024',
        },
    }
    for i in range(0, 50):
        data[str(i)+'d'] = {
            'name': f'doc-{i}',
            'category': 'doc',
            'color': 'white',
            'text': 'doc ',
            'year': '2020',
        }
    return data
