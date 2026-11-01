from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Transaction

@login_required
def transaction_list_view(request):
    user = request.user
    if user.is_customer:
        txns = Transaction.objects.filter(customer=user)
    elif user.is_collector:
        txns = Transaction.objects.filter(collector=user)
    else:  # Admin or Recycler
        txns = Transaction.objects.all()

    # Search filter
    search_q = request.GET.get('q', '')
    if search_q:
        txns = txns.filter(transaction_id__icontains=search_q) | txns.filter(pickup__reference_id__icontains=search_q)

    paginator = Paginator(txns, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'transactions/transaction_list.html', {
        'page_obj': page_obj,
        'search_q': search_q,
    })


@login_required
def transaction_detail_view(request, transaction_id):
    txn = get_object_or_404(Transaction, transaction_id=transaction_id)
    user = request.user

    # Security check: only customer, collector, or admin can view receipt
    if not (user.is_platform_admin or user == txn.customer or user == txn.collector):
        messages.error(request, "You are not authorized to view this receipt.")
        return redirect('dashboard:index')

    return render(request, 'transactions/transaction_detail.html', {'txn': txn})
