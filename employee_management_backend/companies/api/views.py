from django.contrib.sites.shortcuts import get_current_site
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404

from employee_management_backend.companies import models
from employee_management_backend.companies.api import serializers
from employee_management_backend.users.models import User

from organizations.backends import invitation_backend
from organizations.models import (
    Organization,
    OrganizationUser,
    OrganizationOwner,
)

from rest_framework import views, viewsets, status, exceptions
from rest_framework.response import Response
from rest_framework.settings import api_settings


class BaseListRetrieveWithOrganizationID:
    """Add organization_id get parameter to list and retrieve methods.

    # Methods

    ## list:
    * GET list Endpoint.
    * Displays objects of a single organization (The organization_id get
      parameter is used to filter the organisation) that the user is part of.
    ## Returns
    * List of objects.
    ## Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.

    ## retrieve:
    * GET details Endpoint.
    * Displays details of object found in a particular organization (The
      organization_id get parameter is used to filter the organization)
      that the user is part of.
    ## Returns
    * Details of a model instance.
    ## Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_404_NOT_FOUND
        * If user trying to get model instance is not an organization user of
          the organization.
    """

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            organization_id = self.request.query_params.get(
                "organization_id", None
            )
            queryset = self.filter_queryset(self.get_queryset(organization_id))

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            raise exceptions.AuthenticationFailed()

    def retrieve(self, request, pk=None, *args, **kwargs):
        organization_id = self.request.query_params.get(
            "organization_id", None
        )
        instance = get_object_or_404(self.get_queryset(organization_id), id=pk)
        return Response(self.get_serializer(instance).data)


class OrganizationViewSet(viewsets.ModelViewSet):
    """Organization Management Viewset.

    # Methods

    ## get_serializer_class:
    * Used to specify which serializer to use depending on API version requested.
    * v1 returns details with related fields having only the ID while v2
      returns details with nested related fields.

    ## get_queryset:
    * Used to filter queryset to get organizations where authenticated user is
      an organization user/member.

    ## create:
    * POST Organization details Endpoint.
    * Creates an organization and adds the authenticated user that has created
      the organization as an organization user and organization owner if he/she
      is a staff member.
    ### Returns
    * Created Organization with status rest_framework.status.HTTP_201_CREATED.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_400_BAD_REQUEST
        * If post data for POST request is not valid.
    * status.HTTP_403_FORBIDDEN
        * If user trying to create the organization is not a staff member.

    ## update:
    * PUT/PATCH Organization details Endpoint.
    * Updates Organization Object if the authenticated user trying to update
      the organization is the organization owner.
    ### Returns
    * Updated Organization details.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_400_BAD_REQUEST
        * If post data for POST request is not valid.
    * status.HTTP_403_FORBIDDEN
        * If organization user trying to delete the organization is not the
          organization owner.
    * status.HTTP_404_NOT_FOUND
        * If user trying to do an update is not an organization user of the
          organization.

    ## destroy:
    * DELETE Organization details Endpoint.
    * Used to delete an Organization Object if the authenticated user trying to
      delete the organization is a staff member.
    ### Returns
    * Empty with status rest_framework.status.HTTP_204_NO_CONTENT.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_403_FORBIDDEN
        * If organization user trying to delete the organization is not the
          organization owner.
    * status.HTTP_404_NOT_FOUND
        * If user trying to delete object is not an organization user.
    """

    queryset = Organization.objects.all().order_by("-created")

    def get_serializer_class(self):
        if self.request.version == "v1":
            return serializers.SimpleOrganizationSerializer
        return serializers.OrganizationSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.version == "v1":
                return self.queryset.filter(users=self.request.user)
            else:
                return self.queryset.filter(
                    users=self.request.user
                ).prefetch_related("users")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.is_staff:
            self.perform_create(serializer)
            # Adds the first user as an organization user and organization owner.
            serializer.instance.get_or_add_user(request.user)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            raise exceptions.PermissionDenied(
                "Only Staff Members can create an organization!"
            )

    def update(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            if instance.owner.organization_user.user == request.user:
                self.perform_update(serializer)
            else:
                raise exceptions.PermissionDenied(
                    "User is not allowed to update this organization!"
                )

            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            raise exceptions.AuthenticationFailed()

    def destroy(self, request, pk=None, *args, **kwargs):
        if request.user.is_authenticated:
            organization = get_object_or_404(self.get_queryset(), id=pk)
            if request.user.is_staff:
                organization.delete()
            else:
                raise exceptions.PermissionDenied(
                    "Only Staff Members can delete an organization!"
                )

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.AuthenticationFailed()


class OrganizationUserViewSet(
    BaseListRetrieveWithOrganizationID, viewsets.ModelViewSet
):
    """Organization User Management Viewset.

    # Methods

    ## get_serializer_class:
    * Used to specify which serializer to use depending on API version requested.
    * v1 returns details with related fields having only the ID while v2
      returns details with nested related fields.

    ## get_queryset:
    * Used to filter queryset to get organization (The organization_id parameter
      is used to filter the organization) where self.request.user is an
      organization user/member and then gets the organization users of that
      organization.

    ## list:
    * GET OrganizationUser list Endpoint.
    * Displays OrganizationUser objects of a single organization (The
      organization_id get parameter is used to filter the organisation) that
      the user is part of.
    ### Returns
    * List of OrganizationUser objects.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.

    ## retrieve:
    * GET OrganizationUser details Endpoint.
    * Displays details of OrganizationUser object found in a particular
      organization (The organization_id get parameter is used to filter the
      organization) that the user is part of.
    ### Returns
    * Details of OrganizationUser.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_404_NOT_FOUND
        * If user trying to get OrganizationUser is not an organization user of
          the organization.

    ## create:
    * POST OrganizationUser details Endpoint.
    * Adds an OrganizationUser if authenticated user is an organization
      admin.
    * If user with email provided does not exist, it creates the user.
    * Send a notification email to this user to inform them that they have
      been added to a new organization.
    ### Returns
    * Created OrganizationUser with status.HTTP_201_CREATED.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_400_BAD_REQUEST
        * If post data for POST request is not valid.
    * status.HTTP_403_FORBIDDEN
        * If user trying to create object is not an organization user.
        * If user trying to create object is not an organization admin.

    ## update:
    * PUT/PATCH Organization details Endpoint.
    * Updates an OrganizationUser Object if the authenticated user trying to
      update the organization is an administrator.
    * It is used to give or deny a user admin priviledges by an administrator.
    * Organization field cannot be updated and is used to filter the user's
      organizations. Its value must be similar to the initial value or else
      the correct organization user object will not be found.
    * User field cannot be updated.
    ### Returns
    * Updated Organization details.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_403_FORBIDDEN
        * If authenticated user tries to take away organization owner's admin
          priviledges.
        * If authenticated user is not an organization admin.
    * status.HTTP_404_NOT_FOUND
        * If user trying to do an update is not an organization user of the
          organization.

    ## destroy:
    * DELETE Organization details Endpoint.
    * Used to delete Organization User Object if the authenticated user trying
      to delete the organizationUser is:
        * An organization owner.
        * An organization user who is an administrator.
        * The one leaving the organization.
    ### Returns
    * Empty response with status rest_framework.status.HTTP_204_NO_CONTENT.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_403_FORBIDDEN
        * If user trying to perform a delete is not an organization
          administrator or owner.
    * status.HTTP_404_NOT_FOUND
        * If user trying to do a delete is not part of the organization.
    """

    queryset = OrganizationUser.objects.all().order_by("-created")

    def get_serializer_class(self):
        if self.request.version == "v1":
            return serializers.SimpleOrganizationUserSerializer
        return serializers.OrganizationUserSerializer

    def get_queryset(self, organization_id=None):
        if self.request.user.is_authenticated:
            try:
                if self.request.version == "v1":
                    return self.queryset.filter(
                        organization_id=organization_id,
                        organization__users=self.request.user,
                    )
                else:
                    return (
                        self.queryset.filter(
                            organization_id=organization_id,
                            organization__users=self.request.user,
                        )
                        .select_related("user", "organization")
                        .prefetch_related("organization__users")
                    )
            except Exception:
                return OrganizationUser.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data.get("user_email"):
            raise exceptions.ValidationError(
                "user_email has not been provided!"
            )
        try:
            user = User.objects.get(
                email__iexact=serializer.validated_data.get("user_email")
            )
        except User.MultipleObjectsReturned:
            raise exceptions.ValidationError(
                "This email address has been used multiple times."
            )
        except User.DoesNotExist:
            user = invitation_backend().invite_by_email(
                serializer.validated_data.get("user_email"),
                **{
                    "domain": get_current_site(request),
                    "organization": serializer.validated_data.get(
                        "organization"
                    ),
                    "sender": request.user,
                }
            )
        serializer.validated_data["user"] = user

        if (
            request.user
            in serializer.validated_data.get("organization").users.all()
        ):
            if request.user.organizations_organizationuser.get(
                organization=serializer.validated_data.get("organization").id
            ).is_admin:
                try:
                    serializer.validated_data.pop("user_email")
                except KeyError:
                    pass

                try:
                    self.perform_create(serializer)
                    # Send a notification email to this user to inform them that
                    # they have been added to a new organization.
                    invitation_backend().send_notification(
                        user,
                        **{
                            "domain": get_current_site(request),
                            "organization": serializer.validated_data.get(
                                "organization"
                            ),
                            "sender": request.user,
                        }
                    )
                except IntegrityError:
                    raise exceptions.ValidationError(
                        "The user is already a member of the specified organization!"
                    )
            else:
                raise exceptions.PermissionDenied(
                    "User is not allowed to create an organization user in this organization!"
                )
        else:
            raise exceptions.PermissionDenied(
                "User is not part of the organization specified!"
            )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, pk=None, *args, **kwargs):
        if request.user.is_authenticated:
            # Use value in organization field to get the correct instance of
            # organization user. Its value should be similar as before or else
            # the correct instance won't be found and a 404 error would be
            # raised.
            organization_id = self.request.data.get("organization", None)
            partial = kwargs.pop("partial", False)
            instance = get_object_or_404(
                self.get_queryset(organization_id=organization_id), id=pk
            )

            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)

            # Unset organization field so that it cannot be updated.
            try:
                serializer.validated_data.pop("organization")
            except KeyError:
                pass
            # Unset user field so that it cannot be updated.
            try:
                serializer.validated_data.pop("user")
            except KeyError:
                pass

            if request.user.organizations_organizationuser.get(
                organization=organization_id
            ).is_admin:
                if (
                    serializer.instance.user == request.user
                    and not serializer.validated_data.get("is_admin")
                ):
                    raise exceptions.PermissionDenied(
                        "Organization owner must be an administrator!"
                    )
                try:
                    serializer.validated_data.pop("user_email")
                except KeyError:
                    pass
                self.perform_update(serializer)
            else:
                raise exceptions.PermissionDenied(
                    "User is not allowed to update this organization user!"
                )

            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            raise exceptions.AuthenticationFailed()

    def destroy(self, request, pk=None, *args, **kwargs):
        if request.user.is_authenticated:
            organization_id = self.request.query_params.get(
                "organization_id", None
            )
            organization_user = get_object_or_404(
                self.get_queryset(organization_id), id=pk
            )
            organization = Organization.objects.get(id=organization_id)
            # Check if request.user is the organization owner
            if organization.owner.organization_user.user == request.user:
                organization_user.delete()
            # Check if the organization user being deleted is the request.user.
            elif organization_user.user == request.user:
                organization_user.delete()
            # Check if request.user is one of the organization's administrators
            elif request.user.organizations_organizationuser.get(
                organization=organization
            ).is_admin:
                # If that is true, the delete can proceed
                organization_user.delete()
            else:
                raise exceptions.PermissionDenied(
                    "User is not allowed to delete this organization user!"
                )

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.AuthenticationFailed()


class OrganizationOwnerAPIView(views.APIView):
    """OrganizationOwner Management Viewset.

    get_queryset:
    # Used to filter queryset.
    * Filter queryset to get organization where self.request.user is an
      organization user/member (The organization_id parameter is used for this).
    * Get the organization owner from the organization obtained above which
      is then returned.

    get:
    # GET OrganizationOwner details Endpoint.
    # Returns
    * Details of a particular OrganizationOwner.
    # Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_404_NOT_FOUND
        * If user trying is not part of the organization.
    """

    queryset = OrganizationOwner.objects.all().order_by("-created")

    def get_serializer_class(self):
        if self.request.version == "v1":
            return serializers.SimpleOrganizationOwnerSerializer
        return serializers.OrganizationOwnerSerializer

    def get_queryset(self, organization_id=None):
        if self.request.user.is_authenticated:
            if self.request.version == "v1":
                return self.queryset.filter(
                    organization_id=organization_id,
                    organization_user__user=self.request.user,
                )
            else:
                return (
                    self.queryset.filter(
                        organization_id=organization_id,
                        organization_user__user=self.request.user,
                    )
                    .select_related("organization", "organization_user")
                    .prefetch_related(
                        "organization_user__user",
                        "organization_user__organization",
                        "organization__users",
                    )
                )

    def get(self, request, *args, **kwargs):
        self.serializer_class = self.get_serializer_class()

        if request.user.is_authenticated:
            organization_id = self.request.query_params.get(
                "organization_id", None
            )
            instance = get_object_or_404(self.get_queryset(organization_id))
            return Response(self.serializer_class(instance).data)
        else:
            raise exceptions.AuthenticationFailed()


class TeamViewSet(BaseListRetrieveWithOrganizationID, viewsets.ModelViewSet):
    """Team Management Viewset.

    # Methods

    ## get_serializer_class:
    * Used to specify which serializer to use depending on API version requested.
    * v1 returns details with related fields having only the ID while v2
      returns details with nested related fields.

    ## get_queryset:
    * Used to filter queryset.
    * Filters queryset to get organization where self.request.user is an
      organization user/member (The organization_id parameter is used for this).
    * Gets all the teams associated to this organization.

    ## list:
    * GET Team list Endpoint.
    * Displays Team objects of a single organization (The organization_id get
      parameter is used to filter the organisation) that the user is part of.
    ### Returns
    * List of Team objects.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.

    ## retrieve:
    * GET Team details Endpoint.
    * Displays details of Team object found in a particular organization (The
      organization_id get parameter is used to filter the organization)
      that the user is part of.
    ### Returns
    * Details of a Team model instance.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_404_NOT_FOUND
        * If user trying to get model instance is not an organization user of
          the organization.

    ## create:
    * POST Team details Endpoint.
    * Adds Team.
    * Adds a Team if the authenticated user is an organization owner or
      administrator in the organization in which the Team is created in.
    ### Returns
    * Created Team with status.HTTP_201_CREATED.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_400_BAD_REQUEST
        * If post data for POST request is not valid.
    * status.HTTP_403_FORBIDDEN
        * If authenticated user creating the team is not an organization
          user in the organization in which the event is being created.
        * If authenticated user creating the team is not an organization
          admin in the organization in which the event is being created.

    ## update:
    * PUT/PATCH Team details Endpoint.
    * Updates Team Object if the authenticated user trying to update the
      organization is an organization administrator or owner of the
      organization in which the team was created under.
    * Organization field cannot be updated and is used to filter the user's
      organizations. Its value must be similar to the initial value or else
      the correct organization object will not be found.
    ### Returns
    * Updated Team details.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_403_FORBIDDEN
        If authenticated user doing an update is not an organization admin.
    * status.HTTP_404_NOT_FOUND
        If user trying to do an update is not an organization user of the
        organization.


    ## destroy:
    * DELETE Team details Endpoint.
    * Used to delete team Object if the authenticated user trying to delete the
      Team is an organization administrator or owner for the organization
      in which the Team was created under.
    ### Returns
    * Empty response with status rest_framework.status.HTTP_204_NO_CONTENT.
    ### Raises
    * status.HTTP_401_UNAUTHORIZED
        * If request is from anonymous user.
    * status.HTTP_403_FORBIDDEN
        * If user trying to perform a delete is not an organization
          administrator or owner.
    * status.HTTP_404_NOT_FOUND
        * If user trying to do a delete is not part of the organization.
    """

    queryset = models.Team.objects.all().order_by("-id")

    def get_serializer_class(self):
        if self.request.version == "v1":
            return serializers.SimpleTeamSerializer
        else:
            return serializers.TeamSerializer

    def get_queryset(self, organization_id=None):
        if self.request.user.is_authenticated:
            if self.request.version == "v1":
                return self.queryset.filter(
                    organization_id=organization_id,
                    organization__users=self.request.user,
                )
            else:
                return (
                    self.queryset.filter(
                        organization_id=organization_id,
                        organization__users=self.request.user,
                    )
                    .select_related("organization")
                    .prefetch_related("organization__users")
                )

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            organization = serializer.validated_data.get("organization")

            # Check if request.user is the organization owner
            if organization.owner.organization_user.user == request.user:
                self.perform_create(serializer)
            # Check if request.user is an administrator
            elif request.user in organization.users.all():
                if request.user.organizations_organizationuser.get(
                    organization=organization.id
                ).is_admin:
                    self.perform_create(serializer)
                else:
                    raise exceptions.ValidationError(
                        "User is not allowed to create a team for this organization!"
                    )
            else:
                raise exceptions.ValidationError(
                    "User is not a part of the organization specified!"
                )

            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            raise exceptions.AuthenticationFailed()

    def update(self, request, pk=None, *args, **kwargs):
        if request.user.is_authenticated:
            # Use value in organization field to get the correct instance of
            # organization user. Its value should be similar as before or else
            # the correct instance won't be found and a 404 error would be
            # raised.
            organization_id = self.request.data.get("organization", None)
            partial = kwargs.pop("partial", False)
            instance = get_object_or_404(
                self.get_queryset(organization_id=organization_id), id=pk
            )

            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)

            # Unset organization field so that it cannot be updated.
            try:
                serializer.validated_data.pop("organization")
            except KeyError:
                pass

            # Check if request.user is the organization owner
            if (
                instance.organization.owner.organization_user.user
                == request.user
            ):
                self.perform_update(serializer)
            # Check if request.user is an administrator
            elif request.user.organizations_organizationuser.get(
                organization=organization_id
            ).is_admin:
                self.perform_update(serializer)
            else:
                raise exceptions.PermissionDenied(
                    "User is not allowed to update this Team!"
                )

            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we need
                # to forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            raise exceptions.AuthenticationFailed()

    def destroy(self, request, pk=None, *args, **kwargs):
        if request.user.is_authenticated:
            organization_id = self.request.query_params.get(
                "organization_id", None
            )
            team = get_object_or_404(self.get_queryset(organization_id), id=pk)

            # Check if request.user is the organization owner
            if organization.owner.organization_user.user == request.user:
                team.delete()
            # If request.user, is an admin for the organization, delete team
            elif request.user.organizations_organizationuser.get(
                organization_id=organization_id
            ).is_admin:
                team.delete()
            else:
                raise exceptions.PermissionDenied(
                    "User is not allowed to delete this team!"
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.AuthenticationFailed()
