from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import Poll, PollVote, PollComment
from .serializers import (
    PollSerializer, PollVoteSerializer, PollCommentSerializer, 
    PollCreateSerializer, PollStatsSerializer
)


class PollListView(generics.ListAPIView):
    """Lista sondaży z filtrowaniem i wyszukiwaniem"""
    serializer_class = PollSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['poll_type', 'is_active', 'is_featured']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['start_date', 'end_date', 'total_votes', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Poll.objects.filter(is_active=True)
        
        # Filtrowanie po statusie
        status_filter = self.request.query_params.get('status')
        now = timezone.now()
        
        if status_filter == 'ongoing':
            queryset = queryset.filter(start_date__lte=now, end_date__gte=now)
        elif status_filter == 'upcoming':
            queryset = queryset.filter(start_date__gt=now)
        elif status_filter == 'expired':
            queryset = queryset.filter(end_date__lt=now)
        
        # Filtrowanie po tagach
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__icontains=tag_list[0])
            for tag in tag_list[1:]:
                queryset = queryset.filter(tags__icontains=tag)
        
        return queryset


class PollDetailView(generics.RetrieveAPIView):
    """Szczegóły sondażu"""
    serializer_class = PollSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Poll.objects.filter(is_active=True)


class PollVoteView(generics.CreateAPIView):
    """Głosowanie w sondażu"""
    serializer_class = PollVoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['poll'] = self.get_poll()
        return context
    
    def get_poll(self):
        poll_id = self.kwargs.get('poll_id')
        return generics.get_object_or_404(Poll, id=poll_id, is_active=True)
    
    def create(self, request, *args, **kwargs):
        poll = self.get_poll()
        
        # Sprawdź czy sondaż jest aktywny
        if not poll.is_ongoing:
            return Response({
                'error': 'Sondaż nie jest obecnie aktywny'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            serializer.save()
            message = 'Głos został oddany pomyślnie'
        except serializers.ValidationError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': message,
            'poll': PollSerializer(poll, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class PollVoteDeleteView(generics.DestroyAPIView):
    """Usuwanie głosu w sondażu"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        poll_id = self.kwargs.get('poll_id')
        poll = generics.get_object_or_404(Poll, id=poll_id, is_active=True)
        return generics.get_object_or_404(PollVote, user=self.request.user, poll=poll)
    
    def destroy(self, request, *args, **kwargs):
        vote = self.get_object()
        poll = vote.poll
        vote.delete()
        
        return Response({
            'message': 'Głos został usunięty',
            'poll': PollSerializer(poll, context={'request': request}).data
        })


class PollCommentListView(generics.ListCreateAPIView):
    """Lista i tworzenie komentarzy do sondażu"""
    serializer_class = PollCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        poll_id = self.kwargs.get('poll_id')
        return PollComment.objects.filter(
            poll_id=poll_id, 
            is_approved=True
        ).order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['poll'] = generics.get_object_or_404(Poll, id=self.kwargs.get('poll_id'))
        return context


class PollCreateView(generics.CreateAPIView):
    """Tworzenie nowego sondażu (dla adminów)"""
    serializer_class = PollCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class PollUpdateView(generics.UpdateAPIView):
    """Aktualizacja sondażu (dla adminów)"""
    serializer_class = PollCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Poll.objects.all()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def poll_stats(request):
    """Statystyki sondaży"""
    total_polls = Poll.objects.filter(is_active=True).count()
    active_polls = Poll.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).count()
    total_votes = PollVote.objects.count()
    
    # Najpopularniejszy sondaż
    most_popular_poll = Poll.objects.filter(is_active=True).order_by('-total_votes').first()
    
    # Ostatnie sondaże
    recent_polls = Poll.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    # Rozkład typów sondaży
    poll_types_distribution = dict(
        Poll.objects.filter(is_active=True)
        .values_list('poll_type')
        .annotate(count=Count('id'))
    )
    
    stats_data = {
        'total_polls': total_polls,
        'active_polls': active_polls,
        'total_votes': total_votes,
        'most_popular_poll': PollSerializer(most_popular_poll, context={'request': request}).data if most_popular_poll else None,
        'recent_polls': PollSerializer(recent_polls, many=True, context={'request': request}).data,
        'poll_types_distribution': poll_types_distribution
    }
    
    return Response(stats_data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_polls(request):
    """Wyróżnione sondaże"""
    polls = Poll.objects.filter(is_active=True, is_featured=True).order_by('-created_at')
    serializer = PollSerializer(polls, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def trending_polls(request):
    """Trending sondaże (najwięcej głosów w ostatnim tygodniu)"""
    week_ago = timezone.now() - timedelta(days=7)
    polls = Poll.objects.filter(
        is_active=True,
        votes__created_at__gte=week_ago
    ).annotate(
        recent_votes=Count('votes', filter=Q(votes__created_at__gte=week_ago))
    ).order_by('-recent_votes')[:10]
    
    serializer = PollSerializer(polls, many=True, context={'request': request})
    return Response(serializer.data)

