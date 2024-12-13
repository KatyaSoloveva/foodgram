from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from core.constants import MAX_LENGTH, MIN_COUNT

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=MAX_LENGTH,
                            verbose_name='Название тега')
    slug = models.SlugField(max_length=MAX_LENGTH, unique=True,
                            verbose_name='URL')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=MAX_LENGTH,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=MAX_LENGTH,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


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
        validators=[MinValueValidator(MIN_COUNT)]
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингредиенты')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='recipesingredients')
    ingredient = models.ForeignKey(Ingredient, verbose_name='Ингредиент',
                                   on_delete=models.CASCADE,
                                   related_name='recipesingredients')
    amount = models.IntegerField(verbose_name='Kоличество',
                                 validators=[MinValueValidator(MIN_COUNT)])

    class Meta:
        verbose_name = 'Рецепт-Ингредиент'
        verbose_name_plural = 'Рецептыы-Ингредиенты'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Избранное',
                               related_name='favorites')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_user'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='subscriber')
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  verbose_name='Подписка',
                                  related_name='subscription')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.following}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='shoppingcarts')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='shoppingcarts')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

        def __str__(self):
            return f'{self.user} {self.recipe}'


class URL(models.Model):
    hash = models.CharField(max_length=MAX_LENGTH, unique=True,
                            verbose_name='Хэш')
    url = models.URLField(verbose_name='URL')

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'
        constraints = [
            models.UniqueConstraint(
                fields=['hash', 'url'],
                name='unique_hash_url'
            )
        ]

    def __str__(self):
        return self.hash
