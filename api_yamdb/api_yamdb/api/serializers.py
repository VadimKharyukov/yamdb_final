from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from reviews.models import CustomUser
from reviews.models import Review, Comment, Title, Category, Genre


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(slug_field='name', read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('author', 'id')

    def validate(self, data):
        request = self.context.get('request')
        if request.method != 'POST':
            return data
        title = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=request.user, title=title).exists():
            raise serializers.ValidationError(
                'Больше одного обзора написать нельзя'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('author', 'id', 'review')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id', )
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=('name', 'slug'),
                message='Такая категория уже существует'
            )
        ]


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id', )
        validators = [
            UniqueTogetherValidator(
                queryset=Genre.objects.all(),
                fields=('name', 'slug'),
                message='Такой жанр уже существует'
            )
        ]


class TitleSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,
                                   validators=[UniqueValidator(
                                       queryset=CustomUser.objects.all())])
    username = serializers.CharField(required=True,
                                     validators=[UniqueValidator(
                                         queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = ('email', 'username')

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Недоступное имя пользователя!введите другое'
            )
        return username


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'confirmation_code')


class AdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True,
                                     validators=[UniqueValidator(
                                         queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = ('username', 'last_name', 'first_name', 'email',
                  'role', 'bio')


class UserSerializer(AdminSerializer):
    role = serializers.CharField(read_only=True)
