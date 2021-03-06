# Generated by Django 3.1.8 on 2021-04-13 12:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('training', '0002_auto_20210413_1232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exerciseset',
            name='workout_session',
        ),
        migrations.AddField(
            model_name='exerciseset',
            name='workout',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='training.workout'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workout',
            name='exercises',
            field=models.ManyToManyField(related_name='exercises', to='training.Exercise'),
        ),
        migrations.AddField(
            model_name='workout',
            name='user',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, to='user.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='exerciseset',
            name='exercise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='training.exercise'),
        ),
        migrations.DeleteModel(
            name='WorkoutSession',
        ),
    ]
