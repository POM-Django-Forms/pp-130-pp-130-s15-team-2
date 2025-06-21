import os
import django

def setup_site():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')
    django.setup()
    
    from django.contrib.sites.models import Site
    from django.conf import settings
    
    site = Site.objects.get_or_create(pk=settings.SITE_ID)[0]
    site.name = 'Library Management System'
    site.domain = 'localhost:8000'  # Update this in production
    site.save()
    print(f"Site set up: {site.domain}")

if __name__ == "__main__":
    setup_site()
