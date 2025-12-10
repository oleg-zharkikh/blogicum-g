from rest_framework import serializers

from .models import Post, Category, Location, Comment


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'title', 'text', 'author', 'location', 'category')
