from django.shortcuts import get_object_or_404
from posts.models import Follow, Group, Post, User
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .customviewset import CreateRetrieveViewSet
from .permissions import UserIsAuthorOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class PostViewSet(viewsets.ModelViewSet):
    """GET, POST): получаем список всех постов или создаём новый пост.
    (GET, PUT, PATCH, DELETE):получаем, редактируем или удаляем пост по id."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        UserIsAuthorOrReadOnly,
    ]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        """POST - пост записи."""
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """(GET): получаем список всех групп.
    (GET): получаем информацию о группе по id."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """(GET, POST): получаем список всех комментариев поста с id=post_id.
    Или создаём новый, указав id поста, который хотим прокомментировать.
    (GET, PUT, PATCH, DELETE): получаем, редактируем или удаляем
    комментарий по id у поста с id=post_id."""
    serializer_class = CommentSerializer
    permission_classes = [
        UserIsAuthorOrReadOnly,
    ]

    def get_queryset(self):
        """GET - получаем список комментариев поста или создаём новый."""
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return post.comments

    def perform_create(self, serializer):
        """GET, PUT, PATCH - автор получает или редактирует по id."""
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(post=post, author=self.request.user)


class FollowViewSet(CreateRetrieveViewSet):
    """GET, POST - возвращает все подписки пользователя, сделавшего запрос.
    Анонимные запросы запрещены."""
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ('following__username',)

    def get_queryset(self):
        """Фильтрация подписок по user"""
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """GET, POST - возвращает все подписки пользователя."""
        following = User.objects.get(
            username=self.request.data['following']
        )
        serializer.save(user=self.request.user, following=following)
