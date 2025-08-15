# todos/management/commands/test_ai.py
from django.core.management.base import BaseCommand
import google.generativeai as genai
import os
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

class Command(BaseCommand):
    help = "Test Gemini AI integration"

    def handle(self, *args, **kwargs):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.stdout.write(self.style.ERROR("GOOGLE_API_KEY is not set"))
            return

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(["Hello, AI! Can you help me?"])

        self.stdout.write(self.style.SUCCESS("AI Response:"))
        self.stdout.write(response.text)
