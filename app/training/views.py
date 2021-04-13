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

class SetView(BaseViewTraining):
    """
    Manage exerciseset in database
    """
    queryset = Set.objects.all()
    serializer_class = serializers.SetSerializer
