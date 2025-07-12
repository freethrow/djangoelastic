from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_article, name="add_article"),
    path("test/", views.test_search, name="test_search"),
    path("<str:article_id>/", views.detail, name="detail"),
]
