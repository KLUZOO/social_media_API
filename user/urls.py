from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from user.views import (
    CreateUserView,
    ManageUserView,
    UsersListView,
    FollowUserView,
)

router = routers.DefaultRouter()
router.register("users", UsersListView, basename="user")

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path(
        "users/<int:user_id>/follow/",
        FollowUserView.as_view(),
        name="follow-user",
    ),
    path("", include(router.urls)),
]

app_name = "user"
