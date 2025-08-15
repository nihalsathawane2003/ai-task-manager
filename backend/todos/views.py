from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task, Category, ContextEntry
from .serializers import TaskSerializer, CategorySerializer, ContextEntrySerializer
from .ai.engine import suggest_for_task

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-priority_score", "deadline")
    serializer_class = TaskSerializer

    # Optional: allow partial filter via query params handled by get_queryset override
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("search")
        status_q = self.request.query_params.get("status")
        cat = self.request.query_params.get("category")
        minp = self.request.query_params.get("min_priority")
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(description__icontains=q)
        if status_q:
            qs = qs.filter(status=status_q)
        if cat:
            qs = qs.filter(category__name__iexact=cat)
        if minp:
            try:
                minpf = float(minp)
                qs = qs.filter(priority_score__gte=minpf)
            except:
                pass
        return qs

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("-usage_count")
    serializer_class = CategorySerializer

class ContextEntryViewSet(viewsets.ModelViewSet):
    queryset = ContextEntry.objects.all().order_by("-created_at")
    serializer_class = ContextEntrySerializer

@api_view(["POST"])
def ai_suggest(request):
    payload = request.data or {}
    try:
        suggestion = suggest_for_task(payload)
        return Response(suggestion, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
