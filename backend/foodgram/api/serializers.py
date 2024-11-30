from rest_framework import serializers

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


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


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = WriteRecipeIngredientSerializer(source='recipesingredients',
                                                  many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'ingredients', 'tags',
                  'cooking_time', 'text', 'image')

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


class RecipeGETSerializer(serializers.ModelSerializer):
    ingredients = ReadRecipeIngredientSerializer(source='recipesingredients',
                                                 many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = serializers.ImageField(required=False, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')
