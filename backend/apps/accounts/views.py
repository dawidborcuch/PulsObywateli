from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.db import transaction

from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer, 
    UserUpdateSerializer, PasswordChangeSerializer, UserProfileSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """Rejestracja nowego użytkownika"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            # Generowanie tokenów JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh)
                },
                'message': 'Konto zostało utworzone pomyślnie'
            }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """Logowanie użytkownika"""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Logowanie użytkownika
        login(request, user)
        
        # Generowanie tokenów JWT
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Aktualizacja ostatniej aktywności
        if hasattr(user, 'profile'):
            user.profile.update_activity()
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh)
            },
            'message': 'Zalogowano pomyślnie'
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Profil użytkownika - wyświetlanie i edycja"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    """Aktualizacja danych użytkownika"""
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserProfileSettingsView(generics.RetrieveUpdateAPIView):
    """Ustawienia profilu użytkownika"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Zmiana hasła użytkownika"""
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    return Response({
        'message': 'Hasło zostało zmienione pomyślnie'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """Wylogowanie użytkownika"""
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Wylogowano pomyślnie'})
    except Exception as e:
        return Response({'error': 'Błąd podczas wylogowania'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Statystyki użytkownika"""
    user = request.user
    return Response({
        'votes_count': user.votes_count,
        'comments_count': user.comments_count,
        'member_since': user.created_at,
        'last_activity': user.profile.last_activity if hasattr(user, 'profile') else None,
    })

