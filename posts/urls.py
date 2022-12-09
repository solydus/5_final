from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='home'),
    path('group/', views.group),
    path('group_post/', views.group),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<post_id>/edit/', views.post_edit,
         name='post_edit'),
    path('posts/<int:post_id>/', views.post_detail, name='posts_detail'),
    path('posts/<int:pk>/delete/', views.postdelete.as_view(),
         name='posts_delete'),
    path('create/', views.post_create, name='create'),
    path('posts/<int:post_id>/comment/', views.add_comment,
         name='add_comment'),
    path(
        'follow/',
        views.follow_index,
        name='follow_index'
    ),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
