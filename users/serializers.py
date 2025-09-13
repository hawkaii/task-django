from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.openapi import OpenApiExample

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        help_text="Password must meet security requirements"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Must match the password field"
    )

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password', 'password_confirm', 'role')
        extra_kwargs = {
            'email': {'help_text': 'Valid email address'},
            'full_name': {'help_text': 'User\'s full name'},
            'role': {'help_text': 'User role: Admin or User'}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'role', 'date_joined', 'is_active')
        read_only_fields = ('id', 'date_joined')
        extra_kwargs = {
            'email': {'help_text': 'User\'s email address'},
            'full_name': {'help_text': 'User\'s full name'},
            'role': {'help_text': 'User role: Admin or User'},
            'is_active': {'help_text': 'Whether the user account is active'}
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not self.user:
            raise serializers.ValidationError('Invalid email or password.')
        
        if not self.user.is_active:
            raise serializers.ValidationError('User account has been deactivated.')

        data = {}
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data