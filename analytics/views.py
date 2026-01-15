from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from analytics.models import PageView

from django.db.models import Count
from django.db.models.functions import TruncWeek, TruncMonth

from datetime import timedelta
from collections import defaultdict


@login_required
def home(request):

    # ===============================
    # 🔒 CACHE – havi returning chart
    # ===============================
    CACHE_KEY = 'monthly_returning_chart'
    CACHE_TIMEOUT = 60 * 15  # 15 perc

    cached_data = cache.get(CACHE_KEY)

    if cached_data:
        monthly_labels = cached_data['labels']
        monthly_unique_data = cached_data['unique']
        monthly_returning_data = cached_data['returning']
    else:
        monthly_unique_ips = defaultdict(set)
        monthly_returning_ips = defaultdict(set)

        monthly_ip_days = (
            PageView.objects
            .values('ip_address', 'date__year', 'date__month')
            .annotate(days=Count('date', distinct=True))
        )

        for row in monthly_ip_days:
            key = f"{row['date__year']}-{row['date__month']:02d}"
            ip = row['ip_address']

            monthly_unique_ips[key].add(ip)

            if row['days'] > 1:
                monthly_returning_ips[key].add(ip)

        monthly_labels = sorted(monthly_unique_ips.keys())
        monthly_unique_data = [
            len(monthly_unique_ips[m]) for m in monthly_labels
        ]
        monthly_returning_data = [
            len(monthly_returning_ips[m]) for m in monthly_labels
        ]

        cache.set(CACHE_KEY, {
            'labels': monthly_labels,
            'unique': monthly_unique_data,
            'returning': monthly_returning_data,
        }, CACHE_TIMEOUT)

    # ===============================
    # 📊 NAPI / HETI / HAVI SZÁMOK
    # ===============================
    today = timezone.now().date()

    daily_visits = PageView.objects.filter(date=today).count()

    weekly_visits = (
        PageView.objects
        .annotate(week=TruncWeek('date'))
        .filter(week=TruncWeek(today))
        .count()
    )

    monthly_visits = (
        PageView.objects
        .annotate(month=TruncMonth('date'))
        .filter(month=TruncMonth(today))
        .count()
    )

    # ===============================
    # 👤 EGYEDI LÁTOGATÓK
    # ===============================
    daily_unique_visitors = (
        PageView.objects
        .filter(date=today)
        .values('ip_address')
        .distinct()
        .count()
    )

    weekly_unique_visitors = (
        PageView.objects
        .annotate(week=TruncWeek('date'))
        .filter(week=TruncWeek(today))
        .values('ip_address')
        .distinct()
        .count()
    )

    monthly_unique_visitors = (
        PageView.objects
        .annotate(month=TruncMonth('date'))
        .filter(month=TruncMonth(today))
        .values('ip_address')
        .distinct()
        .count()
    )

    # ===============================
    # 📈 TOP OLDALAK (ALL TIME)
    # ===============================
    top_pages = (
        PageView.objects
        .values('path')
        .annotate(visits=Count('id'))
        .order_by('-visits')[:7]
    )

    # ===============================
    # 📈 TOP OLDALAK – 7 NAP
    # ===============================
    seven_days_ago = today - timedelta(days=7)

    top_pages_last_7_days = (
        PageView.objects
        .filter(date__gte=seven_days_ago)
        .values('path')
        .annotate(visits=Count('id'))
        .order_by('-visits')[:7]
    )

    top_page_labels = [p['path'] for p in top_pages_last_7_days]
    top_page_data = [p['visits'] for p in top_pages_last_7_days]

    # ===============================
    # 📊 NAPI EGYEDI – 7 NAP
    # ===============================
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    daily_labels = [d.strftime("%Y-%m-%d") for d in last_7_days]
    daily_data = [
        PageView.objects
        .filter(date=day)
        .values('ip_address')
        .distinct()
        .count()
        for day in last_7_days
    ]

    # ===============================
    # 📉 VIEWS vs UNIQUE – EVER
    # ===============================
    daily_stats = (
        PageView.objects
        .values('date')
        .annotate(
            views=Count('id'),
            unique=Count('ip_address', distinct=True)
        )
        .order_by('date')
    )

    views_labels = [d['date'].strftime("%Y-%m-%d") for d in daily_stats]
    views_data = [d['views'] for d in daily_stats]
    views_unique_data = [d['unique'] for d in daily_stats] 


    # visszater latogatok %-ban


    monthly_unique_ips = defaultdict(set)
    monthly_returning_ips = defaultdict(set)

    monthly_ip_days = (
        PageView.objects
        .values('ip_address', 'date__year', 'date__month')
        .annotate(days=Count('date', distinct=True))
    )

    for row in monthly_ip_days:
        key = f"{row['date__year']}-{row['date__month']:02d}"
        ip = row['ip_address']

        # összes egyedi IP / hónap
        monthly_unique_ips[key].add(ip)

        # visszatérő (2+ nap ugyanabban a hónapban)
        if row['days'] > 1:
            monthly_returning_ips[key].add(ip)


    monthly_labels = sorted(monthly_unique_ips.keys())
    monthly_total = [len(monthly_unique_ips[m]) for m in monthly_labels]
    monthly_returning = [len(monthly_returning_ips[m]) for m in monthly_labels]

    # százalékos arány
    monthly_returning_percent = [
        round((r / t * 100), 1) if t > 0 else 0
        for r, t in zip(monthly_returning, monthly_total)
    ]



    # ===============================
    # 🧾 CONTEXT
    # ===============================
    context = {
        # számok
        'daily_visits': daily_visits,
        'weekly_visits': weekly_visits,
        'monthly_visits': monthly_visits,

        'daily_unique_visitors': daily_unique_visitors,
        'weekly_unique_visitors': weekly_unique_visitors,
        'monthly_unique_visitors': monthly_unique_visitors,

        # top oldalak
        'top_pages': top_pages,
        'top_pages_last_7_days': top_pages_last_7_days,
        'top_page_labels': top_page_labels,
        'top_page_data': top_page_data,

        # napi chart
        'daily_labels': daily_labels,
        'daily_data': daily_data,

        # views vs unique
        'views_labels': views_labels,
        'views_data': views_data,
        'views_unique_data': views_unique_data,

        # havi returning chart
        'monthly_labels': monthly_labels,
        'monthly_unique_data': monthly_unique_data,
        'monthly_returning_data': monthly_returning_data,

        # visszatero latogatok %-ban
        'monthly_returning_percent': monthly_returning_percent, 
    }

    return render(request, 'analytics/home.html', context)
