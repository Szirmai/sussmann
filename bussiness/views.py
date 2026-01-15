from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from collections import defaultdict
from django.db.models import Sum
from datetime import datetime
import random
from shop.models import Order
from django.db.models import Count
from .forms import *
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import json
from django.utils.safestring import mark_safe
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.safestring import mark_safe
from Home.models import Product



@login_required
def add_cost(request):
    if request.method == "POST":
        form = CostForm(request.POST)
        if form.is_valid():  # Ha a form érvényes
            form.save()  # Mentjük a költséget
            messages.success(request, 'A költség sikeresen el lett mentve!')
            return redirect("bussiness_home")  # Redirect a megfelelő oldalra (például a dashboard)
        else:
            messages.error(request, "Sikertelen művelet!")
    else:

        form = CostForm()  # Ha GET kérés jön, üres formot adunk vissza

    title = "Költség felvétele!"

    return render(request, "dash/add.html", {"form": form, 'title': title})


@login_required
def edit_cost(request, cost_id):
    """ Költség szerkesztése """
    cost = get_object_or_404(Cost, id=cost_id)
    if request.method == "POST":
        form = CostForm(request.POST, instance=cost)
        if form.is_valid():
            form.save()
            messages.success(request, "Sikeres szerkesztés!")
            return redirect('bussiness_home')  # Vissza a listához
        else:
            messages.error(request, "Sikertelen szerkesztés!")
    else:

        form = CostForm(instance=cost)

    return render(request, 'dash/add.html', {'form': form, 'cost': cost})

@login_required
def delete_cost(request, cost_id):
    """ Költség törlése """
    cost = get_object_or_404(Cost, id=cost_id)
    if request.method == "POST":
        cost.delete()
        messages.success(request, "Sikeres törlés")
        return redirect('bussiness_home')  # Vissza a listához
    else:
            messages.error(request, "Sikertelen törlés!")
    return messages.success(request, 'Sikeres törlés!')

@login_required
def add_cost_cat(request):
    if request.method == "POST":
        form = CostTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sikeres mentés!")
            return redirect('add_cost')  # Ide a megfelelő nézet nevét írd be
        else:
            messages.error(request, "Sikertelen mentés!")
    else:
        form = CostTypeForm()

    costtypes = CostType.objects.all().order_by('-id')
    title = "Kategória hozzáadása!"

    costtypes = CostType.objects.all().order_by('-id')
    return render(request, 'bus/add_cost_cat.html', {'form': form, 'title': title, 'costtypes': costtypes})

@login_required
def delete_cost_cat(request, cost_id):
    """ Kategória törlése, ha nincs hozzá kapcsolódó költség """
    cost_type = get_object_or_404(CostType, id=cost_id)

    # Ellenőrizd, hogy vannak-e hozzá tartozó költségek
    if Cost.objects.filter(type=cost_type).exists():
        messages.error(request, "Nem törölheted ezt a kategóriát, mert van hozzá tartozó költség!")
        return redirect('add_cost')  # Visszaviszi az oldalt

    if request.method == "POST":
        cost_type.delete()
        messages.success(request, "Sikeresen törölted a kategóriát.")
        return redirect('add_cost')

    messages.error(request, "Hiba történt, próbáld újra!")
    return redirect('add_cost')




@login_required
def home(request):
    # =====================
    # ÉV KEZELÉS
    # =====================
    current_year = timezone.now().year
    selected_year = request.GET.get("year", current_year)

    try:
        selected_year = int(selected_year)
    except ValueError:
        selected_year = current_year

    # =====================
    # ELÉRHETŐ ÉVEK
    # =====================
    order_years = [d.year for d in Order.objects.dates('created_at', 'year', order='DESC')]
    cost_years = [d.year for d in Cost.objects.dates('created_at', 'year', order='DESC')]

    available_years = sorted(set(order_years + cost_years), reverse=True)

    # =====================
    # ORDERS (kiválasztott év)
    # =====================
    orders = Order.objects.filter(created_at__year=selected_year)

    total_cost = sum(
        o.all_cost for o in orders
        if o.all_cost is not None
    )

    # =====================
    # COSTS (kiválasztott év)
    # =====================
    costs = Cost.objects.filter(created_at__year=selected_year).order_by('-created_at')
    cost_value = sum(c.cost for c in costs)

    # =====================
    # COST TYPE ÖSSZESÍTÉS
    # =====================
    cost_data = defaultdict(int)
    for c in costs:
        if c.type:
            cost_data[c.type.name] += c.cost

    labels = list(cost_data.keys())
    values = list(cost_data.values())

    # =====================
    # HÓNAPOK
    # =====================
    month_names = [
        "Január", "Február", "Március", "Április", "Május", "Június",
        "Július", "Augusztus", "Szeptember", "Október", "November", "December"
    ]

    # =====================
    # HAVI COSTOK TÍPUSONKÉNT
    # =====================
    monthly_costs_by_type = defaultdict(lambda: {m: 0 for m in month_names})

    cost_by_month_and_type = (
        Cost.objects
        .filter(created_at__year=selected_year)
        .values('created_at__month', 'type__name')
        .annotate(total=Sum('cost'))
    )

    for entry in cost_by_month_and_type:
        month = month_names[entry['created_at__month'] - 1]
        cost_type = entry['type__name'] or "Nincs kategória"
        monthly_costs_by_type[cost_type][month] = entry['total']

    def gen_color():
        return f'rgba({random.randint(50,200)}, {random.randint(50,200)}, {random.randint(50,200)}, 0.7)'

    color_map = {ct: gen_color() for ct in monthly_costs_by_type}

    monthly_datasets = []
    for ct, months in monthly_costs_by_type.items():
        color = color_map[ct]
        monthly_datasets.append({
            'label': ct,
            'data': list(months.values()),
            'backgroundColor': color,
            'borderColor': color.replace('0.7', '1'),
            'borderWidth': 1
        })

    # =====================
    # PROFIT
    # =====================
    total_profit = total_cost - cost_value

    # =====================
    # HAVI BEVÉTEL
    # =====================
    monthly_revenue = defaultdict(int)
    for o in orders:
        if o.all_cost:
            monthly_revenue[o.created_at.month] += o.all_cost

    chart_labels = [month_names[m-1] for m in sorted(monthly_revenue)]
    chart_data = [monthly_revenue[m] for m in sorted(monthly_revenue)]

    # =====================
    # RENDELÉSSZÁM HAVONTA
    # =====================
    orders_by_month = (
        Order.objects
        .filter(created_at__year=selected_year)
        .values('created_at__month')
        .annotate(total=Count('id'))
    )

    orders_data = defaultdict(int)
    for e in orders_by_month:
        orders_data[month_names[e['created_at__month'] - 1]] = e['total']

    orders_labels = list(orders_data.keys())
    orders_values = list(orders_data.values())

    # =====================
    # NAPI – UTOLSÓ 7 NAP
    # =====================
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)

    orders_daily = Order.objects.filter(
        created_at__date__gte=seven_days_ago,
        created_at__date__lte=today
    )

    daily_revenue = {(seven_days_ago + timedelta(days=i)).strftime("%Y-%m-%d"): 0 for i in range(7)}
    daily_orders = daily_revenue.copy()

    for o in orders_daily:
        day = o.created_at.strftime("%Y-%m-%d")
        if o.all_cost:
            daily_revenue[day] += o.all_cost
        daily_orders[day] += 1

    costs_selected_year = Cost.objects.filter(created_at__year=selected_year)
    total_cost_selected_year = costs_selected_year.aggregate(total=Sum('cost'))['total'] or 0

    # Összes költség minden évből
    total_cost_all_years = Cost.objects.aggregate(total=Sum('cost'))['total'] or 0

    total_revenue_all_years = (
    Order.objects
    .filter(all_cost__isnull=False, )
    .aggregate(total=Sum('all_cost'))['total'] or 0
    )

    total_profit_all_years = total_revenue_all_years - total_cost_all_years

    

    koltseg = (
    Product.objects
    .filter(available=False)
    .aggregate(total=Sum('cost'))['total'] or 0
    )
    koltseg_eves = (
        Product.objects
        .filter(available=False)
        .filter(created_at__year=selected_year)
        .aggregate(total=Sum('cost'))['total'] or 0
    )
    megteremtett_ertek_ossz_eves = (
        Product.objects
        .filter(created_at__year=selected_year)
        .aggregate(total=Sum('price'))['total'] or 0
    )
    megteremtett_ertek_ossz_ever = (
        Product.objects

        .aggregate(total=Sum('price'))['total'] or 0
    )
    meglevo_ertek = (
        Product.objects
        .filter(available=True)
        .aggregate(total=Sum('price'))['total'] or 0
    )
    ever_megt_ert = megteremtett_ertek_ossz_ever - total_cost_all_years
    eves_megt_ert = megteremtett_ertek_ossz_eves - total_cost_selected_year
    profit_eves = total_cost - koltseg_eves
    profit_ever = total_revenue_all_years - koltseg
    raktar_ertek = total_cost_all_years - koltseg

    context = {
        'total_profit_all_years': total_profit_all_years,
        'total_revenue_all_years': total_revenue_all_years,
        'total_cost_selected_year': total_cost_selected_year,
        'total_cost_all_years': total_cost_all_years,
        'available_years': available_years,
        'selected_year': selected_year,

        'labels': labels,
        'values': values,
        'monthly_labels': month_names,
        'monthly_datasets': monthly_datasets,

        'total_cost': total_cost,
        'total_profit': total_profit,

        'chart_labels': chart_labels,
        'chart_data': chart_data,

        'orders_labels': orders_labels,
        'orders_values': orders_values,

        'chart_labels_daily': mark_safe(json.dumps(list(daily_revenue.keys()))),
        'chart_data_daily': mark_safe(json.dumps(list(daily_revenue.values()))),
        'chart_orders_daily_count': list(daily_orders.values()),
        'income_item': orders,
        'costs': costs,
        'koltseg': koltseg,
        'koltseg_eves': koltseg_eves,
        'megteremtett_ertek_ossz_eves': megteremtett_ertek_ossz_eves,
        'megteremtett_ertek_ossz_ever': megteremtett_ertek_ossz_ever,
        'meglevo_ertek': meglevo_ertek,
        'ever_megt_ert': ever_megt_ert,
        'eves_megt_ert': eves_megt_ert,
        'profit_eves': profit_eves,
        'profit_ever': profit_ever,
        'raktar_ertek': raktar_ertek,
    }

    return render(request, 'bus/home.html', context)



#be kell építeni a home-ba:



@login_required
def revenue_last_7_days(request):
    today_daily = timezone.now()
    seven_days_ago_daily = today_daily - timedelta(days=7)

    orders_daily = Order.objects.filter(created_at__gte=seven_days_ago_daily, created_at__lte=today_daily)

    daily_revenue_daily = {}
    for order_daily in orders_daily:
        day_daily = order_daily.created_at.strftime("%Y-%m-%d")  # Dátumot stringgé alakítjuk
        if day_daily not in daily_revenue_daily:
            daily_revenue_daily[day_daily] = 0
        daily_revenue_daily[day_daily] += order_daily.all_cost if order_daily.all_cost else 0

    days_daily = list(daily_revenue_daily.keys())
    revenues_daily = list(daily_revenue_daily.values())

    context = {
        'chart_labels_daily': mark_safe(json.dumps(days_daily)),  # JSON biztosítása
        'chart_data_daily': mark_safe(json.dumps(revenues_daily)),  # JSON biztosítása
        'today': today_daily,  # A dátum megfelelő formázásban
    }

    return render(request, 'your_template.html', context)














