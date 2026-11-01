from scrap.models import ScrapCategory

def global_context(request):
    """Provides common global context variables to all templates."""
    categories = []
    try:
        categories = ScrapCategory.objects.filter(is_active=True)[:6]
    except Exception:
        pass
    
    return {
        'site_name': 'RecyConnect',
        'site_tagline': 'Connecting Collectors. Empowering Recycling. Building a Greener Future.',
        'global_categories': categories,
    }
