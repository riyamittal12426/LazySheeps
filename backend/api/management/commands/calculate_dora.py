"""
Management command to calculate DORA metrics for all repositories
Run with: python manage.py calculate_dora
"""
from django.core.management.base import BaseCommand
from api.dora_metrics import calculate_dora_for_all_repositories


class Command(BaseCommand):
    help = 'Calculate DORA metrics for all repositories'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days to calculate metrics for (default: 90)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCalculating DORA metrics for all repositories (last {days} days)...\n'
            )
        )
        
        results = calculate_dora_for_all_repositories()
        
        # Print results
        success_count = 0
        for result in results:
            if result['success']:
                success_count += 1
                metrics = result['metrics']
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ {result['repository']}: "
                        f"DF={metrics['deployment_frequency']:.2f}/day, "
                        f"LT={metrics['lead_time_for_changes']:.2f}h, "
                        f"CFR={metrics['change_failure_rate']:.2f}%, "
                        f"MTTR={metrics['mttr']:.2f}h, "
                        f"Tier={metrics['performance_tier'].upper()}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ {result['repository']}: {result['error']}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Completed: {success_count}/{len(results)} repositories\n'
            )
        )
