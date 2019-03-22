from django.urls import path, include

from rest_framework import routers

from employee_management_backend.companies.api import views


router_companies = routers.DefaultRouter()

router_companies.register("organizations", views.OrganizationViewSet)
router_companies.register("organization-users", views.OrganizationUserViewSet)
router_companies.register("teams", views.TeamViewSet)


urlpatterns = [
    path("", include(router_companies.urls)),
    path("organization-owner/", views.OrganizationOwnerAPIView.as_view()),
]
