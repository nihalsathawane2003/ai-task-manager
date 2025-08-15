from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TaskViewSet, CategoryViewSet, ContextEntryViewSet, ai_suggest

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"context", ContextEntryViewSet, basename="context")

urlpatterns = [
    path("", include(router.urls)),
    path("ai/suggest/", ai_suggest, name="ai-suggest"),
]
