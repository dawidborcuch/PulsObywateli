from rest_framework import serializers
from .models import Poll, PollVote, PollComment


class PollSerializer(serializers.ModelSerializer):
    """Serializer do wyświetlania sondaży"""
    is_ongoing = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    results = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'description', 'poll_type', 'options', 'start_date', 'end_date',
            'is_active', 'is_featured', 'allow_multiple_votes', 'require_authentication',
            'total_votes', 'unique_voters', 'is_ongoing', 'is_expired', 'results',
            'tags', 'tags_list', 'created_at', 'updated_at', 'user_vote', 'comments_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_votes', 'unique_voters']
    
    def get_results(self, obj):
        return obj.get_results()
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                vote = obj.votes.get(user=request.user)
                return vote.selected_option
            except PollVote.DoesNotExist:
                return None
        return None
    
    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class PollVoteSerializer(serializers.ModelSerializer):
    """Serializer do głosowania w sondażu"""
    
    class Meta:
        model = PollVote
        fields = ['selected_option']
    
    def validate_selected_option(self, value):
        """Sprawdza czy wybrana opcja istnieje w sondażu"""
        poll = self.context['poll']
        if value not in poll.options:
            raise serializers.ValidationError("Wybrana opcja nie istnieje w tym sondażu")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        poll = self.context['poll']
        
        # Sprawdź czy użytkownik już głosował (jeśli nie pozwala na wielokrotne głosowanie)
        if not poll.allow_multiple_votes:
            existing_vote = PollVote.objects.filter(user=user, poll=poll).first()
            if existing_vote:
                raise serializers.ValidationError("Już głosowałeś w tym sondażu")
        
        # Dodaj informacje o głosującym
        vote = PollVote.objects.create(
            user=user,
            poll=poll,
            selected_option=validated_data['selected_option'],
            ip_address=self.context['request'].META.get('REMOTE_ADDR'),
            user_agent=self.context['request'].META.get('HTTP_USER_AGENT', ''),
        )
        
        return vote


class PollCommentSerializer(serializers.ModelSerializer):
    """Serializer do komentarzy w sondażach"""
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    
    class Meta:
        model = PollComment
        fields = ['id', 'content', 'user_nickname', 'user_avatar', 'is_approved', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_nickname', 'user_avatar', 'is_approved', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        user = self.context['request'].user
        poll = self.context['poll']
        
        comment = PollComment.objects.create(
            user=user,
            poll=poll,
            content=validated_data['content']
        )
        
        return comment


class PollCreateSerializer(serializers.ModelSerializer):
    """Serializer do tworzenia sondaży (dla adminów)"""
    
    class Meta:
        model = Poll
        fields = [
            'title', 'description', 'poll_type', 'options', 'start_date', 'end_date',
            'is_active', 'is_featured', 'allow_multiple_votes', 'require_authentication', 'tags'
        ]
    
    def validate_options(self, value):
        """Sprawdza czy opcje są prawidłowe"""
        if not isinstance(value, list) or len(value) < 2:
            raise serializers.ValidationError("Sondaż musi mieć co najmniej 2 opcje")
        if len(value) > 10:
            raise serializers.ValidationError("Sondaż może mieć maksymalnie 10 opcji")
        return value
    
    def validate(self, attrs):
        """Sprawdza czy data zakończenia jest po dacie rozpoczęcia"""
        if attrs['end_date'] <= attrs['start_date']:
            raise serializers.ValidationError("Data zakończenia musi być po dacie rozpoczęcia")
        return attrs


class PollStatsSerializer(serializers.Serializer):
    """Serializer do statystyk sondaży"""
    total_polls = serializers.IntegerField()
    active_polls = serializers.IntegerField()
    total_votes = serializers.IntegerField()
    most_popular_poll = PollSerializer()
    recent_polls = PollSerializer(many=True)
    poll_types_distribution = serializers.DictField()

