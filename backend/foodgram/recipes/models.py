from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=255,
                            verbose_name='Название тега')
    slug = models.SlugField(max_length=255, unique=True,
                            verbose_name='URL')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=2,
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
    name = models.CharField(max_length=255,
                            verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(upload_to='recipes/images/',
                              verbose_name='Картинка')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
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
    amount = models.IntegerField(verbose_name='Kоличество')

    class Meta:
        verbose_name = 'Рецепт-Ингредиент'
        verbose_name_plural = 'Рецептыы-Ингредиенты'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Пользователь',
                               related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Избранное',
                               related_name='favorites')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='subscriber')
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  verbose_name='Подписка',
                                  related_name='subscription')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]
