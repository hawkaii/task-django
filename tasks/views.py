from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter
from .models import Task, Comment
from .serializers import TaskSerializer, CommentSerializer
from .permissions import IsAdmin, IsTaskAssignee, IsActiveUser, CanCommentOnOwnTasks


@extend_schema_view(
    list=extend_schema(
        summary="List tasks",
        description="Get a paginated list of tasks. Admins see all tasks, users see only their assigned tasks.",
        parameters=[
            OpenApiParameter(name='status', description='Filter by task status'),
            OpenApiParameter(name='assigned_to', description='Filter by assigned user ID'),
            OpenApiParameter(name='search', description='Search in title and description'),
        ]
    ),
    retrieve=extend_schema(
        summary="Get task details",
        description="Retrieve details of a specific task"
    ),
    create=extend_schema(
        summary="Create task",
        description="Create a new task (Admin only)",
        examples=[
            OpenApiExample(
                'Create Task Example',
                value={
                    'title': 'Implement user authentication',
                    'description': 'Add JWT-based authentication to the API',
                    'status': 'ToDo',
                    'assigned_to': 1
                }
            )
        ]
    ),
    update=extend_schema(
        summary="Update task",
        description="Update all fields of a task"
    ),
    partial_update=extend_schema(
        summary="Partial update task",
        description="Update specific fields of a task"
    ),
    destroy=extend_schema(
        summary="Delete task",
        description="Permanently delete a task (Admin only)"
    )
)
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


@extend_schema_view(
    list=extend_schema(
        summary="List comments",
        description="Get a list of comments. Admins see all comments, users see only comments on their assigned tasks.",
        parameters=[
            OpenApiParameter(name='task', description='Filter by task ID'),
        ]
    ),
    retrieve=extend_schema(
        summary="Get comment details",
        description="Retrieve details of a specific comment"
    ),
    create=extend_schema(
        summary="Create comment",
        description="Add a comment to a task you have access to",
        examples=[
            OpenApiExample(
                'Create Comment Example',
                value={
                    'task': 1,
                    'content': 'I\'ve started working on this task and will update progress soon.'
                }
            )
        ]
    ),
    update=extend_schema(
        summary="Update comment",
        description="Update all fields of a comment you authored"
    ),
    partial_update=extend_schema(
        summary="Partial update comment",
        description="Update specific fields of a comment you authored"
    ),
    destroy=extend_schema(
        summary="Delete comment",
        description="Delete a comment you authored"
    )
)
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