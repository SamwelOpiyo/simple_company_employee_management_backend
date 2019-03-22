from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from model_mommy import mommy

from employee_management_backend.users.models import User


class OrganizationTestCase(APITestCase):
    """
    Test suite for Organization api views.
    """

    def setUp(self):
        """
        Define the test client and other test variables.
        """

        self.api_version = "v1"
        self.new_user = User(username="TestUsername")
        self.new_user.is_staff = True
        self.new_user.save()

        self.post_data = {"name": "Test Organization"}

        self.client = APIClient()
        self.client.force_authenticate(user=self.new_user)
        self.response = self.client.post(
            reverse("companies:organizations-list", args=[self.api_version]),
            self.post_data,
            format="json",
        )
        self.new_organization_id = self.response.json()["id"]

    def test_organization_post(self):
        """
        Test Organization creation.
        """

        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.response.json()["name"], "Test Organization")
        self.assertEqual(self.response.json()["slug"], "test-organization")

    def test_anonymous_user_organization_post(self):
        """
        Test if the api can raise error if anonymous user tries to create an
        Organization.
        """
        new_client = APIClient()
        new_response = new_client.post(
            reverse("companies:organizations-list", args=[self.api_version]),
            self.post_data,
            format="json",
        )
        self.assertEqual(
            new_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_get_organization_list(self):
        """
        Test the api endpoint for list organizations.
        """
        response = self.client.get(
            reverse("companies:organizations-list", args=[self.api_version])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_get_organization_list(self):
        """
        Test the api endpoint for list organizations using request from
        anonymous user.
        """
        new_client = APIClient()
        new_response = new_client.get(
            reverse("companies:organizations-list", args=[self.api_version])
        )
        self.assertEqual(
            new_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_get_organization_retrieve(self):
        """
        Test the api endpoint for retrieve Organization.
        """
        response = self.client.get(
            reverse(
                "companies:organizations-detail",
                args=[self.api_version, self.new_organization_id],
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_get_organizations_retrieve(self):
        """
        Test the api endpoint for retrieve Organization using request from
        anonymous user.
        """
        new_client = APIClient()
        new_response = new_client.get(
            reverse(
                "companies:organizations-detail",
                args=[self.api_version, self.new_organization_id],
            )
        )
        self.assertEqual(
            new_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_non_staff_user_organization_post(self):
        """
        Test if the api can raise error if non-staff user tries to create an
        Organization.
        """
        new_client = APIClient()
        new_user = mommy.make("users.User")
        new_client.force_authenticate(user=new_user)
        new_response = new_client.post(
            reverse("companies:organizations-list", args=[self.api_version]),
            self.post_data,
            format="json",
        )
        self.assertEqual(new_response.status_code, status.HTTP_403_FORBIDDEN)


class OrganizationOwnerTestCase(APITestCase):
    """
    Test suite for Organization User api views.
    """

    def setUp(self):
        """
        Define the test client and other test variables.
        """

        self.api_version = "v1"
        self.new_user = User(username="TestUsername")
        self.new_user.is_staff = True
        self.new_user.save()

        self.post_data = {"name": "Test Organization(Owner)"}

        self.client = APIClient()
        self.client.force_authenticate(user=self.new_user)
        self.response = self.client.post(
            reverse("companies:organizations-list", args=[self.api_version]),
            self.post_data,
            format="json",
        )
        self.new_organization_id = self.response.json()["id"]

    def test_organization_owner_creation(self):
        """
        Test Organization Owner creation.
        """

        response = self.client.get(
            "/api/v1/organization-owner/?organization_id={}".format(
                self.new_organization_id
            )
        )

        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            self.response.json()["name"], "Test Organization(Owner)"
        )
        self.assertEqual(
            self.response.json()["slug"], "test-organizationowner"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_organization_user_creation(self):
        """
        Test Organization User creation.
        """

        response = self.client.get(
            reverse(
                "companies:organization-users-list", args=[self.api_version]
            ),
            kwargs={"organization_id": self.new_organization_id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
