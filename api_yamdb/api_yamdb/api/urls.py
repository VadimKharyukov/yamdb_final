from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ReviewViewSet,
                    CommentViewSet,
                    TitleViewSet,
                    CategoryViewSet,
                    GenreViewSet,
                    CustomUserViewSet,
                    signup,
                    token)

router = DefaultRouter()
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/'
                r'(?P<review_id>\d+)/comments',
                CommentViewSet, basename='comments')
router.register('titles', TitleViewSet)
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', signup),
    path('v1/auth/token/', token),
]
