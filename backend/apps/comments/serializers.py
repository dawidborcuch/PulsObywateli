from rest_framework import serializers
from .models import Comment, CommentLike, CommentReport


class CommentSerializer(serializers.ModelSerializer):
    """Serializer do wyświetlania komentarzy"""
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    replies = serializers.SerializerMethodField()
    user_like = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'user_nickname', 'user_avatar', 'is_approved', 'is_edited',
            'likes_count', 'dislikes_count', 'replies_count', 'created_at', 'updated_at',
            'replies', 'user_like'
        ]
        read_only_fields = [
            'id', 'user_nickname', 'user_avatar', 'is_approved', 'is_edited',
            'likes_count', 'dislikes_count', 'replies_count', 'created_at', 'updated_at'
        ]
    
    def get_replies(self, obj):
        """Zwraca odpowiedzi do komentarza"""
        replies = obj.replies.filter(is_approved=True).order_by('created_at')
        return CommentSerializer(replies, many=True, context=self.context).data
    
    def get_user_like(self, obj):
        """Zwraca czy użytkownik polubił komentarz"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                like = obj.likes.get(user=request.user)
                return 'like' if like.is_like else 'dislike'
            except CommentLike.DoesNotExist:
                return None
        return None


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer do tworzenia komentarzy"""
    
    class Meta:
        model = Comment
        fields = ['content', 'parent']
    
    def create(self, validated_data):
        user = self.context['request'].user
        bill = self.context['bill']
        
        comment = Comment.objects.create(
            user=user,
            bill=bill,
            content=validated_data['content'],
            parent=validated_data.get('parent')
        )
        
        # Aktualizuj liczbę komentarzy użytkownika
        user.comments_count = Comment.objects.filter(user=user).count()
        user.save(update_fields=['comments_count'])
        
        # Jeśli to odpowiedź, aktualizuj liczbę odpowiedzi rodzica
        if comment.parent:
            comment.parent.update_replies_count()
        
        return comment


class CommentUpdateSerializer(serializers.ModelSerializer):
    """Serializer do aktualizacji komentarzy"""
    
    class Meta:
        model = Comment
        fields = ['content']
    
    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.is_edited = True
        instance.save()
        return instance


class CommentLikeSerializer(serializers.ModelSerializer):
    """Serializer do polubień komentarzy"""
    
    class Meta:
        model = CommentLike
        fields = ['is_like']
    
    def create(self, validated_data):
        user = self.context['request'].user
        comment = self.context['comment']
        
        # Sprawdź czy użytkownik już polubił/nie polubił
        like, created = CommentLike.objects.get_or_create(
            user=user,
            comment=comment,
            defaults={'is_like': validated_data['is_like']}
        )
        
        if not created:
            like.is_like = validated_data['is_like']
            like.save()
        
        return like


class CommentReportSerializer(serializers.ModelSerializer):
    """Serializer do zgłaszania komentarzy"""
    
    class Meta:
        model = CommentReport
        fields = ['reason', 'description']
    
    def create(self, validated_data):
        user = self.context['request'].user
        comment = self.context['comment']
        
        # Sprawdź czy użytkownik już zgłosił ten komentarz
        report, created = CommentReport.objects.get_or_create(
            user=user,
            comment=comment,
            defaults={
                'reason': validated_data['reason'],
                'description': validated_data.get('description', '')
            }
        )
        
        if not created:
            report.reason = validated_data['reason']
            report.description = validated_data.get('description', '')
            report.save()
        
        return report


class CommentStatsSerializer(serializers.Serializer):
    """Serializer do statystyk komentarzy"""
    total_comments = serializers.IntegerField()
    approved_comments = serializers.IntegerField()
    pending_comments = serializers.IntegerField()
    total_reports = serializers.IntegerField()
    unresolved_reports = serializers.IntegerField()
    most_commented_bill = serializers.DictField()
    recent_comments = CommentSerializer(many=True)

