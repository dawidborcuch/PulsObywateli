from django.urls import path
from . import views

urlpatterns = [
    path('bills/<int:bill_id>/', views.CommentListView.as_view(), name='comment-list'),
    path('<int:id>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('<int:comment_id>/like/', views.CommentLikeView.as_view(), name='comment-like'),
    path('<int:comment_id>/like/delete/', views.CommentLikeDeleteView.as_view(), name='comment-like-delete'),
    path('<int:comment_id>/report/', views.CommentReportView.as_view(), name='comment-report'),
    path('stats/', views.comment_stats, name='comment-stats'),
    path('user/', views.user_comments, name='user-comments'),
]

