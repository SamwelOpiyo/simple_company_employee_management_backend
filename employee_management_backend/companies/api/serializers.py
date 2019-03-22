from rest_framework import serializers

from organizations.models import (
    Organization,
    OrganizationUser,
    OrganizationOwner,
)

from employee_management_backend.companies import models
from employee_management_backend.users.api.serializers import ProfileSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    users_nested = ProfileSerializer(source="users", many=True, read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "is_active",
            "created",
            "modified",
            "users_nested",
        ]
        extra_kwargs = {
            "slug": {"read_only": True},
            "created": {"read_only": True},
            "modified": {"read_only": True},
        }


class SimpleOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "is_active", "created", "modified"]
        extra_kwargs = {
            "slug": {"read_only": True},
            "created": {"read_only": True},
            "modified": {"read_only": True},
        }


class OrganizationUserSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True, required=False)
    user_nested = ProfileSerializer(source="user", read_only=True)
    organization_nested = OrganizationSerializer(
        source="organization", read_only=True
    )

    class Meta:
        model = OrganizationUser
        fields = [
            "id",
            "is_admin",
            "user_email",
            "user_nested",
            "organization",
            "organization_nested",
            "created",
            "modified",
        ]
        extra_kwargs = {
            "created": {"read_only": True},
            "modified": {"read_only": True},
            "organization": {"write_only": True},
        }


class SimpleOrganizationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationUser
        fields = [
            "id",
            "is_admin",
            "user",
            "organization",
            "created",
            "modified",
        ]
        extra_kwargs = {
            "created": {"read_only": True},
            "modified": {"read_only": True},
        }


class SimpleOrganizationOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationOwner
        fields = [
            "id",
            "organization_user",
            "organization",
            "created",
            "modified",
        ]
        extra_kwargs = {
            "created": {"read_only": True},
            "modified": {"read_only": True},
        }


class OrganizationOwnerSerializer(serializers.ModelSerializer):
    organization_user_nested = SimpleOrganizationUserSerializer(
        source="organization_user", read_only=True
    )
    organization_nested = OrganizationSerializer(
        source="organization", read_only=True
    )

    class Meta:
        model = OrganizationOwner
        fields = [
            "id",
            "organization_user",
            "organization_user_nested",
            "organization",
            "organization_nested",
            "created",
            "modified",
        ]
        extra_kwargs = {
            "organization": {"write_only": True},
            "organization_user": {"write_only": True},
            "created": {"read_only": True},
            "modified": {"read_only": True},
        }


class SimpleTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Team
        fields = ["id", "organization", "name"]


class TeamSerializer(serializers.ModelSerializer):
    organization_nested = OrganizationSerializer(
        source="organization", read_only=True
    )

    class Meta:
        model = models.Team
        fields = ["id", "organization", "organization_nested", "name"]
        extra_kwargs = {"organization": {"write_only": True}}


class SimpleTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TeamMember
        fields = ["id", "team", "organization_user", "is_admin"]


class TeamMemberSerializer(serializers.ModelSerializer):
    organization_user_nested = OrganizationUserSerializer(
        source="organization_user", read_only=True
    )
    team_nested = SimpleTeamSerializer(source="team", read_only=True)

    class Meta:
        model = models.Team
        fields = [
            "id",
            "organization_user",
            "organization_user_nested",
            "team",
            "team_nested",
            "is_admin",
            "name",
        ]
        extra_kwargs = {
            "organization_user": {"write_only": True},
            "team": {"write_only": True},
        }
