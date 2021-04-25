from rest_framework import serializers, status
from rest_framework.decorators import action

from training import models


class UserWorkoutForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return models.Workout.objects.filter(user=self.context['request'].user)


class UserExercisesetForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return models.ExerciseSet.objects.filter(user=self.context['request'].user)


class SetSerializer(serializers.ModelSerializer):
    """
    Serializer for Set object
    """
    # to restrict user to choose only his exercisets
    exercise = UserExercisesetForeignKey()

    class Meta:
        model = models.Set
        fields = (
            'id', 'exercise',
            'reps', 'reps_unit', 'weight',
            'weight_unit', 'rest', 'rest_unit'
        )
        read_only_fields =('id', 'exercise')



class ExerciseSetSerializer(serializers.ModelSerializer):
    """
    Serializer for ExerciseSet object
    """
    id = serializers.IntegerField(required=False)
    set = SetSerializer(many=True, read_only=True)
    # to restrict user to choose only his workouts
    workout = UserWorkoutForeignKey(required=False)

    class Meta:
        model = models.ExerciseSet
        fields = ('id', 'workout', 'exercise', 'set')
        read_only_fields =('workout',)



class WorkoutSerializer(serializers.ModelSerializer):
    """
    Serializer for Workout object
    """
    exerciseset = ExerciseSetSerializer(many=True)
    date = serializers.DateField()

    class Meta:
        model = models.Workout
        fields = ('id', 'user_id', 'date', 'exerciseset')
        read_only_fields =('id', 'user_id')

    def create(self, validated_data):
        """
        Create workout with exercisesets
        """
        exercisesets = validated_data.pop('exerciseset', None)

        workout = models.Workout.objects.create(**validated_data)
        # create exercisesets for workout
        for exerciseset in exercisesets:
            exercise = models.ExerciseSet.objects.create(**exerciseset, workout=workout, user=self.context['request'].user)

    def update(self, instance, validated_data):
        """
        Update workout with exercisesets
        """
        exercisesets = validated_data.pop('exerciseset', None)
        instance.date = validated_data.get('date', instance.date)
        instance.save()

        workout_exercisesets = instance.exerciseset.all()
        # keep track of exercisesets (ids) to be kept for workout
        keep_exercisesets = []
        for exerciseset in exercisesets:
            # if id -> update exerciseset(exists) / else create
            if 'id' in exerciseset.keys():
                if models.ExerciseSet.objects.filter(id=exerciseset['id']).exists():
                    exercise = models.ExerciseSet.objects.get(id=exerciseset['id'])
                    exercise.exercise = exerciseset.get('exercise', exercise.exercise)
                    exercise.save()
                    keep_exercisesets.append(exercise.id)
                else:
                    continue
            else:
                exercise = models.ExerciseSet.objects.create(**exerciseset, workout=instance, user=self.context['request'].user)
                keep_exercisesets.append(exercise.id)

        for exerciseset in workout_exercisesets:
            # if not in keep_exercisesets -> exerciseset was deleted by user
            if exerciseset.id not in keep_exercisesets:
                exerciseset.delete()

        return instance

        return workout
