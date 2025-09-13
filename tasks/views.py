from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer
from .permissions import IsAdmin, IsTaskAssignee, IsActiveUser, CanCommentOnOwnTasks


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'assigned_to']
    search_fields = ['title', 'description']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsAdmin]
        else:
            self.permission_classes = [IsActiveUser]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.role == 'Admin':
            return Task.objects.all()
        else:
            return Task.objects.filter(assigned_to=self.request.user)

    def check_object_permissions(self, request, obj):
        if request.user.role == 'Admin':
            return super().check_object_permissions(request, obj)
        
        if self.action in ['retrieve', 'update', 'partial_update']:
            if obj.assigned_to != request.user:
                self.permission_denied(request, message="You can only access your own tasks.")
        
        return super().check_object_permissions(request, obj)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [CanCommentOnOwnTasks]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task']

    def get_queryset(self):
        if self.request.user.role == 'Admin':
            return Comment.objects.all()
        else:
            return Comment.objects.filter(task__assigned_to=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)