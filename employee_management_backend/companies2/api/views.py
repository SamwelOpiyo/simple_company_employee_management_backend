from employee_management_backend.users import models
from employee_management_backend.users.api import serializers


from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    """
    get_queryset:
    Filter queryset to get authenticated user.
    """

    queryset = models.User.objects.all().order_by("-date_joined")

    def get_serializer_class(self):
        if self.request.version == "v1":
            return serializers.SimpleUserSerializer
        return serializers.UserSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            try:
                return self.queryset.filter(id=self.request.user.id)
            except Exception:
                return self.queryset.none()


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """

    queryset = models.User.objects.all().order_by("-date_joined")

    lookup_field = "username"
    lookup_url_kwarg = "username"

    def get_serializer_class(self):
        if self.request.version == "v1":
            return serializers.ProfileSerializer
        return serializers.ProfileSerializer


class AddressViewSet(viewsets.ModelViewSet):
    """
    get_queryset:
    * Filter queryset to get authenticated user addresses.
    """

    queryset = models.Address.objects.all().order_by("-id")

    def get_serializer_class(self):
        if self.request.version == "v1":
            return serializers.SimpleAddressSerializer
        return serializers.AddressSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.request.user.user_addresses.all().order_by("-id")
