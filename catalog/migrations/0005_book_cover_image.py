# Generated by Django 5.1.6 on 2025-03-06 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_book_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='book_covers/'),
        ),
    ]
