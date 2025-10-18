from rest_framework import serializers
from .models import Bill, BillVote, ClubColor, BillUpdate


class BillSerializer(serializers.ModelSerializer):
    """Serializer do wyświetlania projektów ustaw"""
    support_percentage = serializers.ReadOnlyField()
    against_percentage = serializers.ReadOnlyField()
    neutral_percentage = serializers.ReadOnlyField()
    tags_list = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = [
            'id', 'title', 'description', 'number', 'status', 'authors', 'initiators',
            'submission_date', 'source_url', 'document_url', 'support_votes', 'against_votes',
            'neutral_votes', 'total_votes', 'support_percentage', 'against_percentage',
            'neutral_percentage', 'is_active', 'is_featured', 'tags', 'tags_list',
            'project_type', 'data_source', 'sejm_id', 'eli', 'passed',
            'full_text', 'attachments', 'attachment_files', 'ai_analysis', 'ai_analysis_date',
            'voting_date', 'voting_number', 'session_number', 'voting_topic', 'voting_results', 'club_results', 'druk_numbers',
            'created_at', 'updated_at', 'user_vote'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'support_votes', 'against_votes', 'neutral_votes', 'total_votes']
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                vote = obj.votes.get(user=request.user)
                return vote.vote
            except BillVote.DoesNotExist:
                return None
        return None


class BillVoteSerializer(serializers.ModelSerializer):
    """Serializer do głosowania na projekty ustaw"""
    
    class Meta:
        model = BillVote
        fields = ['vote']
    
    def create(self, validated_data):
        user = self.context['request'].user
        bill = self.context['bill']
        
        # Sprawdź czy użytkownik już głosował
        vote, created = BillVote.objects.get_or_create(
            user=user,
            bill=bill,
            defaults={'vote': validated_data['vote']}
        )
        
        if not created:
            vote.vote = validated_data['vote']
            vote.save()
        
        return vote


class BillUpdateSerializer(serializers.ModelSerializer):
    """Serializer do aktualizacji projektów ustaw"""
    
    class Meta:
        model = BillUpdate
        fields = ['old_status', 'new_status', 'description', 'created_at']
        read_only_fields = ['created_at']


class BillCreateSerializer(serializers.ModelSerializer):
    """Serializer do tworzenia nowych projektów ustaw (dla adminów)"""
    
    class Meta:
        model = Bill
        fields = [
            'title', 'description', 'number', 'status', 'authors', 'initiators',
            'submission_date', 'source_url', 'document_url', 'is_active', 'is_featured', 'tags'
        ]


class BillStatsSerializer(serializers.Serializer):
    """Serializer do statystyk projektów ustaw"""
    total_bills = serializers.IntegerField()
    active_bills = serializers.IntegerField()
    total_votes = serializers.IntegerField()
    most_supported_bill = BillSerializer()
    most_controversial_bill = BillSerializer()
    status_distribution = serializers.DictField()
    recent_bills = BillSerializer(many=True)


class ClubColorSerializer(serializers.ModelSerializer):
    """Serializer do zarządzania kolorami klubów"""
    
    class Meta:
        model = ClubColor
        fields = ['id', 'club_name', 'color_hex', 'color_name', 'is_active', 'created_at', 'updated_at']

