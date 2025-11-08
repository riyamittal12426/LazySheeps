"""
Clear all demo data from the database
"""
from django.core.management.base import BaseCommand
from api.models import (
    Repository, Contributor, RepositoryWork, 
    Commit, Issue, Badge, Collaboration, ActivityLog
)


class Command(BaseCommand):
    help = 'Clear all demo data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL data from the database. '
                    'Run with --confirm to proceed.'
                )
            )
            return

        self.stdout.write('Clearing all data...')

        # Delete in order to respect foreign key constraints
        counts = {}
        
        counts['ActivityLog'] = ActivityLog.objects.all().count()
        ActivityLog.objects.all().delete()
        
        counts['Collaboration'] = Collaboration.objects.all().count()
        Collaboration.objects.all().delete()
        
        counts['Badge'] = Badge.objects.all().count()
        Badge.objects.all().delete()
        
        counts['Issue'] = Issue.objects.all().count()
        Issue.objects.all().delete()
        
        counts['Commit'] = Commit.objects.all().count()
        Commit.objects.all().delete()
        
        counts['RepositoryWork'] = RepositoryWork.objects.all().count()
        RepositoryWork.objects.all().delete()
        
        counts['Contributor'] = Contributor.objects.all().count()
        Contributor.objects.all().delete()
        
        counts['Repository'] = Repository.objects.all().count()
        Repository.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('\nSuccessfully cleared all data:'))
        for model, count in counts.items():
            self.stdout.write(f'  - {model}: {count} deleted')
        
        self.stdout.write(self.style.SUCCESS('\nDatabase is now empty and ready for new imports!'))
