from django.db import models
from django.contrib.auth import get_user_model
# from django.utils.text import slugify

# from unidecode import unidecode

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

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(unidecode(self.name))
    #     super().save(*args, **kwargs)


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
    # image = 
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингредиенты')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='recipesingredients')
    ingredient = models.ForeignKey(Ingredient, verbose_name='Ингредиент',
                                   on_delete=models.CASCADE,
                                   related_name='recipesingredients')
    amount = models.SmallIntegerField(verbose_name='Kоличество')
