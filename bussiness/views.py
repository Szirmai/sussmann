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
    orders = Order.objects.all()
    
    # Az összes rendelés teljes árának összegzése
    total_cost = sum(order.all_cost for order in orders if order.all_cost is not None and order.status=="Kiszállítva")
    costs = Cost.objects.all().order_by('-created_at')

    # Teljes költség összege
    cost_value = sum(cost.cost for cost in costs)

    # CostType szerint csoportosított költségek (eredeti adatok megtartása)
    cost_data = defaultdict(int)
    for cost in costs:
        if cost.type:
            cost_data[cost.type.name] += cost.cost

    labels = list(cost_data.keys())
    values = list(cost_data.values())

    # Hónapok listája
    month_names = [
        "Január", "Február", "Március", "Április", "Május", "Június",
        "Július", "Augusztus", "Szeptember", "Október", "November", "December"
    ]

    # Hónapokra és CostType-ra bontott adatok
    monthly_costs_by_type = defaultdict(lambda: {month: 0 for month in month_names})

    cost_by_month_and_type = (
        Cost.objects
        .values('created_at__month', 'type__name')
        .annotate(total=Sum('cost'))
    )

    for entry in cost_by_month_and_type:
        month_index = entry['created_at__month'] - 1
        cost_type = entry['type__name'] or "Nincs kategória"
        monthly_costs_by_type[cost_type][month_names[month_index]] = entry['total']

    # Színek generálása minden CostType-hoz
    def generate_color():
        return f'rgba({random.randint(50, 200)}, {random.randint(50, 200)}, {random.randint(50, 200)}, 0.7)'

    color_map = {cost_type: generate_color() for cost_type in monthly_costs_by_type.keys()}

    # Hónapokra bontott Chart.js adatok előkészítése
    monthly_labels = month_names
    monthly_datasets = []
    for cost_type, month_values in monthly_costs_by_type.items():
        color = color_map[cost_type]  # Egyedi szín hozzárendelése
        monthly_datasets.append({
            'label': cost_type,
            'data': list(month_values.values()),
            'backgroundColor': color,
            'borderColor': color.replace('0.7', '1'),  # Telítettebb szín a borderhez
            'borderWidth': 1
        })

    total_profit = total_cost - cost_value

    orders = Order.objects.all()

    # Kiszámoljuk a havi bevételeket
    monthly_revenue_data = defaultdict(int)  # Hónapok és bevételek összegzése

    for order in orders:
        if order.all_cost is not None:
            month = order.created_at.strftime('%Y-%m')  # Hónap formátuma YYYY-MM
            monthly_revenue_data[month] += order.all_cost  # Hozzáadjuk a bevételt az adott hónaphoz

    # Hónapok listájának generálása (sorrendbe téve)
    months = sorted(monthly_revenue_data.keys())

    # Bevételek kiírása hónapok szerint
    monthly_revenue_list = [
        {'month': month, 'revenue': monthly_revenue_data[month]}
        for month in months
    ]

    # Az adatokat Chart.js-hez is előkészítjük
    chart_labels = months  # Hónapok listája
    chart_data = [monthly_revenue_data[month] for month in months]  # Bevételek adatainak listája

     # Hónapokra bontott rendelések számolása
    orders_by_month = Order.objects.values('created_at__month').annotate(total=Count('id'))

    # Adatok előkészítése a Chart.js-hez
    orders_data = defaultdict(int)
    for entry in orders_by_month:
        month_index = entry['created_at__month'] - 1  # 0-alapú indexeléshez
        orders_data[month_names[month_index]] = entry['total']

    orders_labels = list(orders_data.keys())  # Hónapok nevei
    orders_values = list(orders_data.values())  # Megrendelések száma

    title = 'Pénzügyi adatok'

    today_daily = timezone.now().date()  # Csak a dátum kell
    seven_days_ago_daily = today_daily - timedelta(days=6)  # Az utolsó 7 napot nézzük

    # Lekérdezzük az összes rendelést az elmúlt 7 napból
    orders_daily = Order.objects.filter(created_at__date__gte=seven_days_ago_daily, created_at__date__lte=today_daily)

    # Üres szótár a napi bevételekhez
    daily_revenue_daily = { (seven_days_ago_daily + timedelta(days=i)).strftime("%Y-%m-%d"): 0 for i in range(7) }

    # Rendelések összegzése napokra bontva
    for order_daily in orders_daily:
        day_daily = order_daily.created_at.date().strftime("%Y-%m-%d")  # Csak a dátum kell
        daily_revenue_daily[day_daily] += order_daily.all_cost if order_daily.all_cost is not None else 0

    # Kulcsokat és értékeket listába tesszük
    days_daily = list(daily_revenue_daily.keys())  # Dátumok
    revenues_daily = list(daily_revenue_daily.values())  # Bevételek

    daily_orders_count = {}  # ÚJ: Naponta hány rendelés történt

    for order_daily in orders_daily:
        day_daily = order_daily.created_at.strftime("%Y-%m-%d")
    
    # Rendelésszám
        if day_daily not in daily_orders_count:
            daily_orders_count[day_daily] = 0
        daily_orders_count[day_daily] += 1  # Egy rendelés történt ezen a napon

# Új adat a frontendhez
    orders_count_daily_count = [daily_orders_count.get(day, 0) for day in days_daily]

    income_item = Order.objects.filter(status="Kiszállítva").order_by('-created_at')


    context = {
        'costs': costs,
        'cost_value': cost_value,
        'labels': labels,
        'values': values,
        'monthly_labels': monthly_labels,
        'monthly_datasets': monthly_datasets,
        'total_cost': total_cost,
        'total_profit': total_profit,
        
        'monthly_revenue_list': monthly_revenue_list,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'orders_labels': orders_labels,
        'orders_values': orders_values,

        'title': title,

        'chart_labels_daily': mark_safe(json.dumps(days_daily)),  # JSON biztosítása
        'chart_data_daily': mark_safe(json.dumps(revenues_daily)),  # JSON biztosítása
        'today': today_daily,  # A dátum megfelelő formázásban
        'chart_orders_daily_count': orders_count_daily_count,
        'income_item': income_item,
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














