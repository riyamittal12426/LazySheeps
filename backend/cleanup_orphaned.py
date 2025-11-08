import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Contributor

# Find and delete orphaned contributors
orphaned = Contributor.objects.filter(works__isnull=True)
count = orphaned.count()
print(f'Found {count} orphaned contributors')

if count > 0:
    orphaned.delete()
    print(f'✅ Deleted {count} orphaned contributors')
else:
    print('✅ No orphaned contributors found')
