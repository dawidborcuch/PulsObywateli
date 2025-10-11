from django.urls import path
from . import views

urlpatterns = [
    path('', views.BillListView.as_view(), name='bill-list'),
    path('<int:id>/', views.BillDetailView.as_view(), name='bill-detail'),
    path('<int:bill_id>/vote/', views.BillVoteView.as_view(), name='bill-vote'),
    path('<int:bill_id>/vote/delete/', views.BillVoteDeleteView.as_view(), name='bill-vote-delete'),
    path('create/', views.BillCreateView.as_view(), name='bill-create'),
    path('<int:id>/update/', views.BillUpdateView.as_view(), name='bill-update'),
    path('stats/', views.bill_stats, name='bill-stats'),
    path('featured/', views.featured_bills, name='featured-bills'),
    path('trending/', views.trending_bills, name='trending-bills'),
    path('<int:bill_id>/ai-analysis/generate/', views.generate_ai_analysis, name='generate-ai-analysis'),
    path('<int:bill_id>/ai-analysis/', views.get_ai_analysis, name='get-ai-analysis'),
]

