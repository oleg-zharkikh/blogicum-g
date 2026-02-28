from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('',
         views.index,
         name='index'),

    path('list/', views.get_list),

    path('task/', views.run_celery_task, name='new_task'),
    path('task/<slug:task_id>/', views.get_task_status, name='check_status'),


    path('posts/<int:post_id>/',
         views.post_detail,
         name='post_detail'),
    path('posts/create/', views.post, name='create_post'),
    path('posts/<int:post_id>/edit/', views.post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/comment/', views.comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.comment, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.delete_comment, name='delete_comment'),

    path('category/<slug:category_slug>/',
         views.category_posts,
         name='category_posts'
         ),

    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<slug:author>/', views.author_profile, name='profile'),

    path('auth/logout/', views.custom_logout, name='logout'),
]
