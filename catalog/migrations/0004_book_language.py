# Generated by Django 5.1.6 on 2025-03-06 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_author_author_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='language',
            field=models.CharField(blank=True, help_text="Enter the book's language", max_length=100, null=True),
        ),
    ]
