import csv
import short_url
from django.shortcuts import redirect
from django.http import HttpResponse
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
from .permissions import IsAdminIsAuthorOrReadOnly
from .pagination import UserRecipePagination
from .filters import IngredientSearchFilter

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminIsAuthorOrReadOnly,)
    pagination_class = UserRecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags__slug')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGETSerializer
        return RecipeSerializer

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        author = request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data=request.data,
                context={'request': request, 'recipe': recipe}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if Favorite.objects.filter(author=author, recipe=recipe).exists():
                Favorite.objects.get(author=author, recipe=recipe).delete()
                return Response('Рецепт успешно удален из избранного',
                                status=status.HTTP_204_NO_CONTENT)
            return Response('Ошибка удаления из избранного',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data=request.data,
                context={'request': request, 'recipe': recipe})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                ShoppingCart.objects.get(user=user, recipe=recipe).delete()
                return Response('Рецепт успешно удален из списка покупок',
                                status=status.HTTP_204_NO_CONTENT)
            return Response('Ошибка удаления из списка покупок',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
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
        try:
            recipe = Recipe.objects.get(pk=pk)
            host = request.META['HTTP_HOST']
            protocol = request.META['wsgi.url_scheme']
            main_url = '/'.join(request.META['PATH_INFO'].split('/')[1:-2])
            url = f'{protocol}://{host}/{main_url}'
            if URL.objects.filter(url=url).exists():
                hash = URL.objects.get(url=url).hash
            else:
                hash = short_url.encode_url(recipe.pk)
                URL.objects.create(hash=hash, url=url)
            short = f'{protocol}://{host}/s/{hash}'
            return Response({'short-link': short})
        except Recipe.DoesNotExist:
            return Response('Рецепт не найден',
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def redirect_view(request, hash):
    try:
        url = URL.objects.get(hash=hash)
        return redirect(url.url)
    except URL.DoesNotExist:
        return Response('Данная короткая ссылка не существует',
                        status=status.HTTP_404_NOT_FOUND)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class CustomUserViewSet(UserViewSet):
    pagination_class = UserRecipePagination

    @action(methods=['get'], detail=False, url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(methods=['put', 'delete'], detail=False, url_path='me/avatar')
    def avatar(self, request):
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
        user = request.user
        followings = Follow.objects.filter(user=user)
        page = self.paginate_queryset(followings)
        serializer = FollowSerializer(page,
                                      context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)
