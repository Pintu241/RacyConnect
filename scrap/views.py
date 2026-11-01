from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from accounts.decorators import admin_required
from .models import ScrapCategory
from .forms import ScrapCategoryForm

def category_list_view(request):
    """Public scrap categories and live indicative rates page."""
    categories = ScrapCategory.objects.filter(is_active=True).order_by('order', 'name')
    search_query = request.GET.get('q', '')
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    return render(request, 'scrap/category_list.html', {
        'categories': categories,
        'search_query': search_query,
    })

def category_detail_view(request, slug):
    """Detailed view of a scrap category with rates and impact."""
    category = get_object_or_404(ScrapCategory, slug=slug, is_active=True)
    other_categories = ScrapCategory.objects.filter(is_active=True).exclude(id=category.id)[:4]
    return render(request, 'scrap/category_detail.html', {
        'category': category,
        'other_categories': other_categories,
    })

def api_get_rates(request):
    """API endpoint providing current rates for the scrap calculator."""
    categories = ScrapCategory.objects.filter(is_active=True).values(
        'id', 'name', 'base_rate_per_kg', 'min_rate_per_kg', 'max_rate_per_kg', 'unit', 'icon'
    )
    return JsonResponse({'categories': list(categories)})

@admin_required
def category_manage_list(request):
    categories = ScrapCategory.objects.all().order_by('order', 'name')
    return render(request, 'scrap/manage_list.html', {'categories': categories})

@admin_required
def category_create_view(request):
    if request.method == 'POST':
        form = ScrapCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Category '{cat.name}' added successfully.")
            return redirect('scrap:manage')
    else:
        form = ScrapCategoryForm()
    return render(request, 'scrap/category_form.html', {'form': form, 'title': 'Add New Scrap Category'})

@admin_required
def category_edit_view(request, pk):
    category = get_object_or_404(ScrapCategory, pk=pk)
    if request.method == 'POST':
        form = ScrapCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated.")
            return redirect('scrap:manage')
    else:
        form = ScrapCategoryForm(instance=category)
    return render(request, 'scrap/category_form.html', {'form': form, 'category': category, 'title': f'Edit Category: {category.name}'})
