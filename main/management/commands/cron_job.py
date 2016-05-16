from django.core.management.base import BaseCommand
import os, sys

sys.path.append("../../..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

from main.models import Unicorn, Store
from main.scripts import pdf_multi_plcb_product_getter as pg

class Command(BaseCommand):

    def handle(self, *args, **options):
        help = "Runs the daily PLCB scraper."
        pg.hunt_unicorns()
