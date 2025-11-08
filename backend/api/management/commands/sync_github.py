"""
Django management command for running periodic GitHub sync
Usage: python manage.py sync_github
This should be run as a cron job every 15-30 minutes
"""
from django.core.management.base import BaseCommand
from api.github_sync import SyncJobRunner
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run periodic GitHub sync for all installations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if recently synced',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting periodic GitHub sync...'))
        
        try:
            result = SyncJobRunner.run_periodic_sync()
            
            self.stdout.write(self.style.SUCCESS(
                f"✅ Sync completed successfully:\n"
                f"   - Installations processed: {result['installations_processed']}\n"
                f"   - Repositories synced: {result['repositories_synced']}\n"
                f"   - Errors: {len(result['errors'])}"
            ))
            
            if result['errors']:
                self.stdout.write(self.style.WARNING('\n⚠️  Errors encountered:'))
                for error in result['errors']:
                    self.stdout.write(self.style.ERROR(f"   - {error}"))
            
            return result
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Sync failed: {str(e)}'))
            raise
