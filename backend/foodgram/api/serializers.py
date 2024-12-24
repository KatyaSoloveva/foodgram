from rest_framework import serializers
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredient, Favorite, Recipe,
                            RecipeIngredient, Tag, ShoppingCart)
from users.models import Follow, User
from core.services import recipe_create_update
from core.validators import validate_fields
from core.constants import MIN_COUNT, MAX_COUNT


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


class UserSerializer(UserSerializer):
    """Сериализатор для модели пользователя."""

    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        """Получение значения для поля is_subscribed."""
        request = self.context['request']
        user = request.user
        return (request and user.is_authenticated
                and user.user_subscriptions.filter(
                    author=obj
                ).exists())


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

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_COUNT,
        max_value=MAX_COUNT,
        error_messages={
            'min_value':
            f'Значение поля amount не должно быть меньше {MIN_COUNT}',
            'max_value':
            f'Значение поля amount не должно быть больше {MAX_COUNT}'}
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о рецептах."""

    author = UserSerializer(read_only=True)
    ingredients = ReadRecipeIngredientSerializer(source='recipesingredients',
                                                 many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(read_only=True)
    is_favorited = serializers.BooleanField(default=False,
                                            read_only=True)
    is_in_shopping_cart = serializers.BooleanField(default=False,
                                                   read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и обновления рецепта"""

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = WriteRecipeIngredientSerializer(source='recipesingredients',
                                                  many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_COUNT,
        max_value=MAX_COUNT,
        error_messages={
            'min_value':
            f'Значение поля cooking_time не должно быть меньше {MIN_COUNT}',
            'max_value':
            f'Значение поля cooking_time не должно быть больше {MAX_COUNT}'}
    )

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
        """Изменение рецепта."""
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

    def validate_ingredients(self, value):
        """Валидация поля ingredients."""
        return validate_fields(value, 'ингредиентов', 'ингредиенты', 'id')

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
    Используется в FollowSerializer и ShoppingFavoriteMixin.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        model = Follow
        fields = '__all__'
        read_only_fields = ('user', 'author')

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
        """Получение данных о подписке."""
        return FollowReadSerializer(instance=instance.author,
                                    context=self.context).data


class FollowReadSerializer(UserSerializer):
    """Сериализатор для получения информации о подписках."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(default=0)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        "Получение рецептов автора."
        recipes = obj.recipes.all()
        request = self.context['request']
        if 'recipes_limit' in request.query_params:
            try:
                recipes_limit = int(
                    request.query_params['recipes_limit']
                )
                recipes = recipes[:recipes_limit]
            except ValueError:
                raise serializers.ValidationError(
                    'Пармаетр recipes_limit не является числом.'
                )
        return PartialRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data


class ShoppingFavoriteSerializer(serializers.ModelSerializer):
    """Класс-родитель для FavoriteSerializer и ShoppingCartSerializer."""

    def validate(self, data):
        """
        Валидация полей recipe-user.

        Невозможность повторно добавить рецепт в список
        покупок или избранное.
        """
        user = self.context['request'].user
        recipe = self.context['recipe']
        model = self.Meta.model
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт уже есть в {model._meta.verbose_name}!'
            )
        return data

    def to_representation(self, instance):
        """Предоставление данных о рецептах в избранном/списке покупок."""
        return PartialRecipeSerializer(instance=instance.recipe,
                                       context=self.context).data


class FavoriteSerializer(ShoppingFavoriteSerializer):
    """Сериализатор для модели Favorite."""

    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('user', 'recipe')


class ShoppingCartSerializer(ShoppingFavoriteSerializer):
    """Сериализатор для модели ShoppingCart."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        read_only_fields = ('user', 'recipe')
