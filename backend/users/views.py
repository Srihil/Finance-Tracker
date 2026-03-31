from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model, authenticate

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


def get_tokens_for_user(user):
    """
    Creates a JWT refresh + access token pair for the given user.
    Called after register and login.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access' : str(refresh.access_token),
    }

class RegisterView(APIView):
    """
    Public endpoint — no authentication required.
    Creates a new user and returns JWT tokens immediately
    so the user is logged in right after registering.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user   = serializer.save()
            tokens = get_tokens_for_user(user)

            return Response(
                {
                    'message': 'Account created successfully!',
                    'user'   : UserProfileSerializer(user).data,
                    'tokens' : tokens,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

# ============================================================
# LOGIN VIEW
# POST /api/auth/login/
# ============================================================
class LoginView(APIView):
    """
    Public endpoint — no authentication required.
    Accepts email + password, returns JWT tokens on success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email    = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '')

        # Basic validation
        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ FIX: Since USERNAME_FIELD = 'email' in our User model,
        # authenticate() expects the email directly as username parameter
        user = authenticate(
            request,
            username=email,   # ← pass email here, NOT user_obj.username
            password=password
        )

        if user is None:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'This account has been deactivated.'},
                status=status.HTTP_403_FORBIDDEN
            )

        tokens = get_tokens_for_user(user)

        return Response(
            {
                'message': 'Login successful!',
                'user'   : UserProfileSerializer(user).data,
                'tokens' : tokens,
            },
            status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    """
    Protected endpoint — requires valid JWT token.
    Returns the currently logged-in user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class ProfileUpdateView(APIView):
    """
    Protected endpoint — requires valid JWT token.
    Allows updating first_name, last_name, phone, profile_picture.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True 
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Profile updated successfully!',
                    'user'   : serializer.data,
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class ChangePasswordView(APIView):
    """
    Protected endpoint.
    User must provide their old password to set a new one.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Old password is incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            tokens = get_tokens_for_user(user)

            return Response(
                {
                    'message': 'Password changed successfully!',
                    'tokens' : tokens,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class LogoutView(APIView):
    """
    Protected endpoint.
    Blacklists the refresh token so it can't be used again.
    The frontend should also delete the stored token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Logged out successfully!'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'message': 'Logged out successfully!'},
                status=status.HTTP_200_OK
            )