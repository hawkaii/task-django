from rest_framework import serializers
from .models import Task, Comment
from users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ('id', 'task', 'author', 'content', 'created_at')
        read_only_fields = ('id', 'author', 'created_at')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'assigned_to', 
            'assigned_to_id', 'created_at', 'updated_at', 'comments', 'comments_count'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_comments_count(self, obj):
        return obj.comments.count()