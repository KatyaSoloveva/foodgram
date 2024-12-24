import short_url
from django.db.models import Sum, Count, F
from django.http import FileResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from .serializers import (AvatarSerializer, IngredientSerializer,
                          FavoriteSerializer, FollowWriteSerializer,
                          FollowReadSerializer,
                          RecipeSerializer, RecipeGETSerializer,
                          ShoppingCartSerializer, TagSerializer)
from .permissions import IsAuthorOrReadOnly
from .pagination import UserRecipePagination
from .filters import IngredientSearchFilter, RecipeFilter
from recipes.models import (Ingredient, Favorite,
                            Recipe, RecipeIngredient,
                            ShoppingCart, Tag, URL)
from users.models import Follow, User
from core.services import delete_favorite_shopping, get_data


class RecipeViewSet(viewsets.ModelViewSet):
    """ ViewSet для модели Recipe."""

    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = UserRecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.with_relation()
        if user.is_authenticated:
            queryset = Recipe.objects.with_annotation(user)
        return queryset

    def get_serializer_class(self):
        """Функция для выбора сериализатора."""
        if self.action in ('list', 'retrieve'):
            return RecipeGETSerializer
        return RecipeSerializer

    @staticmethod
    def add_favorite_or_cart(serializer, pk, request):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer(data=request.data,
                                context={'request': request, 'recipe': recipe})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=('post',), detail=True)
    def favorite(self, request, *args, **kwargs):
        """
        Добавление рецепта в избранное.

        Предоставляет возможность текущему пользователю добавить рецепт в
        избранное.
        """
        return self.add_favorite_or_cart(FavoriteSerializer,
                                         self.kwargs['pk'], request)

    @favorite.mapping.delete
    def delete_favorite(self, request, *args, **kwargs):
        """
        Удаление рецепта из избранного.

        Предоставляет возможность текущему пользователю
        удалить рецепт из избранного.
        """
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return delete_favorite_shopping(request.user, recipe, Favorite,
                                        'избранного')

    @action(methods=('post',), detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        """
        Добавление рецепта в список покупок.

        Предоставляет возможность текущему пользователю добавить рецепт в
        список покупок.
        """
        return self.add_favorite_or_cart(ShoppingCartSerializer,
                                         self.kwargs['pk'], request)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, *args, **kwargs):
        """
        Удаление рецепта из списка покупок.

        Предоставляет возможность текущему пользователю
        удалить рецепт из списка покупок.
        """
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return delete_favorite_shopping(request.user, recipe, ShoppingCart,
                                        'списка покупок')

    @action(methods=('get',), detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание списка покупок текущим пользователем."""
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=user
        ).values(name=F('ingredient__name'),
                 measurement_unit=F('ingredient__measurement_unit')).annotate(
                     amount=Sum('amount')).order_by('ingredient__name')
        print(ingredients)
        my_data = get_data(ingredients)
        response = FileResponse(my_data, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shoppingcart.txt"'
        )
        return response

    @action(methods=('get',), detail=True, url_path='get-link')
    def getlink(self, request, pk=None):
        """
        Получение короткой ссылки.

        Предоставляет возможность текущему пользователю получить короткую
        ссылку на выбранный рецепт.
        """
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        url = request.headers.get('Referer')
        if not url:
            url = request.build_absolute_uri(reverse('recipes-detail',
                                                     args=(recipe.pk,)))
        if URL.objects.filter(url=url).exists():
            hash = URL.objects.get(url=url).hash
        else:
            hash = short_url.encode_url(recipe.pk)
            URL.objects.create(hash=hash, url=url)
        short = request.build_absolute_uri(reverse('get_url', args=(hash,)))
        return Response({'short-link': short})


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ ViewSet для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ ViewSet для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class UserViewSet(UserViewSet):
    """ ViewSet для модели User."""

    pagination_class = UserRecipePagination

    @action(methods=('get',), detail=False, url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        """Получение данных о текущем пользователе."""
        return super().me(request, *args, **kwargs)

    @action(methods=('put',), detail=False, url_path='me/avatar')
    def avatar(self, request):
        """
        Добавление аватара.

        Предоставляет возможность текущему пользователю добавить в профиль
        аватар.
        """
        user = request.user
        serializer = AvatarSerializer(data=request.data, instance=user,
                                      context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """
        Удаление аватара.

        Предоставляет возможность текущему пользователю удалить
        аватар из профиля.
        """
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('post',), detail=True)
    def subscribe(self, request, *args, **kwargs):
        """
        Подписка.

        Предоставляет возможность текущему пользователю подписаться
        на выбранного пользователя.
        """
        user = request.user
        author = get_object_or_404(User.objects.annotate(
            recipes_count=Count('recipes')
        ).order_by('username'), id=self.kwargs['id'])
        serializer = FollowWriteSerializer(
            data=request.data,
            context={'request': request, 'author': author})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=author, user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, *args, **kwargs):
        """
        Отписка.

        Предоставляет возможность текущему пользователю
        отписаться от выбранного пользователя.
        """
        user = request.user
        author = get_object_or_404(User, id=self.kwargs['id'])
        delete, _ = Follow.objects.filter(author=author, user=user).delete()
        return Response(
            'Успешная отписка' if delete != 0 else 'Ошибка отписки',
            status=status.HTTP_204_NO_CONTENT if delete != 0
            else status.HTTP_400_BAD_REQUEST
        )

    @action(methods=('get',), detail=False)
    def subscriptions(self, request):
        """
        Список подписок.

        Предоставляет возможность текущему пользователю получить
        список своих подписок.
        """
        user = request.user
        authors = User.objects.filter(
            subscriptions_to_author__user=user
        ).annotate(recipes_count=Count('recipes')
                   ).order_by('username')
        page = self.paginate_queryset(authors)
        serializer = FollowReadSerializer(page,
                                          context={'request': request},
                                          many=True)
        return self.get_paginated_response(serializer.data)
