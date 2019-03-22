from django.db import models
from django.utils.translation import ugettext_lazy as _


from organizations.models import (
    Organization,
    OrganizationUser,
    OrganizationOwner,
)


class Team(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name=_("organization"),
        related_name="organization_teams",
        help_text=_("Organization that the team belongs to."),
    )
    name = models.CharField(
        max_length=200,
        help_text=_("The name of the team."),
        verbose_name=_("name"),
    )

    class Meta:
        verbose_name = _("team")
        verbose_name_plural = _("team")

    def __str__(self):
        return f"Organization: {self.organization.name} Team: {self.name}"


class TeamMember(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name=_("team"),
        related_name="team_team_members",
        help_text=_("Team being referred to."),
    )
    organization_user = models.ForeignKey(
        OrganizationUser,
        on_delete=models.CASCADE,
        verbose_name=_("organization user"),
        related_name="organization_user_team_member_instances",
        help_text=_("Employee/organization user who is part of the team."),
    )
    is_admin = models.BooleanField(
        verbose_name=_("is administrator"),
        help_text=_(
            "Is the employee/organization user an administrator of this team."
        ),
    )

    class Meta:
        unique_together = (("team", "organization_user"),)
        verbose_name = _("team member")
        verbose_name_plural = _("team members")

    def __str__(self):
        return "Organization: {} Team: {} Team Member: {}".format(
            self.team.organization.name,
            self.team.name,
            self.organization_user.user.username,
        )
