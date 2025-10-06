from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone

from .models import Comment, CommentLike, CommentReport
from .serializers import (
    CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer,
    CommentLikeSerializer, CommentReportSerializer, CommentStatsSerializer
)


class CommentListView(generics.ListCreateAPIView):
    """Lista i tworzenie komentarzy do projektu ustawy"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        bill_id = self.kwargs.get('bill_id')
        return Comment.objects.filter(
            bill_id=bill_id,
            parent__isnull=True,  # Tylko główne komentarze
            is_approved=True
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == 'POST':
            from apps.bills.models import Bill
            context['bill'] = generics.get_object_or_404(Bill, id=self.kwargs.get('bill_id'))
        return context


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Szczegóły, edycja i usuwanie komentarza"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Comment.objects.filter(is_approved=True)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CommentUpdateSerializer
        return CommentSerializer
    
    def perform_update(self, serializer):
        # Sprawdź czy użytkownik może edytować komentarz
        if self.get_object().user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Nie możesz edytować tego komentarza")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Sprawdź czy użytkownik może usunąć komentarz
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Nie możesz usunąć tego komentarza")
        
        # Aktualizuj liczbę komentarzy użytkownika
        user = instance.user
        user.comments_count = Comment.objects.filter(user=user).count()
        user.save(update_fields=['comments_count'])
        
        # Jeśli to odpowiedź, aktualizuj liczbę odpowiedzi rodzica
        if instance.parent:
            instance.parent.update_replies_count()
        
        instance.delete()


class CommentLikeView(generics.CreateAPIView):
    """Polubienie/niepolubienie komentarza"""
    serializer_class = CommentLikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        comment_id = self.kwargs.get('comment_id')
        context['comment'] = generics.get_object_or_404(Comment, id=comment_id, is_approved=True)
        return context
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            serializer.save()
            message = 'Reakcja została zapisana'
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': message,
            'comment': CommentSerializer(
                serializer.instance.comment, 
                context={'request': request}
            ).data
        }, status=status.HTTP_201_CREATED)


class CommentLikeDeleteView(generics.DestroyAPIView):
    """Usuwanie polubienia komentarza"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        comment_id = self.kwargs.get('comment_id')
        comment = generics.get_object_or_404(Comment, id=comment_id, is_approved=True)
        return generics.get_object_or_404(CommentLike, user=self.request.user, comment=comment)
    
    def destroy(self, request, *args, **kwargs):
        like = self.get_object()
        comment = like.comment
        like.delete()
        
        return Response({
            'message': 'Reakcja została usunięta',
            'comment': CommentSerializer(comment, context={'request': request}).data
        })


class CommentReportView(generics.CreateAPIView):
    """Zgłaszanie komentarza"""
    serializer_class = CommentReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        comment_id = self.kwargs.get('comment_id')
        context['comment'] = generics.get_object_or_404(Comment, id=comment_id, is_approved=True)
        return context
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            serializer.save()
            message = 'Komentarz został zgłoszony'
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': message
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def comment_stats(request):
    """Statystyki komentarzy"""
    total_comments = Comment.objects.count()
    approved_comments = Comment.objects.filter(is_approved=True).count()
    pending_comments = Comment.objects.filter(is_approved=False).count()
    total_reports = CommentReport.objects.count()
    unresolved_reports = CommentReport.objects.filter(is_resolved=False).count()
    
    # Najczęściej komentowany projekt ustawy
    most_commented_bill = Comment.objects.values('bill__title', 'bill__number').annotate(
        comments_count=Count('id')
    ).order_by('-comments_count').first()
    
    # Ostatnie komentarze
    recent_comments = Comment.objects.filter(is_approved=True).order_by('-created_at')[:10]
    
    stats_data = {
        'total_comments': total_comments,
        'approved_comments': approved_comments,
        'pending_comments': pending_comments,
        'total_reports': total_reports,
        'unresolved_reports': unresolved_reports,
        'most_commented_bill': most_commented_bill,
        'recent_comments': CommentSerializer(recent_comments, many=True, context={'request': request}).data
    }
    
    return Response(stats_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_comments(request):
    """Komentarze użytkownika"""
    comments = Comment.objects.filter(user=request.user).order_by('-created_at')
    serializer = CommentSerializer(comments, many=True, context={'request': request})
    return Response(serializer.data)

