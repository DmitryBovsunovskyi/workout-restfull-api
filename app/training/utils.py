from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions, viewsets
from training import serializers
from training import models

class BaseViewTraining(viewsets.ModelViewSet):
    """
    Base view class for training.models to manage objects in database
    """
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Create a new object
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Restrict data to be seen by its owner,
        allowing admin to see full data
        """
        if self.request.user.is_superuser:
            return self.queryset

        return self.queryset.filter(user=self.request.user)
