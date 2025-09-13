from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from drf_spectacular.openapi import OpenApiParameter
from .serializers import UserRegistrationSerializer, UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()


@extend_schema(
    summary="Obtain JWT token pair",
    description="Login with email and password to obtain access and refresh tokens",
    examples=[
        OpenApiExample(
            'Login Example',
            value={
                'email': 'admin@example.com',
                'password': 'password123'
            }
        )
    ]
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    summary="Register new user",
    description="Create a new user account with email and password",
    examples=[
        OpenApiExample(
            'Registration Example',
            value={
                'email': 'user@example.com',
                'password': 'securepassword123',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'User'
            }
        )
    ]
)
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


@extend_schema(
    summary="List all users",
    description="Get a list of all users (Admin only)"
)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema_view(
    list=extend_schema(
        summary="List users",
        description="Get a paginated list of all users (Admin only)"
    ),
    retrieve=extend_schema(
        summary="Get user details",
        description="Retrieve details of a specific user (Admin only)"
    ),
    create=extend_schema(
        summary="Create user",
        description="Create a new user (Admin only)"
    ),
    update=extend_schema(
        summary="Update user",
        description="Update all fields of a user (Admin only)"
    ),
    partial_update=extend_schema(
        summary="Partial update user",
        description="Update specific fields of a user (Admin only)"
    ),
    destroy=extend_schema(
        summary="Delete user",
        description="Permanently delete a user (Admin only)"
    ),
    soft_delete=extend_schema(
        summary="Soft delete user",
        description="Deactivate a user without removing their data (Admin only)",
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    'message': 'User user@example.com has been soft deleted'
                }
            )
        ]
    )
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'soft_delete':
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    @action(detail=True, methods=['patch'])
    def soft_delete(self, request, pk=None):
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