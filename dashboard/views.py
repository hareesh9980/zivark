from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
import json


@login_required
def home_view(request):
    from rfq.models import RFQ, Quotation

    # ── SUMMARY STATS ────────────────────────
    total_rfqs  = RFQ.objects.count()
    draft       = RFQ.objects.filter(status='draft').count()
    in_progress = RFQ.objects.filter(status='in_progress').count()
    sent        = RFQ.objects.filter(status='sent').count()
    won         = RFQ.objects.filter(status='won').count()
    lost        = RFQ.objects.filter(status='lost').count()

    # ── REVENUE ──────────────────────────────
    from django.db.models import Sum
    total_revenue = Quotation.objects.filter(
        status='won'
    ).aggregate(Sum('grand_total'))['grand_total__sum'] or 0

    month_revenue = Quotation.objects.filter(
        status='won',
        created_at__month=date.today().month,
        created_at__year=date.today().year,
    ).aggregate(Sum('grand_total'))['grand_total__sum'] or 0

    # ── WIN RATE ─────────────────────────────
    closed = won + lost
    win_rate = round((won / closed * 100) if closed > 0 else 0, 1)

    # ── MONTHLY RFQ TREND (last 6 months) ────
    monthly_labels = []
    monthly_rfq    = []
    monthly_won    = []
    monthly_rev    = []

    for i in range(5, -1, -1):
        d     = date.today().replace(day=1) - timedelta(days=i*30)
        month = d.month
        year  = d.year
        label = d.strftime('%b %Y')
        monthly_labels.append(label)
        monthly_rfq.append(
            RFQ.objects.filter(
                created_at__month=month,
                created_at__year=year
            ).count()
        )
        monthly_won.append(
            RFQ.objects.filter(
                status='won',
                created_at__month=month,
                created_at__year=year
            ).count()
        )
        rev = Quotation.objects.filter(
            status='won',
            created_at__month=month,
            created_at__year=year
        ).aggregate(Sum('grand_total'))['grand_total__sum'] or 0
        monthly_rev.append(float(rev))

    # ── WEEKLY RFQ TREND (last 7 days) ───────
    weekly_labels = []
    weekly_rfq    = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        weekly_labels.append(d.strftime('%d %b'))
        weekly_rfq.append(
            RFQ.objects.filter(
                created_at__date=d
            ).count()
        )

    # ── STATUS BREAKDOWN ─────────────────────
    status_data = [draft, in_progress, sent, won, lost]

    # ── RECENT RFQs ──────────────────────────
    recent_rfqs = RFQ.objects.select_related(
        'client', 'engineer'
    ).order_by('-created_at')[:10]

    return render(request, 'dashboard/home.html', {
        # Stats
        'total_rfqs':    total_rfqs,
        'draft':         draft,
        'in_progress':   in_progress,
        'sent':          sent,
        'won':           won,
        'lost':          lost,
        'win_rate':      win_rate,
        'total_revenue': total_revenue,
        'month_revenue': month_revenue,

        # Chart data
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_rfq':    json.dumps(monthly_rfq),
        'monthly_won':    json.dumps(monthly_won),
        'monthly_rev':    json.dumps(monthly_rev),
        'weekly_labels':  json.dumps(weekly_labels),
        'weekly_rfq':     json.dumps(weekly_rfq),
        'status_data':    json.dumps(status_data),

        # Recent
        'recent_rfqs': recent_rfqs,
    })