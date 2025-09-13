from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active and 
            request.user.role == 'Admin'
        )


class IsTaskAssignee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active and 
            obj.assigned_to == request.user
        )


class IsActiveUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active
        )


class CanCommentOnOwnTasks(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            return False
        
        if request.user.role == 'Admin':
            return True
        
        if request.method == 'POST':
            task_id = request.data.get('task')
            if task_id:
                from .models import Task
                try:
                    task = Task.objects.get(id=task_id)
                    return task.assigned_to == request.user
                except Task.DoesNotExist:
                    return False
        
        return True

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            return False
        
        if request.user.role == 'Admin':
            return True
        
        return obj.task.assigned_to == request.user