# Generated by Django 4.1.1 on 2022-09-27 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_remove_user_dislikes_remove_user_likes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='telegram_id',
            field=models.CharField(max_length=200, unique=True, verbose_name='телеграм id'),
        ),
    ]