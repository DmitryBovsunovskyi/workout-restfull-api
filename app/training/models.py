from django.db import models
from django.conf import settings

from training.constants import REPS_UNIT_CHOICES, WEIGHT_UNIT_CHOICES, REST_UNIT_CHOICES


class MuscleGroup(models.Model):
    """
    Object for muscle group instance
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)


    def __str__(self):
    	return self.name

class Exercise(models.Model):
    """
    Object for exercise instance
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    muscles = models.ManyToManyField("MuscleGroup", related_name="muscles")

    def __str__(self):
    	return self.name


class Workout(models.Model):
    """
    Object for training instance
    """
    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):

        return str(self.date)


class ExerciseSet(models.Model):
    """
    Object for exerciseset instance to be used in workout
    """
    workout = models.ForeignKey('Workout',on_delete=models.CASCADE, related_name='exerciseset')
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
    	return str(self.exercise)


class Set(models.Model):
    """
    Object for set instance to be used in exerciseset
    """
    exercise = models.ForeignKey('ExerciseSet', on_delete=models.CASCADE, related_name='set')
    reps = models.PositiveIntegerField(default=0)
    reps_unit = models.CharField(max_length=20, choices=REPS_UNIT_CHOICES.choices(), default=REPS_UNIT_CHOICES.REPS)
    weight = models.DecimalField(max_digits=20, decimal_places=2)
    weight_unit = models.CharField(max_length=20, choices=WEIGHT_UNIT_CHOICES.choices(), default=WEIGHT_UNIT_CHOICES.KG)
    rest = models.PositiveIntegerField(default=0)
    rest_unit = models.CharField(max_length=20, choices=REST_UNIT_CHOICES.choices(), default=REST_UNIT_CHOICES.MIN)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
    	return f"{self.reps} {self.reps_unit} x {self.weight} {self.weight_unit}"
