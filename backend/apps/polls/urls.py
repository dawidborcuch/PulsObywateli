from django.urls import path
from . import views

urlpatterns = [
    path('', views.PollListView.as_view(), name='poll-list'),
    path('<int:id>/', views.PollDetailView.as_view(), name='poll-detail'),
    path('<int:poll_id>/vote/', views.PollVoteView.as_view(), name='poll-vote'),
    path('<int:poll_id>/vote/delete/', views.PollVoteDeleteView.as_view(), name='poll-vote-delete'),
    path('<int:poll_id>/comments/', views.PollCommentListView.as_view(), name='poll-comments'),
    path('create/', views.PollCreateView.as_view(), name='poll-create'),
    path('<int:id>/update/', views.PollUpdateView.as_view(), name='poll-update'),
    path('stats/', views.poll_stats, name='poll-stats'),
    path('featured/', views.featured_polls, name='featured-polls'),
    path('trending/', views.trending_polls, name='trending-polls'),
]

