# Generated by Django 4.1.2 on 2022-11-22 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_billingaddress"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="billing_address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.billingaddress",
            ),
        ),
    ]
