import short_url
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from djoser.views import UserViewSet

from .serializers import (AvatarSerializer, IngredientSerializer,
                          FavoriteSerializer, FollowSerializer,
                          RecipeGETSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)
from recipes.models import (Ingredient, Favorite, Follow, Recipe,
                            ShoppingCart, Tag)


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipeSerializer

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        author = recipe.author
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data=request.data,
                context={'request': request, 'recipe': recipe}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, recipe=recipe)
            return Response(serializer.data)
        else:
            if Favorite.objects.filter(author=author, recipe=recipe).exists():
                Favorite.objects.get(author=author).delete()
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
            return Response(serializer.data)
        else:
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                ShoppingCart.objects.get(user=user).delete()
                return Response('Рецепт успешно удален из списка покупок',
                                status=status.HTTP_204_NO_CONTENT)
            return Response('Ошибка удаления из списка покупок',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True, url_path='get-link')
    def getlink(self, request, pk=None):
        recipe = Recipe.objects.get(pk=pk)
        return Response({'short-link': short_url.encode_url(recipe.pk)})


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class CustomUserViewSet(UserViewSet):

    @action(methods=['put', 'delete'], detail=False, url_path='me/avatar')
    def avatar(self, request):
        instance = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data, instance=instance,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            instance.avatar = None
            instance.save()
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
            serializer.save(user=user, following=following)
            return Response(serializer.data)
        else:
            if Follow.objects.filter(user=user, following=following).exists():
                Follow.objects.get(user=user).delete()
                return Response('Успешная отписка',
                                status=status.HTTP_204_NO_CONTENT)
            return Response('Ошибка отписки',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = request.user
        followings = Follow.objects.filter(user=user)
        count = followings.count()
        serializer = FollowSerializer(followings,
                                      context={'request': request}, many=True)
        print(serializer.data)
        return Response({'count': count, 'results': serializer.data})
