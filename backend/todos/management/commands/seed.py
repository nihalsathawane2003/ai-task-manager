from django.core.management.base import BaseCommand
from todos.models import Category, Task, ContextEntry
from django.utils import timezone

class Command(BaseCommand):
    help = "Seed sample categories, tasks, and context"

    def handle(self, *args, **options):
        cat_names = ["General", "Bugs", "Urgent", "Writing", "Meetings"]
        for n in cat_names:
            Category.objects.get_or_create(name=n)
        ContextEntry.objects.create(content="Client: urgent fix needed by EOD", source_type="whatsapp")
        ContextEntry.objects.create(content="Email: Weekly report due Friday", source_type="email")
        t1 = Task.objects.create(
            title="Fix login bug",
            description="Users unable to login on mobile (error 500). Reproduce and fix.",
            category=Category.objects.get(name="Bugs"),
            priority_score=75.0
        )
        t2 = Task.objects.create(
            title="Prepare weekly report",
            description="Compile last week's metrics and send to stakeholders.",
            category=Category.objects.get(name="Writing"),
            priority_score=40.0
        )
        self.stdout.write(self.style.SUCCESS("Seeded sample categories, tasks, and context."))
