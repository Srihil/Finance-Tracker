from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
  password  = serializers.CharField(
    write_only=True,
    required=True,
    validators=[validate_password], 
    style={'input_type': 'password'}
  )
  password2 = serializers.CharField(
    write_only=True,
    required=True,
    label='Confirm Password',
    style={'input_type': 'password'}
  )

  class Meta:
    model  = User
    fields = [
      'id', 'username', 'email',
      'password', 'password2',
      'first_name', 'last_name', 'phone'
    ]
    extra_kwargs = {
      'first_name': {'required': False},
      'last_name' : {'required': False},
      'phone'     : {'required': False},
    }

  def validate_email(self, value):
    if User.objects.filter(email=value.lower()).exists():
      raise serializers.ValidationError(
        "An account with this email already exists."
      )
    return value.lower()

  def validate_username(self, value):
    if len(value.strip()) < 3:
      raise serializers.ValidationError(
        "Username must be at least 3 characters."
      )
    if User.objects.filter(username=value).exists():
      raise serializers.ValidationError(
        "This username is already taken."
      )
    return value.strip()

  def validate(self, attrs):
    if attrs['password'] != attrs['password2']:
      raise serializers.ValidationError({
        'password': "Passwords do not match."
      })
    return attrs

  def create(self, validated_data):
    validated_data.pop('password2')
    user = User.objects.create_user(
      username   = validated_data['username'],
      email      = validated_data['email'],
      password   = validated_data['password'],
      first_name = validated_data.get('first_name', ''),
      last_name  = validated_data.get('last_name', ''),
      phone      = validated_data.get('phone', ''),
    )
    return user

class UserProfileSerializer(serializers.ModelSerializer):
  full_name = serializers.SerializerMethodField()

  class Meta:
    model  = User
    fields = [
      'id', 'username', 'email', 'first_name',
      'last_name', 'full_name', 'phone',
      'profile_picture', 'date_joined', 'created_at'
    ]
    read_only_fields = ['id', 'email', 'date_joined', 'created_at']

  def get_full_name(self, obj):
    full = f"{obj.first_name} {obj.last_name}".strip()
    return full if full else obj.username

class ChangePasswordSerializer(serializers.Serializer):
  old_password = serializers.CharField(
    required=True,
    write_only=True,
    style={'input_type': 'password'}
  )
  new_password = serializers.CharField(
    required=True,
    write_only=True,
    validators=[validate_password],
    style={'input_type': 'password'}
  )
  new_password2 = serializers.CharField(
    required=True,
    write_only=True,
    style={'input_type': 'password'}
  )

  def validate(self, attrs):
    if attrs['new_password'] != attrs['new_password2']:
      raise serializers.ValidationError({
        'new_password': "New passwords do not match."
      })
    return attrs

class LoginResponseSerializer(serializers.Serializer):
  access  = serializers.CharField()
  refresh = serializers.CharField()
  user    = UserProfileSerializer()