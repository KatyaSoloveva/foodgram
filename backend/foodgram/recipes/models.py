from django.db import models
from django.db.models import Subquery, OuterRef, Exists
from django.core.validators import MinValueValidator, MaxValueValidator

from core.constants import (LENGTH, LENGTH_MEASUREMENT_UNIT, MAX_LENGTH,
                            MAX_INGREDIENT_LENGTH, MAX_TAG_LENGTH,
                            MAX_COUNT, MIN_COUNT)
from users.models import User


class RecipeManager(models.Manager):
    def with_relation(self):
        return self.select_related('author').prefetch_related(
            'ingredients', 'tags')

    def with_annotation(self, user):
        return self.with_relation().annotate(
            is_favorited=Exists(Subquery(Favorite.objects.filter(
                recipe_id=OuterRef('pk'), user=user))),
            is_in_shopping_cart=Exists(Subquery(
                ShoppingCart.objects.filter(
                    recipe_id=OuterRef('pk'), user=user
                )))
        ).order_by('-pub_date')


class Tag(models.Model):
    name = models.CharField(max_length=MAX_TAG_LENGTH,
                            verbose_name='Название тега')
    slug = models.SlugField(max_length=MAX_TAG_LENGTH, unique=True,
                            verbose_name='URL')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:LENGTH]


class Ingredient(models.Model):
    name = models.CharField(max_length=MAX_INGREDIENT_LENGTH,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=LENGTH_MEASUREMENT_UNIT,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            ),
        )

    def __str__(self):
        return self.name[:LENGTH]


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               verbose_name='Автор рецепта',
                               related_name='recipes',
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=MAX_LENGTH,
                            verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Картинка')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(MIN_COUNT), MaxValueValidator(MAX_COUNT))
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингредиенты')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    objects = RecipeManager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:LENGTH]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='recipesingredients')
    ingredient = models.ForeignKey(Ingredient, verbose_name='Ингредиент',
                                   on_delete=models.CASCADE,
                                   related_name='recipesingredients')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Kоличество',
        validators=(MinValueValidator(MIN_COUNT),
                    MaxValueValidator(MAX_COUNT))
    )

    class Meta:
        verbose_name = 'Рецепт-Ингредиент'
        verbose_name_plural = 'Рецепты-Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class FavoriteShopping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s_recipe_user'
            ),
        )

    def __str__(self):
        return (f'{self._meta.verbose_name}: {self.user} - '
                f'{self.recipe}')


class Favorite(FavoriteShopping):

    class Meta(FavoriteShopping.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'


class ShoppingCart(FavoriteShopping):

    class Meta(FavoriteShopping.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shoppingcarts'


class URL(models.Model):
    hash = models.SlugField(max_length=MAX_LENGTH, unique=True,
                            verbose_name='Хэш')
    url = models.URLField(verbose_name='URL')

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'
        constraints = (
            models.UniqueConstraint(
                fields=('hash', 'url'),
                name='unique_hash_url'
            ),
        )

    def __str__(self):
        return self.hash[:LENGTH]
