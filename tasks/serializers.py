from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Task, Comment
from users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ('id', 'task', 'author', 'content', 'created_at')
        read_only_fields = ('id', 'author', 'created_at')
        extra_kwargs = {
            'task': {'help_text': 'ID of the task this comment belongs to'},
            'content': {'help_text': 'Comment content'}
        }

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(
        write_only=True,
        help_text="ID of the user to assign this task to"
    )
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'assigned_to', 
            'assigned_to_id', 'created_at', 'updated_at', 'comments', 'comments_count'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = {
            'title': {'help_text': 'Task title'},
            'description': {'help_text': 'Detailed description of the task'},
            'status': {'help_text': 'Current status: ToDo, InProgress, or Done'}
        }

    @extend_schema_field(serializers.IntegerField)
    def get_comments_count(self, obj):
        return obj.comments.count()