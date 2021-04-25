from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from training.models import Workout, Exercise, ExerciseSet, Set
from training.utils import BaseViewTraining
from training import serializers


class WorkoutView(BaseViewTraining):
    """
    Manage workout in database
    """
    queryset = Workout.objects.all()
    serializer_class = serializers.WorkoutSerializer


class ExerciseSetView(BaseViewTraining):
    """
    Manage exerciseset in database
    """
    queryset = ExerciseSet.objects.all()
    serializer_class = serializers.ExerciseSetSerializer

    @action(detail=True)
    def total_rest_time(self, request, pk=None):
        """
        Return total time of rest during exercise
        """
        exercise = self.get_object()
        total_rest_time = 0
        sets = exercise.set.all()
        if sets:
            for set in sets:
                if set.rest_unit == 'MIN':
                    total_rest_time += set.rest
                elif set.rest_unit == 'SEC':
                    total_rest_time += set.rest/60
                elif set.rest_unit == 'HR':
                    total_rest_time += set.rest*60

            return Response({f'total time of rest in {exercise}': f'{total_rest_time} minute(s).'}, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'This exercise has no sets.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True)
    def highest_weight(self, request, pk=None):
        """
        Return the highest weight in the exerciseset
        """
        exercise = self.get_object()
        highest_weight = 0
        weight_unit = ''
        sets = exercise.set.all()
        if sets:
            for set in sets:
                highest_weight += set.weight
                weight_unit = set.weight_unit

            return Response({f'the highest weight in {exercise}': f'{highest_weight} {weight_unit}'})

        else:
            return Response({'error': 'This exercise has no weight'}, status=status.HTTP_404_NOT_FOUND)


class SetView(BaseViewTraining):
    """
    Manage set in database
    """
    queryset = Set.objects.all()
    serializer_class = serializers.SetSerializer

    filterset_fields = ['weight_unit']
