# Generated by Django 3.1.8 on 2021-04-13 12:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import training.constants


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExerciseSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exerciseset', to='training.exercise')),
            ],
        ),
        migrations.CreateModel(
            name='MuscleGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercises', models.ManyToManyField(related_name='exercises', to='training.ExerciseSet')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workout_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workoutsession', to='training.workout')),
            ],
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reps', models.PositiveIntegerField(default=0)),
                ('reps_unit', models.CharField(choices=[('REPS', 'Repetitions'), ('MIN', 'Minutes'), ('SEC', 'Seconds'), ('KM', 'Kilometers')], default=training.constants.REPS_UNIT_CHOICES['REPS'], max_length=20)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=20)),
                ('weight_unit', models.CharField(choices=[('KG', 'Kilograms'), ('BW', 'Body weight'), ('KH', 'Kilometers per hour')], default=training.constants.WEIGHT_UNIT_CHOICES['KG'], max_length=20)),
                ('rest', models.PositiveIntegerField(default=0)),
                ('rest_unit', models.CharField(choices=[('SEC', 'seconds'), ('MIN', 'Minutes'), ('HR', 'Hours')], default=training.constants.REST_UNIT_CHOICES['MIN'], max_length=20)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='set', to='training.exerciseset')),
            ],
        ),
        migrations.AddField(
            model_name='exerciseset',
            name='workout_session_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exerciseset', to='training.workoutsession'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='muscles',
            field=models.ManyToManyField(related_name='muscles', to='training.MuscleGroup'),
        ),
    ]