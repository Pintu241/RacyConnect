from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction as db_transaction
from django.core.paginator import Paginator
from django.utils import timezone
from accounts.decorators import customer_required, collector_required, role_required
from .models import PickupRequest
from .forms import PickupRequestCreateForm, PickupCompleteForm, PickupCancelForm
from transactions.models import Transaction

@login_required
def pickup_list_view(request):
    user = request.user
    status_filter = request.GET.get('status', 'all')

    if user.is_customer:
        requests_qs = PickupRequest.objects.filter(customer=user)
    elif user.is_collector:
        requests_qs = PickupRequest.objects.filter(assigned_collector=user)
    else:  # Admin or Recycler
        requests_qs = PickupRequest.objects.all()

    if status_filter == 'active':
        requests_qs = requests_qs.filter(status__in=[PickupRequest.STATUS_PENDING, PickupRequest.STATUS_ACCEPTED, PickupRequest.STATUS_IN_PROGRESS])
    elif status_filter == 'completed':
        requests_qs = requests_qs.filter(status=PickupRequest.STATUS_COMPLETED)
    elif status_filter == 'cancelled':
        requests_qs = requests_qs.filter(status=PickupRequest.STATUS_CANCELLED)

    paginator = Paginator(requests_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pickups/pickup_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
    })


@login_required
def pickup_create_view(request):
    user = request.user
    if request.method == 'POST':
        form = PickupRequestCreateForm(request.POST, request.FILES)
        if form.is_valid():
            pickup = form.save(commit=False)
            pickup.customer = user
            pickup.save()
            messages.success(request, f"Pickup request {pickup.reference_id} created successfully! Our collectors have been notified.")
            return redirect('pickups:detail', reference_id=pickup.reference_id)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        # Prepopulate with customer profile details
        initial_data = {
            'pickup_address': user.address,
            'city': user.city or 'Green City',
            'postal_code': user.postal_code,
            'contact_phone': user.phone_number,
            'preferred_date': timezone.now().date(),
        }
        form = PickupRequestCreateForm(initial=initial_data)

    return render(request, 'pickups/pickup_create.html', {'form': form})


@login_required
def pickup_detail_view(request, reference_id):
    pickup = get_object_or_404(PickupRequest, reference_id=reference_id)
    user = request.user

    # Permission check: customer, assigned collector, or admin
    if not (user.is_platform_admin or user == pickup.customer or user == pickup.assigned_collector or (user.is_collector and pickup.status == PickupRequest.STATUS_PENDING)):
        messages.error(request, "You do not have permission to view this pickup request.")
        return redirect('dashboard:index')

    cancel_form = PickupCancelForm() if pickup.can_be_cancelled(user) else None
    complete_form = None
    if pickup.can_be_completed(user):
        initial_rate = pickup.category.base_rate_per_kg
        complete_form = PickupCompleteForm(initial={
            'agreed_rate_per_kg': initial_rate,
            'actual_weight': pickup.estimated_weight,
        })

    return render(request, 'pickups/pickup_detail.html', {
        'pickup': pickup,
        'cancel_form': cancel_form,
        'complete_form': complete_form,
    })


@login_required
def pickup_cancel_view(request, reference_id):
    pickup = get_object_or_404(PickupRequest, reference_id=reference_id)
    user = request.user

    if not pickup.can_be_cancelled(user):
        messages.error(request, "This pickup request can no longer be cancelled.")
        return redirect('pickups:detail', reference_id=pickup.reference_id)

    if request.method == 'POST':
        form = PickupCancelForm(request.POST)
        if form.is_valid():
            pickup.status = PickupRequest.STATUS_CANCELLED
            pickup.cancellation_reason = form.cleaned_data['cancellation_reason']
            pickup.save()
            messages.info(request, f"Pickup request {pickup.reference_id} was cancelled.")
            return redirect('pickups:detail', reference_id=pickup.reference_id)
    
    return redirect('pickups:detail', reference_id=pickup.reference_id)


@collector_required
def collector_available_pickups(request):
    """View for scrap collectors to browse available open requests in need of pickup."""
    open_pickups = PickupRequest.objects.filter(status=PickupRequest.STATUS_PENDING).order_by('preferred_date', 'created_at')
    
    # Optional area search
    query = request.GET.get('q', '')
    if query:
        open_pickups = open_pickups.filter(pickup_address__icontains=query) | open_pickups.filter(city__icontains=query)

    paginator = Paginator(open_pickups, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'pickups/collector_available.html', {
        'page_obj': page_obj,
        'query': query,
    })


@collector_required
def collector_accept_pickup(request, reference_id):
    """Collector accepts a pending pickup request."""
    if request.method != 'POST':
        return redirect('pickups:available')

    pickup = get_object_or_404(PickupRequest, reference_id=reference_id)
    if pickup.status != PickupRequest.STATUS_PENDING:
        messages.warning(request, f"Pickup {pickup.reference_id} has already been accepted or is no longer pending.")
        return redirect('pickups:available')

    pickup.assigned_collector = request.user
    pickup.status = PickupRequest.STATUS_ACCEPTED
    pickup.save()

    messages.success(request, f"You have accepted pickup request {pickup.reference_id}! Please contact the customer and arrive on the scheduled date.")
    return redirect('pickups:detail', reference_id=pickup.reference_id)


@collector_required
def collector_update_status(request, reference_id, new_status):
    """Collector updates status e.g. marks out for pickup."""
    if request.method != 'POST':
        return redirect('pickups:detail', reference_id=reference_id)

    pickup = get_object_or_404(PickupRequest, reference_id=reference_id)
    if pickup.assigned_collector != request.user and not request.user.is_platform_admin:
        messages.error(request, "You are not authorized to update this pickup.")
        return redirect('pickups:detail', reference_id=reference_id)

    if new_status == 'in_progress' and pickup.status == PickupRequest.STATUS_ACCEPTED:
        pickup.status = PickupRequest.STATUS_IN_PROGRESS
        pickup.save()
        messages.success(request, f"Pickup {pickup.reference_id} marked as 'Out for Pickup'.")
    elif new_status == 'release' and pickup.status in [PickupRequest.STATUS_ACCEPTED, PickupRequest.STATUS_IN_PROGRESS]:
        pickup.assigned_collector = None
        pickup.status = PickupRequest.STATUS_PENDING
        pickup.save()
        messages.info(request, f"Pickup {pickup.reference_id} was released back to the open pool.")
        return redirect('dashboard:collector')

    return redirect('pickups:detail', reference_id=pickup.reference_id)


@login_required
def pickup_complete_view(request, reference_id):
    """Collector or admin completes pickup, records actual weight & rate, generates transaction."""
    pickup = get_object_or_404(PickupRequest, reference_id=reference_id)
    user = request.user

    if not pickup.can_be_completed(user):
        messages.error(request, "This pickup cannot be completed at this stage.")
        return redirect('pickups:detail', reference_id=pickup.reference_id)

    if request.method == 'POST':
        form = PickupCompleteForm(request.POST)
        if form.is_valid():
            actual_weight = form.cleaned_data['actual_weight']
            agreed_rate = form.cleaned_data['agreed_rate_per_kg']
            payment_method = form.cleaned_data['payment_method']
            payment_status = form.cleaned_data['payment_status']
            transaction_notes = form.cleaned_data['transaction_notes']

            total_amount = round(actual_weight * agreed_rate, 2)

            with db_transaction.atomic():
                # 1. Update Pickup Request
                pickup.actual_weight = actual_weight
                pickup.agreed_rate_per_kg = agreed_rate
                pickup.status = PickupRequest.STATUS_COMPLETED
                pickup.save()

                # 2. Generate Transaction Record
                txn, created = Transaction.objects.get_or_create(
                    pickup=pickup,
                    defaults={
                        'customer': pickup.customer,
                        'collector': pickup.assigned_collector or user,
                        'category': pickup.category,
                        'actual_weight': actual_weight,
                        'agreed_rate_per_kg': agreed_rate,
                        'total_amount': total_amount,
                        'payment_method': payment_method,
                        'payment_status': payment_status,
                        'notes': transaction_notes,
                    }
                )
                if not created:
                    txn.actual_weight = actual_weight
                    txn.agreed_rate_per_kg = agreed_rate
                    txn.total_amount = total_amount
                    txn.payment_method = payment_method
                    txn.payment_status = payment_status
                    txn.notes = transaction_notes
                    txn.save()

                # 3. Update Collector Profile statistics
                collector_user = pickup.assigned_collector or user
                if hasattr(collector_user, 'collector_profile'):
                    profile = collector_user.collector_profile
                    profile.total_collected_weight += actual_weight
                    profile.total_earnings += total_amount
                    profile.save()

            messages.success(request, f"Pickup {pickup.reference_id} marked COMPLETED! Transaction #{txn.transaction_id} generated for ₹{total_amount}.")
            return redirect('transactions:detail', transaction_id=txn.transaction_id)
        else:
            messages.error(request, "Please correct the weight or price values.")

    return redirect('pickups:detail', reference_id=pickup.reference_id)
