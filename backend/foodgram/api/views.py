import csv
import short_url
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from .serializers import (AvatarSerializer, IngredientSerializer,
                          FavoriteSerializer, FollowSerializer,
                          RecipeSerializer, ReadRecipeIngredientSerializer,
                          RecipeGETSerializer, ShoppingCartSerializer,
                          TagSerializer)
from recipes.models import (Ingredient, Favorite, Follow,
                            Recipe, RecipeIngredient,
                            ShoppingCart, Tag, URL)
from .permissions import IsAuthorOrReadOnly
from .pagination import UserRecipePagination
from .filters import IngredientSearchFilter, RecipeFilter
from core.utils import create_delete_object

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    """ ViewSet для модели Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = UserRecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Функция для выбора сериализатора."""
        if self.action in ('list', 'retrieve'):
            return RecipeGETSerializer
        return RecipeSerializer

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, *args, **kwargs):
        """
        Добавление/удаление рецепта из избранного.

        Предоставляет возможность текущему пользователю добавить рецепт в
        избранное и удалить рецепт из избранного.
        """
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return create_delete_object(FavoriteSerializer, request, recipe,
                                    Favorite, 'избранного')

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        """
        Добавление/удаление рецепта из списка покупок.

        Предоставляет возможность текущему пользователю добавить рецепт в
        список покупок и удалить рецепт из списка покупок.
        """
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return create_delete_object(ShoppingCartSerializer, request, recipe,
                                    ShoppingCart, 'списка покупок')

    @action(methods=['get'], detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание списка покупок текущим пользователем."""
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=user
        )
        serializer = ReadRecipeIngredientSerializer(
            ingredients,
            context={'request': request},
            many=True
        )
        dictionary = {}
        for data in serializer.data:
            if data['name'] not in dictionary:
                dictionary[data['name']] = [
                    data['amount'], data['measurement_unit']
                ]
            else:
                dictionary[data['name']][0] += data['amount']
        fields = ['Ингредиент', 'Единица измерения', 'Количество']
        my_data = []
        for key, value in dictionary.items():
            my_data.append([key, value[1], value[0]])
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="shoppingcart.csv"'
        writer = csv.writer(response)
        writer.writerow(fields)
        writer.writerows(my_data)
        return response

    @action(methods=['get'], detail=True, url_path='get-link')
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


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def redirect_view(request, hash):
    """Редирект с короткой ссылки рецепта на обычную."""
    obj = get_object_or_404(URL, hash=hash)
    return redirect(obj.url)


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


class CustomUserViewSet(UserViewSet):
    """ ViewSet для модели User."""

    pagination_class = UserRecipePagination

    @action(methods=['get'], detail=False, url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        """Получение данных о текущем пользователе."""
        return super().me(request, *args, **kwargs)

    @action(methods=['put', 'delete'], detail=False, url_path='me/avatar')
    def avatar(self, request):
        """
        Добавление/удаление аватара.

        Предоставляет возможность текущему пользователю добавить в профиль
        аватар и удалить его.
        """
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data, instance=user,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        """
        Подписка/отписка.

        Предоставляет возможность текущему пользователю подписаться
        на/отписаться от выбранного пользователя.
        """
        user = request.user
        following = get_object_or_404(User, id=self.kwargs['id'])
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=request.data,
                context={'request': request, 'following': following}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(following=following, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if Follow.objects.filter(following=following, user=user).exists():
                Follow.objects.get(following=following, user=user).delete()
                return Response('Успешная отписка',
                                status=status.HTTP_204_NO_CONTENT)
            return Response('Ошибка отписки',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        """
        Список подписок.

        Предоставляет возможность текущему пользователю получить
        список своих подписок.
        """
        user = request.user
        followings = Follow.objects.filter(user=user)
        page = self.paginate_queryset(followings)
        serializer = FollowSerializer(page,
                                      context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)
