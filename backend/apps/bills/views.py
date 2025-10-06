from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, F
from django.utils import timezone
from datetime import timedelta

from .models import Bill, BillVote, BillUpdate
from .serializers import (
    BillSerializer, BillVoteSerializer, BillUpdateSerializer, 
    BillCreateSerializer, BillStatsSerializer
)


class BillListView(generics.ListAPIView):
    """Lista projektów ustaw z filtrowaniem i wyszukiwaniem"""
    serializer_class = BillSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_active', 'is_featured']
    search_fields = ['title', 'description', 'authors', 'tags']
    ordering_fields = ['submission_date', 'created_at', 'total_votes', 'support_votes']
    ordering = ['-submission_date']
    
    def get_queryset(self):
        queryset = Bill.objects.filter(is_active=True)
        
        # Filtrowanie po tagach
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__icontains=tag_list[0])
            for tag in tag_list[1:]:
                queryset = queryset.filter(tags__icontains=tag)
        
        # Filtrowanie po dacie
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(submission_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(submission_date__lte=date_to)
        
        return queryset


class BillDetailView(generics.RetrieveAPIView):
    """Szczegóły projektu ustawy"""
    serializer_class = BillSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Bill.objects.filter(is_active=True)


class BillVoteView(generics.CreateAPIView):
    """Głosowanie na projekt ustawy"""
    serializer_class = BillVoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['bill'] = self.get_bill()
        return context
    
    def get_bill(self):
        bill_id = self.kwargs.get('bill_id')
        return generics.get_object_or_404(Bill, id=bill_id, is_active=True)
    
    def create(self, request, *args, **kwargs):
        bill = self.get_bill()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Sprawdź czy użytkownik już głosował
        existing_vote = BillVote.objects.filter(user=request.user, bill=bill).first()
        
        if existing_vote:
            # Aktualizuj istniejący głos
            existing_vote.vote = serializer.validated_data['vote']
            existing_vote.save()
            message = 'Głos został zaktualizowany'
        else:
            # Utwórz nowy głos
            serializer.save()
            message = 'Głos został oddany'
        
        # Aktualizuj statystyki użytkownika
        request.user.votes_count = BillVote.objects.filter(user=request.user).count()
        request.user.save(update_fields=['votes_count'])
        
        return Response({
            'message': message,
            'bill': BillSerializer(bill, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class BillVoteDeleteView(generics.DestroyAPIView):
    """Usuwanie głosu na projekt ustawy"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        bill_id = self.kwargs.get('bill_id')
        bill = generics.get_object_or_404(Bill, id=bill_id, is_active=True)
        return generics.get_object_or_404(BillVote, user=self.request.user, bill=bill)
    
    def destroy(self, request, *args, **kwargs):
        vote = self.get_object()
        bill = vote.bill
        vote.delete()
        
        # Aktualizuj statystyki użytkownika
        request.user.votes_count = BillVote.objects.filter(user=request.user).count()
        request.user.save(update_fields=['votes_count'])
        
        return Response({
            'message': 'Głos został usunięty',
            'bill': BillSerializer(bill, context={'request': request}).data
        })


class BillCreateView(generics.CreateAPIView):
    """Tworzenie nowego projektu ustawy (dla adminów)"""
    serializer_class = BillCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class BillUpdateView(generics.UpdateAPIView):
    """Aktualizacja projektu ustawy (dla adminów)"""
    serializer_class = BillCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Bill.objects.all()
    
    def update(self, request, *args, **kwargs):
        bill = self.get_object()
        old_status = bill.status
        
        response = super().update(request, *args, **kwargs)
        
        # Jeśli status się zmienił, utwórz rekord aktualizacji
        if old_status != bill.status:
            BillUpdate.objects.create(
                bill=bill,
                old_status=old_status,
                new_status=bill.status,
                description=f"Status zmieniony z {old_status} na {bill.status}"
            )
        
        return response


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def bill_stats(request):
    """Statystyki projektów ustaw"""
    total_bills = Bill.objects.filter(is_active=True).count()
    active_bills = Bill.objects.filter(is_active=True, status__in=['submitted', 'in_committee', 'first_reading', 'second_reading', 'third_reading']).count()
    total_votes = BillVote.objects.count()
    
    # Najbardziej popierany projekt
    most_supported_bill = Bill.objects.filter(is_active=True).order_by('-support_votes').first()
    
    # Najbardziej kontrowersyjny projekt (najwięcej głosów przeciw)
    most_controversial_bill = Bill.objects.filter(is_active=True).order_by('-against_votes').first()
    
    # Rozkład statusów
    status_distribution = dict(Bill.objects.filter(is_active=True).values_list('status').annotate(count=Count('id')))
    
    # Ostatnie projekty
    recent_bills = Bill.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    stats_data = {
        'total_bills': total_bills,
        'active_bills': active_bills,
        'total_votes': total_votes,
        'most_supported_bill': BillSerializer(most_supported_bill, context={'request': request}).data if most_supported_bill else None,
        'most_controversial_bill': BillSerializer(most_controversial_bill, context={'request': request}).data if most_controversial_bill else None,
        'status_distribution': status_distribution,
        'recent_bills': BillSerializer(recent_bills, many=True, context={'request': request}).data
    }
    
    return Response(stats_data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_bills(request):
    """Wyróżnione projekty ustaw"""
    bills = Bill.objects.filter(is_active=True, is_featured=True).order_by('-created_at')
    serializer = BillSerializer(bills, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def trending_bills(request):
    """Trending projekty ustaw (najwięcej głosów w ostatnim tygodniu)"""
    week_ago = timezone.now() - timedelta(days=7)
    bills = Bill.objects.filter(
        is_active=True,
        votes__created_at__gte=week_ago
    ).annotate(
        recent_votes=Count('votes', filter=Q(votes__created_at__gte=week_ago))
    ).order_by('-recent_votes')[:10]
    
    serializer = BillSerializer(bills, many=True, context={'request': request})
    return Response(serializer.data)

