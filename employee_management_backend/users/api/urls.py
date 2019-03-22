from django.urls import path, include
from rest_framework import routers

from employee_management_backend.users.api import views


router_users = routers.DefaultRouter()

router_users.register("user", views.UserViewSet, "user")
router_users.register("profiles", views.ProfileViewSet, "profiles")
router_users.register("addresses", views.AddressViewSet, "addresses")


urlpatterns = [path("", include(router_users.urls))]
