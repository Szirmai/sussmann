# Create your models here.
from django.shortcuts import render, redirect, get_object_or_404
from shop.models import *
from Home.models import *
from shop.forms import *
from django.contrib import messages
from Home.forms import *
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout

def is_admin(user):
    return user.is_authenticated and user.is_superuser  # Only superusers can access

@user_passes_test(is_admin, login_url='/')
def dash(request):
    order_number = Order.objects.filter(status__iexact='Új').count()
    product_number = Product.objects.all().count()
    contact_number = Contact.objects.filter(status__iexact='Új').count()
    shipping_costs = ShippingCost.objects.all()
    order = Order.objects.all().order_by('-created_at')[0:20]

    context = {
        'order_number': order_number,
        'product_number': product_number,
        'contact_number': contact_number,
        'shipping_costs': shipping_costs,
        'orders': order,
    }
    return render(request, 'dash/home.html', context)

@user_passes_test(is_admin, login_url='/')
def order_page(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    shipping_address = ShippingAddress.objects.filter(order=order)
    billing_address = BillingAddress.objects.filter(order=order)

    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "A rendelés státusza frissítve lett!")
            return redirect("order_list")  # ✅ Újratöltjük az oldalt
    else:
        form = OrderStatusForm(instance=order)

    context = {
        'order': order,
        'order_items': order_items,
        'shipping_address': shipping_address,
        'billing_address': billing_address,
        'form': form,  # ✅ Hozzáadjuk a státusz szerkesztő formot
    }
    return render(request, 'dash/order.html', context)

@user_passes_test(is_admin, login_url='/')
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Request.FILES szükséges a képekhez
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Ha sikeres, átirányítjuk a termékek listájára
    else:
        form = ProductForm()

    return render(request, 'dash/upload-product.html', {'form': form})

@user_passes_test(is_admin, login_url='/')
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Az id alapján lekérjük a terméket
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  # Megadjuk az instance-t, hogy szerkeszthető legyen
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Sikeres mentés után visszairányítjuk a listára
    else:
        form = ProductForm(instance=product)  # Ha GET kérés, akkor a termékadatokkal töltjük a formot

    return render(request, 'dash/upload-product.html', {'form': form, 'product': product})

@user_passes_test(is_admin, login_url='/')
def product_list(request):
    products = Product.objects.all().order_by('-created_at')

    context = {'products': products}
    return render(request, 'dash/product_list.html', context)

@user_passes_test(is_admin, login_url='/')
def order_list(request):

    orders = Order.objects.all().order_by('-created_at')

    context = {'orders': orders}

    return render(request, 'dash/orders.html', context)

@user_passes_test(is_admin, login_url='/')
def contacts(request):
    contacts = Contact.objects.all().order_by('-created_at')

    context = {'contacts': contacts}
    return render(request, 'dash/contacts.html', context)


@user_passes_test(is_admin, login_url='/')
def contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)  # get_object_or_404, hogy egyetlen példányt kapjunk

    if request.method == 'POST':
        form = ContactStatusForm(request.POST, request.FILES, instance=contact)  # A formot az instance-szal kell tölteni
        if form.is_valid():
            form.save()
            messages.success(request, 'A művelet sikeres volt!')
            return redirect('contacts')  # Sikeres mentés után visszairányítjuk a listára
    else:
        form = ContactStatusForm(instance=contact)  # A formot az instance-szal tölthetjük

    context = {'contact': contact,
               'form': form}

    return render(request, 'dash/contact.html', context)

@user_passes_test(is_admin, login_url='/')
def edit_shipping(request, shipping_id):
    shipping = get_object_or_404(ShippingCost, id=shipping_id)  # get_object_or_404, hogy egy egyedi példányt kapjunk
    title = 'Szállítási költség szerkesztése!'
    note = '* A Múltban leadott rendelésekre a változtatás nem vonatkozik'
    if request.method == 'POST':
        form = EditShipping(request.POST, request.FILES, instance=shipping)  # Az instance paramétert helyesen használjuk
        if form.is_valid():
            form.save()
            messages.success(request, 'A művelet sikeres volt!')
            return redirect('dash-home')  # Sikeres mentés után visszairányítjuk a listára
    else:
        form = EditShipping(instance=shipping)  # Az instance paramétert helyesen használjuk

    context = {'shipping': shipping,  # Helyes változó használata
               'form': form,
               'title': title,
               'note': note}

    return render(request, 'dash/edit.html', context)

def logout(request):
    logout(request)
    return redirect("") 