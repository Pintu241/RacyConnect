from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from scrap.models import ScrapCategory
from pickups.models import PickupRequest
from transactions.models import Transaction
from accounts.models import User, CollectorProfile
from .models import Complaint, ContactMessage
from .forms import ContactForm, ComplaintForm

def home_view(request):
    categories = ScrapCategory.objects.filter(is_active=True).order_by('order', 'name')
    
    # Impact stats
    total_recycled_kg = Transaction.objects.aggregate(Sum('actual_weight'))['actual_weight__sum'] or 2480
    total_pickups_count = PickupRequest.objects.filter(status=PickupRequest.STATUS_COMPLETED).count() or 45
    total_collectors_count = CollectorProfile.objects.filter(is_verified=True).count() or 18
    co2_saved_kg = round(float(total_recycled_kg) * 1.85, 1)

    context = {
        'categories': categories,
        'total_recycled_kg': total_recycled_kg,
        'total_pickups_count': total_pickups_count,
        'total_collectors_count': total_collectors_count,
        'co2_saved_kg': co2_saved_kg,
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    return render(request, 'core/about.html')


def how_it_works_view(request):
    return render(request, 'core/how_it_works.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for reaching out! Our sustainability team will contact you shortly.")
            return redirect('core:contact')
        else:
            messages.error(request, "Please check the form fields.")
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})


def privacy_view(request):
    return render(request, 'core/privacy.html')


def terms_view(request):
    return render(request, 'core/terms.html')


@login_required
def complaint_view(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, user=request.user)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, f"Complaint #{complaint.id} logged. Our support team will investigate and respond soon.")
            return redirect('dashboard:index')
        else:
            messages.error(request, "Please fix the form errors.")
    else:
        form = ComplaintForm(user=request.user)
    return render(request, 'core/complaint.html', {'form': form})
