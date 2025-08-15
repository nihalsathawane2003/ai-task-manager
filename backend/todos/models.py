from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    priority_score = models.FloatField(default=0.0)  # 0-100
    deadline = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ContextEntry(models.Model):
    SOURCE_CHOICES = [
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("note", "Note"),
    ]
    content = models.TextField()
    source_type = models.CharField(max_length=16, choices=SOURCE_CHOICES)
    extracted_keywords = models.JSONField(default=list, blank=True)
    sentiment = models.CharField(max_length=16, blank=True)  # pos/neg/neu
    processed_insights = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_type} @ {self.created_at.isoformat()}"
