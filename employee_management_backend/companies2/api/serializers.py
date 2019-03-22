from rest_framework import serializers

from employee_management_backend.users import models


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "name",
            "avatar",
            "bio",
            "salutation",
            "gender",
            "date_joined",
        ]
        extra_kwargs = {
            "date_joined": {"read_only": True},
            "username": {"read_only": True},
            "first_name": {"read_only": True},
            "last_name": {"read_only": True},
            "name": {"read_only": True},
            "avatar": {"read_only": True},
            "bio": {"read_only": True},
            "salutation": {"read_only": True},
            "gender": {"read_only": True},
        }


class AddressSerializer(serializers.ModelSerializer):
    user_nested = ProfileSerializer(source="user", read_only=True)

    class Meta:
        model = models.Address
        fields = [
            "id",
            "user",
            "user_nested",
            "address1",
            "address2",
            "area",
            "city",
            "county",
            "postcode",
            "country",
        ]
        extra_kwargs = {"user": {"write_only": True}}


class SimpleAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = [
            "id",
            "user",
            "address1",
            "address2",
            "area",
            "city",
            "county",
            "postcode",
            "country",
        ]


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "name",
            "email",
            "avatar",
            "bio",
            "salutation",
            "date_of_birth",
            "gender",
            "phone_home",
            "phone_work",
            "mobile",
            "date_joined",
        ]
        extra_kwargs = {"date_joined": {"read_only": True}}


class UserSerializer(serializers.ModelSerializer):
    address_nested = AddressSerializer(
        source="user_addresses", many=True, read_only=True
    )

    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "name",
            "email",
            "avatar",
            "bio",
            "salutation",
            "date_of_birth",
            "gender",
            "phone_home",
            "phone_work",
            "mobile",
            "date_joined",
            "address_nested",
        ]
        extra_kwargs = {"date_joined": {"read_only": True}}
