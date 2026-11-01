from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from accounts.decorators import (
    customer_required,
    collector_required,
    recycler_required,
    admin_required
)
from accounts.models import User, CollectorProfile, RecyclerProfile
from pickups.models import PickupRequest
from transactions.models import Transaction
from recyclers.models import PurchaseRequest
from scrap.models import ScrapCategory
from core.models import Complaint

@login_required
def dashboard_index(request):
    """Dispatches the authenticated user to their role-specific dashboard."""
    user = request.user
    if user.is_platform_admin:
        return redirect('dashboard:admin')
    elif user.is_collector:
        return redirect('dashboard:collector')
    elif user.is_recycler:
        return redirect('dashboard:recycler')
    else:
        return redirect('dashboard:customer')


@customer_required
def customer_dashboard(request):
    user = request.user
    pickups = PickupRequest.objects.filter(customer=user)
    transactions = Transaction.objects.filter(customer=user)

    total_pickups = pickups.count()
    completed_pickups = pickups.filter(status=PickupRequest.STATUS_COMPLETED).count()
    active_pickups_list = pickups.filter(status__in=[
        PickupRequest.STATUS_PENDING,
        PickupRequest.STATUS_ACCEPTED,
        PickupRequest.STATUS_IN_PROGRESS
    ]).order_by('-created_at')

    total_weight = transactions.aggregate(Sum('actual_weight'))['actual_weight__sum'] or 0
    total_earned = transactions.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    recent_completed = pickups.filter(status=PickupRequest.STATUS_COMPLETED).order_by('-updated_at')[:5]

    context = {
        'total_pickups': total_pickups,
        'completed_pickups': completed_pickups,
        'total_weight': total_weight,
        'total_earned': total_earned,
        'active_pickups': active_pickups_list,
        'recent_completed': recent_completed,
    }
    return render(request, 'dashboard/customer_dashboard.html', context)


@collector_required
def collector_dashboard(request):
    user = request.user
    profile = getattr(user, 'collector_profile', None)

    assigned_pickups = PickupRequest.objects.filter(assigned_collector=user)
    active_pickups = assigned_pickups.filter(status__in=[
        PickupRequest.STATUS_ACCEPTED,
        PickupRequest.STATUS_IN_PROGRESS
    ]).order_by('preferred_date')

    completed_pickups = assigned_pickups.filter(status=PickupRequest.STATUS_COMPLETED)
    
    # Available open requests to pick up
    available_pickups = PickupRequest.objects.filter(
        status=PickupRequest.STATUS_PENDING
    ).order_by('preferred_date')[:5]

    transactions = Transaction.objects.filter(collector=user)
    total_earnings = transactions.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_weight = transactions.aggregate(Sum('actual_weight'))['actual_weight__sum'] or 0

    context = {
        'profile': profile,
        'active_pickups': active_pickups,
        'available_pickups': available_pickups,
        'completed_count': completed_pickups.count(),
        'total_earnings': total_earnings,
        'total_weight': total_weight,
        'recent_transactions': transactions.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/collector_dashboard.html', context)


@recycler_required
def recycler_dashboard(request):
    user = request.user
    orders = PurchaseRequest.objects.filter(recycler=user)

    total_orders = orders.count()
    fulfilled_orders = orders.filter(status=PurchaseRequest.STATUS_FULFILLED).count()
    pending_orders = orders.filter(status__in=[PurchaseRequest.STATUS_PENDING, PurchaseRequest.STATUS_APPROVED]).count()

    total_procured_kg = orders.filter(status=PurchaseRequest.STATUS_FULFILLED).aggregate(
        Sum('requested_quantity_kg')
    )['requested_quantity_kg__sum'] or 0

    total_spend = orders.filter(status=PurchaseRequest.STATUS_FULFILLED).aggregate(
        Sum('total_estimated_cost')
    )['total_estimated_cost__sum'] or 0

    # Stock available across categories
    categories = ScrapCategory.objects.filter(is_active=True)
    stock_overview = []
    for cat in categories:
        collected = Transaction.objects.filter(category=cat).aggregate(Sum('actual_weight'))['actual_weight__sum'] or 0
        stock_overview.append({
            'category': cat,
            'collected_kg': collected
        })

    context = {
        'total_orders': total_orders,
        'fulfilled_orders': fulfilled_orders,
        'pending_orders': pending_orders,
        'total_procured_kg': total_procured_kg,
        'total_spend': total_spend,
        'stock_overview': stock_overview,
        'recent_orders': orders.order_by('-created_at')[:6],
    }
    return render(request, 'dashboard/recycler_dashboard.html', context)


@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_collectors = User.objects.filter(role=User.ROLE_COLLECTOR).count()
    unverified_collectors = CollectorProfile.objects.filter(is_verified=False)

    all_pickups = PickupRequest.objects.all()
    total_pickups = all_pickups.count()
    completed_pickups = all_pickups.filter(status=PickupRequest.STATUS_COMPLETED).count()

    transactions = Transaction.objects.all()
    total_weight_collected = transactions.aggregate(Sum('actual_weight'))['actual_weight__sum'] or 0
    total_volume_amount = transactions.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    recent_pickups = all_pickups.order_by('-created_at')[:8]
    recent_complaints = Complaint.objects.all().order_by('-created_at')[:5]

    # Chart 1 Data: Total collected weight by Category
    categories = ScrapCategory.objects.all()
    category_labels = []
    category_weights = []
    for cat in categories:
        w = Transaction.objects.filter(category=cat).aggregate(Sum('actual_weight'))['actual_weight__sum'] or 0
        if w > 0:
            category_labels.append(cat.name)
            category_weights.append(float(w))

    # If no transactions yet, provide category indicative rate distribution
    if not category_labels:
        category_labels = [c.name for c in categories]
        category_weights = [float(c.base_rate_per_kg) for c in categories]

    context = {
        'total_users': total_users,
        'total_collectors': total_collectors,
        'unverified_collectors': unverified_collectors,
        'total_pickups': total_pickups,
        'completed_pickups': completed_pickups,
        'total_weight_collected': total_weight_collected,
        'total_volume_amount': total_volume_amount,
        'recent_pickups': recent_pickups,
        'recent_complaints': recent_complaints,
        'category_labels': category_labels,
        'category_weights': category_weights,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@admin_required
def verify_collector_action(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(CollectorProfile, id=profile_id)
        profile.is_verified = True
        profile.save()
        messages.success(request, f"Collector {profile.user.get_full_name() or profile.user.username} has been verified successfully.")
    return redirect('dashboard:admin')


@admin_required
def update_complaint_status(request, complaint_id, new_status):
    if request.method == 'POST':
        complaint = get_object_or_404(Complaint, id=complaint_id)
        if new_status.upper() in ['OPEN', 'IN_INVESTIGATION', 'RESOLVED']:
            complaint.status = new_status.upper()
            complaint.save()
            messages.success(request, f"Complaint #{complaint.id} status changed to {complaint.get_status_display()}.")
    return redirect('dashboard:admin')
