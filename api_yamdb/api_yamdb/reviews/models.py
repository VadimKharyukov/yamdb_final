from django.contrib.auth.models import AbstractUser
from django.core.validators import (ValidationError,
                                    MaxValueValidator,
                                    MinValueValidator
                                    )
from django.db import models
from django.utils import timezone


class UserRoles:
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    choices = (
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN),
    )


class CustomUser(AbstractUser):
    username = models.CharField(verbose_name='Имя пользователя',
                                unique=True,
                                max_length=150)
    email = models.EmailField(verbose_name='Почтовый ящик',
                              unique=True,
                              max_length=254)
    bio = models.TextField(verbose_name='Биография', blank=True)
    role = models.CharField(verbose_name='Статус',
                            choices=UserRoles.choices,
                            max_length=30,
                            default=UserRoles.USER)
    confirmation_code = models.CharField(max_length=30)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = ''


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=50,
                            unique=True,
                            verbose_name='Идентификатор'
                            )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Идентификатор')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


def year_validator(value):
    if value > timezone.now().year:
        raise ValidationError('Год не может быть больше текущего')


class Title(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    year = models.IntegerField(
        verbose_name='Год публикации',
        validators=[
            year_validator
        ]
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles',
        blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, through='GenreTitle')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        null=True,
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'genre'),
                name='unique_genre_title'
            )
        ]

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews', null=True
    )
    text = models.TextField(max_length=3000)
    score = models.IntegerField(default=1, validators=[
        MaxValueValidator(10),
        MinValueValidator(1)])
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date', )
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'), name='unique_title_review'
            )
        ]


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date', )


class Score(models.Model):
    SCORE_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10),
    )

    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='scores')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
