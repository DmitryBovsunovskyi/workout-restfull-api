from rest_framework import serializers

from training import models


class SetSerializer(serializers.ModelSerializer):
    """
    Serializer for Set object
    """

    class Meta:
        model = models.Set
        fields = (
            'id', 'user_id', 'exercise',
            'reps', 'reps_unit', 'weight',
            'weight_unit', 'rest', 'rest_unit'
        )
        read_only_fields =('id',)


class ExerciseSetSerializer(serializers.ModelSerializer):
    """
    Serializer for ExerciseSet object
    """
    set = SetSerializer(many=True, read_only=True)
    exercise = serializers.StringRelatedField()
    workout = serializers.StringRelatedField()

    class Meta:
        model = models.ExerciseSet
        fields = ('id', 'user_id', 'workout', 'exercise', 'set',)
        read_only_fields =('id',)


class WorkoutSerializer(serializers.ModelSerializer):
    """
    Serializer for Workout object
    """
    exerciseset = ExerciseSetSerializer(many=True, read_only=True)


    date = serializers.DateField()
    class Meta:
        model = models.Workout
        fields = ('id', 'user_id', 'date', 'exerciseset')
        read_only_fields =('id',)
