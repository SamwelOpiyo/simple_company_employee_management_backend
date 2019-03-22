from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


from employee_management_backend.users.utils import user_avatar_path


class User(AbstractUser):
    GENDER_CHOICES = (
        ("male", _("Male")),
        ("female", _("Female")),
        ("other", _("Other")),
    )
    SALUTATION_CHOICES = (
        ("mr", _("MR")),
        ("mrs", _("MRS")),
        ("miss", _("MISS")),
    )
    phone_regex = RegexValidator(
        regex=r"(\d{3})\D*(\d{4}|\d{3})\D*(\d{4}|\d{3})$",
        message="Phone Number must be entered in the format: '9999999999' or '999-999-9999'.",
    )

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(
        verbose_name=_("Name of User"),
        blank=True,
        max_length=255,
        help_text=_("Enter full name of user."),
    )
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        blank=True,
        verbose_name=_("avatar"),
        help_text=_("Upload user avatar here."),
    )
    bio = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("bio"),
        help_text=_("Enter user description here (Min 500 characters)."),
    )
    salutation = models.CharField(
        choices=SALUTATION_CHOICES,
        max_length=10,
        blank=True,
        verbose_name=_("salutation"),
        help_text=_("Enter user title here."),
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("date of birth"),
        help_text=_("Enter date of birth here."),
    )
    gender = models.CharField(
        choices=GENDER_CHOICES,
        max_length=10,
        blank=True,
        verbose_name=_("gender"),
        help_text=_("Enter gender of user here."),
    )
    phone_home = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        validators=[phone_regex],
        verbose_name=_("home phone"),
        help_text=_("Enter home phone details here."),
    )
    phone_work = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        validators=[phone_regex],
        verbose_name=_("work phone"),
        help_text=_("Enter work phone details here."),
    )
    mobile = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        validators=[phone_regex],
        verbose_name=_("mobile phone number"),
        help_text=_("Enter mobile phone details here."),
    )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
        related_name="user_addresses",
        help_text=_("Select owner of address."),
    )
    address1 = models.CharField(
        max_length=255,
        verbose_name=_("address1"),
        help_text=_("Input address location."),
    )
    address2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("address2"),
        help_text=_("Input address location if another exists here."),
    )
    area = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("area"),
        help_text=_("Input area."),
    )
    city = models.CharField(
        max_length=255, verbose_name=_("city"), help_text=_("Input city.")
    )
    county = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("county"),
        help_text=_("Input county."),
    )
    postcode = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("postcode"),
        help_text=_("Input postcode."),
    )
    country = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("country"),
        help_text=_("Input country."),
    )

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")

    def __str__(self):
        return "{},{},{},{}".format(
            self.address1, self.city, self.county, self.country
        )
