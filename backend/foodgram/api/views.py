import short_url
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from djoser.views import UserViewSet

from .serializers import (AvatarSerializer, IngredientSerializer,
                          RecipeGETSerializer, RecipeSerializer, TagSerializer)
from recipes.models import Ingredient, Recipe, Tag


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipeSerializer

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

    @action(methods=['put'], detail=False, url_path='me/avatar')
    def put_avatar(self, request):
        instance = request.user
        serializer = AvatarSerializer(data=request.data, instance=instance,
                                      context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['delete'], detail=False, url_path='me/avatar')
    def delete_avatar(self, request):
        instance = request.user
        instance.avatar = None
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
