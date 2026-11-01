from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.core.paginator import Paginator
from accounts.decorators import recycler_required, role_required, admin_required
from .models import PurchaseRequest
from .forms import PurchaseRequestForm
from scrap.models import ScrapCategory
from pickups.models import PickupRequest
from transactions.models import Transaction

def recycler_marketplace(request):
    """Shows aggregated recyclable materials available across the platform from completed collections."""
    categories = ScrapCategory.objects.filter(is_active=True)

    # Compute inventory aggregations per category
    inventory_data = []
    for cat in categories:
        collected = Transaction.objects.filter(category=cat).aggregate(
            total_weight=Sum('actual_weight'),
            total_txns=Count('id')
        )
        total_weight = collected['total_weight'] or 0
        total_txns = collected['total_txns'] or 0

        # Estimated available volume (completed minus fulfilled purchases)
        procured = PurchaseRequest.objects.filter(
            category=cat,
            status=PurchaseRequest.STATUS_FULFILLED
        ).aggregate(procured_weight=Sum('requested_quantity_kg'))['procured_weight'] or 0

        estimated_available = max(0, float(total_weight) - float(procured))

        inventory_data.append({
            'category': cat,
            'total_collected': total_weight,
            'total_txns': total_txns,
            'estimated_available': estimated_available,
        })

    return render(request, 'recyclers/marketplace.html', {
        'inventory_data': inventory_data,
    })


@recycler_required
def purchase_request_create(request):
    category_id = request.GET.get('category')
    initial_data = {}
    if category_id:
        try:
            cat = ScrapCategory.objects.get(id=category_id)
            initial_data['category'] = cat
            initial_data['offered_price_per_kg'] = cat.base_rate_per_kg
        except ScrapCategory.DoesNotExist:
            pass

    user = request.user
    if hasattr(user, 'recycler_profile') and user.recycler_profile.facility_address:
        initial_data['delivery_facility_address'] = user.recycler_profile.facility_address

    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.recycler = user
            purchase.save()
            messages.success(request, f"Purchase Request {purchase.request_id} submitted successfully! Our platform supply manager will review your order.")
            return redirect('recyclers:purchase_detail', request_id=purchase.request_id)
        else:
            messages.error(request, "Please check the highlighted errors in your order form.")
    else:
        form = PurchaseRequestForm(initial=initial_data)

    return render(request, 'recyclers/purchase_create.html', {'form': form})


@login_required
def purchase_request_list(request):
    user = request.user
    if user.is_recycler:
        orders = PurchaseRequest.objects.filter(recycler=user)
    else:  # Admin
        orders = PurchaseRequest.objects.all()

    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        orders = orders.filter(status=status_filter.upper())

    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'recyclers/purchase_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
    })


@login_required
def purchase_request_detail(request, request_id):
    purchase = get_object_or_404(PurchaseRequest, request_id=request_id)
    user = request.user

    if not (user.is_platform_admin or user == purchase.recycler):
        messages.error(request, "You do not have access to this purchase order.")
        return redirect('dashboard:index')

    return render(request, 'recyclers/purchase_detail.html', {'purchase': purchase})


@admin_required
def purchase_status_update(request, request_id, new_status):
    if request.method != 'POST':
        return redirect('recyclers:purchase_detail', request_id=request_id)

    purchase = get_object_or_404(PurchaseRequest, request_id=request_id)
    allowed = ['APPROVED', 'FULFILLED', 'CANCELLED']
    if new_status.upper() in allowed:
        purchase.status = new_status.upper()
        purchase.save()
        messages.success(request, f"Purchase order {purchase.request_id} updated to {purchase.get_status_display()}.")

    return redirect('recyclers:purchase_detail', request_id=purchase.request_id)
