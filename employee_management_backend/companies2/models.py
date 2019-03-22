from django.db import models
from django.utils.translation import ugettext_lazy as _


from organizations.models import (
    Organization,
    OrganizationUser,
    OrganizationOwner,
)

from organizations.abstract import (
    AbstractOrganization,
    AbstractOrganizationUser,
    AbstractOrganizationOwner,
)


class Company(Organization):
    class Meta:
        proxy = True
        verbose_name = _("company")
        verbose_name_plural = _("companies")

    @property
    def company_employees(self):
        return self.organization_organization_users

    @property
    def company_created_by(self):
        return self.organization_organization_owner

    def __str__(self):
        return f"Company: {self.name}"


class Employee(OrganizationUser):
    class Meta:
        proxy = True
        verbose_name = _("employee")
        verbose_name_plural = _("employees")

    @property
    def company(self):
        return self.organization

    @property
    def employee_organization_owner(self):
        return self.organization_user_organization_owner

    def __str__(self):
        return f"Company: {self.company.name} Employee: {self.user.username}"


class CompanyCreatedBy(OrganizationOwner):
    class Meta:
        proxy = True
        verbose_name = _("company created by")
        verbose_name_plural = _("company created by")

    @property
    def employee(self):
        return self.organization_user

    @property
    def company(self):
        return self.organization

    def __str__(self):
        return "Company: {} Company Created By: {}".format(
            self.company.name, self.employee.user.username
        )


class CompanyTeam(AbstractOrganization):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_("company"),
        related_name="company_teams",
        help_text=_("Company that the team belongs to."),
    )

    class Meta:
        verbose_name = _("team")
        verbose_name_plural = _("team")

    def __str__(self):
        return f"Company: {self.company.name} Team: {self.name}"


class CompanyTeamMember(AbstractOrganizationUser):
    class Meta:
        verbose_name = _("team member")
        verbose_name_plural = _("team members")

    @property
    def company(self):
        return self.organization.company

    @property
    def company_team(self):
        return self.organization

    @property
    def company_team_created_by(self):
        return self.organization_user_organization_owner

    def __str__(self):
        return "Company: {} Team: {} Team Member: {}".format(
            self.company_team.company.name,
            self.company_team.name,
            self.user.username,
        )


class TeamCreatedBy(AbstractOrganizationUser):
    class Meta:
        verbose_name = _("team created by")
        verbose_name_plural = _("team created by")

    @property
    def company(self):
        return self.organization.company

    @property
    def company_team(self):
        return self.organization

    @property
    def company_team_member(self):
        return self.organization_user

    def __str__(self):
        return "Company: {} Team: {} Team Created By: {}".format(
            self.company_team_member.company.name,
            self.company_team_member.team.name,
            self.company_team_member.user.username,
        )
