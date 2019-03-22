from django.urls import path, include

from rest_framework import routers

from employee_management_backend.companies.api import views


router_companies = routers.DefaultRouter()

router_companies.register(
    "organizations", views.OrganizationViewSet, "organizations"
)
router_companies.register(
    "organization-users", views.OrganizationUserViewSet, "organization-users"
)
router_companies.register("teams", views.TeamViewSet, "teams")


urlpatterns = [
    path("", include(router_companies.urls)),
    path(
        "organization-owner/",
        views.OrganizationOwnerAPIView.as_view(),
        name="organization-owner",
    ),
]
