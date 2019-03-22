# Generated by Django 2.0.13 on 2019-03-21 23:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [("organizations", "0003_field_fix_and_editable")]

    operations = [
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name of the team.",
                        max_length=200,
                        verbose_name="name",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        help_text="Organization that the team belongs to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organization_teams",
                        to="organizations.Organization",
                        verbose_name="organization",
                    ),
                ),
            ],
            options={"verbose_name": "team", "verbose_name_plural": "team"},
        ),
        migrations.CreateModel(
            name="TeamMember",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_admin",
                    models.BooleanField(
                        help_text="Is the employee/organization user an administrator of this team.",
                        verbose_name="is administrator",
                    ),
                ),
                (
                    "organization_user",
                    models.ForeignKey(
                        help_text="Employee/organization user who is part of the team.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organization_user_team_member_instances",
                        to="organizations.OrganizationUser",
                        verbose_name="organization user",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        help_text="Team being referred to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team_team_members",
                        to="companies.Team",
                        verbose_name="team",
                    ),
                ),
            ],
            options={
                "verbose_name": "team member",
                "verbose_name_plural": "team members",
            },
        ),
        migrations.AlterUniqueTogether(
            name="teammember", unique_together={("team", "organization_user")}
        ),
    ]