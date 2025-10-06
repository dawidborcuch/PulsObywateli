from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer do rejestracji użytkownika"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'nickname', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'nickname': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Hasła nie są identyczne")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Tworzenie profilu użytkownika
        UserProfile.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer do logowania użytkownika"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Nieprawidłowe dane logowania')
            if not user.is_active:
                raise serializers.ValidationError('Konto jest nieaktywne')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Musisz podać email i hasło')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer do profilu użytkownika"""
    class Meta:
        model = UserProfile
        fields = ('email_notifications', 'newsletter', 'theme', 'last_activity', 'total_votes', 'total_comments')
        read_only_fields = ('last_activity', 'total_votes', 'total_comments')


class UserSerializer(serializers.ModelSerializer):
    """Serializer do wyświetlania danych użytkownika"""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'nickname', 'first_name', 'last_name', 
            'full_name', 'avatar', 'bio', 'is_verified', 'created_at', 
            'votes_count', 'comments_count', 'profile'
        )
        read_only_fields = ('id', 'created_at', 'votes_count', 'comments_count', 'is_verified')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer do aktualizacji danych użytkownika"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'nickname', 'avatar', 'bio')
    
    def validate_nickname(self, value):
        """Sprawdza czy pseudonim jest unikalny"""
        if User.objects.filter(nickname=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('Ten pseudonim jest już zajęty')
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer do zmiany hasła"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Nowe hasła nie są identyczne")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Nieprawidłowe obecne hasło')
        return value

