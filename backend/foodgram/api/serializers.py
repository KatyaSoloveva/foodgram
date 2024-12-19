import re

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredient, Favorite, Recipe,
                            RecipeIngredient, Tag, ShoppingCart)
from users.models import Follow, User
from core.services import (get_fields, validate_count, validate_fields,
                           validate_shopping_favorite, recipe_create_update)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class UserPOSTSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')

    def validate_username(self, value):
        """Валидация поля username."""
        pattern = re.compile(r'^[\w.@+-]+$')
        if not pattern.match(value):
            raise serializers.ValidationError(
                'Поле username содержит недопустимые символы'
            )
        return value

    def validate_email(self, value):
        """Валидация поля email."""
        if User.objects.filter(email=value):
            raise serializers.ValidationError(
                'Пользователь с таким emil уже существует'
            )
        return value


class UserGETSerializer(UserSerializer):
    """
    Сериализатор для модели пользователя.
    """

    avatar = Base64ImageField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        """Получение значения для поля is_subscribed."""
        request = self.context['request']
        user = request.user
        return (request and user.is_authenticated
                and user.followings.filter(author=obj).exists())


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для поля avatar модели пользоваетля."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Вспомогательный сериализатор.

    Позволяет получить данные об ингредиентах.
    Используется в RecipeGETSerializer.
    """

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class WriteRecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Вспомогательный сериализатор.

    Служит для добавления ингредиентов в рецепт.
    Используется в RecipeSerializer.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient.id')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        """Валидация поля amount."""
        return validate_count(value, 'Количество')


class RecipeGETSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения информации о рецептах.
    """

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
        """Получение значения поля is_favorited."""
        return get_fields(self.context, Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        """Получение значения поля is_in_shopping_cart."""
        return get_fields(self.context, ShoppingCart, obj)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и обновления рецепта"""

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
        """Создание рецепта."""
        ingredients_data = validated_data.pop('recipesingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        recipe_create_update(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Изменение реуепта."""
        if 'recipesingredients' not in validated_data:
            raise serializers.ValidationError(
                'Нельзя обновить рецепт без поля ingredients!'
            )
        ingredients_data = validated_data.pop('recipesingredients')
        instance.ingredients.clear()
        recipe_create_update(ingredients_data, instance)
        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                'Нельзя обновить рецепт без поля tags!'
            )
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Предоставление данных о рецепте.

        При создании/обновлении рецепта данные предоставляются
        в полном виде.
        """
        return RecipeGETSerializer(instance, context=self.context).data

    def validate_cooking_time(self, value):
        """Валидация поля cooking_time."""
        return validate_count(value, 'Время готовки')

    def validate_ingredients(self, value):
        """Валидация поля ingredients."""
        return validate_fields(value, 'ингредиентов', 'ингредиенты',
                               'ingredient', 'id')

    def validate_tags(self, value):
        """Валидация поля tags."""
        return validate_fields(value, 'тегов', 'теги')

    def validate_image(self, value):
        "Валидация поля image."
        if not value:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без изображения.'
            )
        return value


class PartialRecipeSerializer(serializers.ModelSerializer):
    """
    Вспомогательный сериализатор.

    Используется для получения
    частичной информации о рецепте.
    Используется в FollowSerializer.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    avatar = Base64ImageField(source='author.avatar',
                              read_only=True)
    recipes = PartialRecipeSerializer(many=True, read_only=True,
                                      source='author.recipes')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        """Получение значения для поля is_subscribed."""
        return True

    def get_recipes_count(self, obj):
        """Получение значения для поля recipes_count."""
        return obj.author.recipes.count()

    def validate(self, data):
        """
        Валидация полей user-author.

        Запрет на повторную подписку на
        одного и того же пользователя и подписку на себя.
        """
        user = self.context['request'].user
        author = self.context['author']
        if user == author:
            raise serializers.ValidationError(
                'Нельзя оформить подписку на самого себя!')
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя!')
        return data

    def to_representation(self, instance):
        """
        Предоставление данных о подписках.

        Возможность получать данные о подписках с учетом
        установления параметра recipes_limit.
        """
        ret = super().to_representation(instance)
        if 'recipes_limit' in self.context['request'].query_params:
            recipes_count = int(
                self.context['request'].query_params['recipes_limit']
            )
            ret['recipes'] = ret['recipes'][:recipes_count]
        return ret


class ShoppingFavoriteMixin(serializers.ModelSerializer):
    """Миксин для полей id, name, image. cooking_time."""

    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')


class FavoriteSerializer(ShoppingFavoriteMixin, serializers.ModelSerializer):
    """Сериализатор для модели Favorite."""

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        """
        Валидация полей recipe-user.

        Невозможность повторно добавить рецепт
        в избранное.
        """
        return validate_shopping_favorite(data, self.context, Favorite,
                                          'избранном')


class ShoppingCartSerializer(ShoppingFavoriteMixin,
                             serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCart."""

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        """
        Валидация полей recipe-user.

        Невозможность повторно
        добавить рецепт в список покупок.
        """
        return validate_shopping_favorite(data, self.context, ShoppingCart,
                                          'списке покупок')
