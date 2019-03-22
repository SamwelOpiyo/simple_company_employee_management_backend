from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from model_mommy import mommy


class UserViewSetTestCase(APITestCase):
    """
    Test suite for User api views.
    """

    def setUp(self):
        """
        Define the test client and other test variables.
        """

        self.api_version = "v1"
        self.new_user = mommy.make("users.User")

        self.post_data = {"username": "JamesJudy"}

        self.client = APIClient()
        self.client.force_authenticate(user=self.new_user)
        self.response = self.client.post(
            reverse("api_users:user-list", args=[self.api_version]),
            self.post_data,
            format="json",
        )

    def test_user_post(self):
        """
        Test User creation.
        """

        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.response.json()["username"], "JamesJudy")
        self.assertEqual(self.response.json()["first_name"], "")

    def test_anonymous_user_user_post(self):
        """
        Test if the api can raise error if anonymous user tries to create a
        User.
        """
        new_client = APIClient()
        new_response = new_client.post(
            reverse("api_users:user-list", args=[self.api_version]),
            self.post_data,
            format="json",
        )
        self.assertEqual(
            new_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_get_user_list(self):
        """
        Test the api endpoint for list user.
        """
        response = self.client.get(
            reverse("api_users:user-list", args=[self.api_version])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_get_user_list(self):
        """
        Test the api endpoint for list user using request from
        anonymous user.
        """
        new_client = APIClient()
        new_response = new_client.get(
            reverse("api_users:user-list", args=[self.api_version])
        )
        print(new_response.json)
        self.assertEqual(
            new_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_get_user_retrieve(self):
        """
        Test the api endpoint for retrieve User.
        """
        response = self.client.get(
            reverse(
                "api_users:user-detail",
                args=[self.api_version, self.new_user.id],
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_get_user_retrieve(self):
        """
        Test the api endpoint for retrieve User using request from
        anonymous user.
        """
        new_client = APIClient()
        new_user = mommy.make("users.User")
        new_response = new_client.get(
            reverse(
                "api_users:user-detail", args=[self.api_version, new_user.id]
            )
        )
        self.assertEqual(
            new_response.status_code, status.HTTP_401_UNAUTHORIZED
        )
