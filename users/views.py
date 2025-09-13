from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'soft_delete':
            self.permission_classes = [permissions.IsAuthenticated]
            # Add custom permission check in the action itself
        else:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    @action(detail=True, methods=['patch'])
    def soft_delete(self, request, pk=None):
        # Check if user is admin
        if request.user.role != 'Admin':
            return Response(
                {'error': 'Only admins can soft delete users'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        user.is_active = False
        user.save()
        
        return Response({
            'message': f'User {user.email} has been soft deleted'
        }, status=status.HTTP_200_OK)