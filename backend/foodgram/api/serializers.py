import base64
import re

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer

from recipes.models import (Ingredient, Favorite, Follow, Recipe,
                            RecipeIngredient, Tag, ShoppingCart)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class UserPOSTSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')

    def validate_username(self, value):
        pattern = re.compile(r'^[\w.@+-]+$')
        if not pattern.match(value):
            raise serializers.ValidationError(
                'Поле username содержит недопустимые символы'
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value):
            raise serializers.ValidationError(
                'Пользователь с таким emil уже существует'
            )
        return value


class UserGETSerializer(UserSerializer):
    avatar = Base64ImageField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            following=obj, user=self.context['request'].user
        ).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class WriteRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient.id')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGETSerializer(serializers.ModelSerializer):
    author = UserGETSerializer(read_only=True)
    ingredients = ReadRecipeIngredientSerializer(source='recipesingredients',
                                                 many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            author=obj.author, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(
            recipe=obj, user=obj.author
        ).exists()


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = WriteRecipeIngredientSerializer(source='recipesingredients',
                                                  many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipesingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for current_ingredient in ingredients_data:
            ingredient = Ingredient.objects.get(
                name=current_ingredient['ingredient']['id']
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=current_ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        if 'recipesingredients' in validated_data:
            ingredients_data = validated_data.pop('recipesingredients')
            for current_ingredient in ingredients_data:
                ingredient = Ingredient.objects.get(
                    name=current_ingredient['ingredient']['id']
                )
                RecipeIngredient.objects.update(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=current_ingredient['amount']
                )
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)

        instance.save()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeGETSerializer(instance, context=self.context)
        return serializer.data


class PartialRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    avatar = Base64ImageField(source='following.avatar',
                              read_only=True)
    recipes = PartialRecipeSerializer(many=True, read_only=True,
                                      source='following.recipes')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.following.recipes.count()

    def validate(self, data):
        user = self.context['request'].user
        following = self.context['following']
        if user == following:
            raise serializers.ValidationError(
                'Нельзя оформить подписку на самого себя!')
        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя!')
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        recipe = self.context['recipe']
        author = recipe.author
        if Favorite.objects.filter(author=author, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже есть в избранном!')
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context['request'].user
        recipe = self.context['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже есть в списке покупок!'
            )
        return data
