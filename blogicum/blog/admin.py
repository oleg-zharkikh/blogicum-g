from django.contrib import admin
from django.utils.html import format_html

import core.blog_settings

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не задано'


class CommentsInLine(admin.StackedInline):
    model = Comment
    fields = ['text']
    extra = 0


class PostsInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostsInline,
    )
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
    )
    list_editable = (
        'description',
        'slug',
        'is_published',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostsInline,
    )
    list_display = (
        'name',
        'is_published',
    )
    list_editable = (
        'is_published',
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    def short_text(self, post_object):
        """Формирует короткую строку для отображения поля text."""
        max_length = core.blog_settings.MAX_VIEWED_LENGTH
        if len(post_object.text) > max_length:
            return f'{post_object.text[:max_length]} ...'
        return post_object.text

    def title_colored(self, post_object):
        """Окрашивает заголовки неопубликованных постов серым."""
        if post_object.is_published:
            color_of_text = '#000000'
        else:
            color_of_text = '#505050'
        return format_html(
            '<span style="color: {};">{}</span>',
            color_of_text,
            post_object.title
        )
    inlines = (
        CommentsInLine,
    )
    list_display = (
        'title_colored',
        'short_text',
        'author',
        'pub_date',
        'location',
        'category',
        'is_published'
    )
    list_editable = (
        'pub_date',
        'is_published',
        'location',
        'category'
    )

    search_fields = ('title_colored',)
    list_filter = ('is_published',)
    list_display_links = ('title_colored',)
    title_colored.short_description = 'Заголовок'
    short_text.short_description = 'Текст'
