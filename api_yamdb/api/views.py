from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import CharFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import status, viewsets, filters, mixins
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, CustomUser, Review, Title
from .permissions import (IsAdmin,
                          IsAdminOrReadOnly,
                          IsOwnerOrAdminOrModeratorOrReadOnly)
from .serializers import (
    TitleSerializer,
    TitleListSerializer,
    CategorySerializer,
    GenreSerializer,
    SignupSerializer,
    AdminSerializer,
    TokenSerializer,
    UserSerializer,
    ReviewSerializer,
    CommentSerializer,
)


@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    username = serializer.data.get('username')
    user, create = CustomUser.objects.get_or_create(email=email,
                                                    username=username)
    confirmation_code = default_token_generator.make_token(user)
    send_mail('Вам отправлен код авторизации',
              f'Ваш код {confirmation_code}',
              settings.DEFAULT_FROM_EMAIL,
              [email],
              )
    return Response({'email': email, 'username': username})


@api_view(['POST'])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.data.get('username')
    confirmation_code = serializer.data.get('confirmation_code')
    user = get_object_or_404(CustomUser, username=username)
    if default_token_generator.check_token(user, confirmation_code):
        user.is_active = True
        user.save()
        token_user = AccessToken.for_user(user)
        return Response({'Ваш токен':
                        f'{token_user}'},
                        status=status.HTTP_200_OK)
    return Response({'Вы ввели неправильный код':
                    f'{confirmation_code}'},
                    status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = AdminSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (IsAdmin, )
    filter_backends = (filters.SearchFilter, )
    lookup_field = 'username'
    search_fields = ('username',)

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateListDestroyModelViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    pass


class TitleFilterSet(FilterSet):
    genre = CharFilter(field_name='genre__slug', lookup_expr='icontains')
    category = CharFilter(field_name='category__slug', lookup_expr='icontains')
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'name', 'year')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilterSet
    filterset_fields = ('slug', )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleListSerializer
        return TitleSerializer


class CategoryViewSet(CreateListDestroyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(CreateListDestroyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    permission_classes = (IsAdminOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrAdminOrModeratorOrReadOnly, )

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrAdminOrModeratorOrReadOnly, )

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
