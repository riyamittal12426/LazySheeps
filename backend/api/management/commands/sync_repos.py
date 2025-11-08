"""
Sync imported repositories with latest GitHub data
"""
from django.core.management.base import BaseCommand
from api.models import Repository
from api.github_importer import GitHubImporter
from django.utils import timezone


class Command(BaseCommand):
    help = 'Sync all imported repositories with latest GitHub data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--repo-id',
            type=int,
            help='Sync specific repository by ID',
        )
        parser.add_argument(
            '--github-token',
            type=str,
            help='GitHub Personal Access Token (optional)',
        )

    def handle(self, *args, **options):
        repo_id = options.get('repo_id')
        github_token = options.get('github_token')
        
        if repo_id:
            repositories = Repository.objects.filter(id=repo_id)
            if not repositories.exists():
                self.stdout.write(self.style.ERROR(f'Repository with ID {repo_id} not found'))
                return
        else:
            repositories = Repository.objects.all()
        
        if not repositories.exists():
            self.stdout.write(self.style.WARNING('No repositories to sync'))
            return
        
        self.stdout.write(f'Syncing {repositories.count()} repositories...\n')
        
        importer = GitHubImporter(github_token)
        success_count = 0
        error_count = 0
        
        for repo in repositories:
            try:
                self.stdout.write(f'Syncing: {repo.name} ({repo.url})')
                
                # Re-import the repository (will update existing data)
                importer.import_repository(repo.url)
                
                repo.updated_at = timezone.now()
                repo.save()
                
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {repo.name} synced successfully'))
            
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Failed to sync {repo.name}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n{success_count} repositories synced successfully, {error_count} errors'
        ))
