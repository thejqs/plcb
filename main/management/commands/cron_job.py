from django.core.management.base import BaseCommand
import os, sys

sys.path.append("../../scripts")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

from main.models import Unicorn


class Command(BaseCommand):

    def handle(self, *args, **options):
        help = "Runs the daily PLCB scraper."
        # function call here.
