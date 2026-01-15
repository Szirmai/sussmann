from django.db import models
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from Home.models import Product  # Assuming you have a Product model
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import *
from .forms import *
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime
from django.core.mail import send_mail

stripe.api_key = settings.STRIPE_SECRET_KEY


def cart_add(request, product_id):
    cart = request.session.get('cart', {})  # Get the cart from the session
    product = get_object_or_404(Product, id=product_id)

    # Add or update quantity
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),  # Convert Decimal to float
            'quantity': 1,
        }

    # Save updated cart back to session
    request.session['cart'] = cart
    request.session.modified = True

    # Calculate price for a single item based on quantity
    item_price = round(cart[str(product_id)]['price'] * cart[str(product_id)]['quantity'], 2)

    messages.success(request, f"✅ {product.name} Hozzáadva a kosárhoz! (Teljes ára a terméknek: {item_price} Ft)")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True

        messages.success(request, "🗑️ Item removed from cart!")
    else:
        messages.error(request, "⚠️ Item not found in cart!")

    # Redirect back to the previous page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



def apply_coupon(request):
    if request.method != "POST":
        return redirect("cart_view")

    code = request.POST.get("coupon_code", "").strip().upper()

    if not code:
        messages.error(request, "Nem adtál meg kuponkódot.")
        return redirect("cart_view")

    try:
        coupon = Coupon.objects.get(code=code, active=True)
    except Coupon.DoesNotExist:
        messages.error(request, "Érvénytelen kuponkód.")
        return redirect("cart_view")

    # Kosár bruttó érték kiszámítása (egyszerűsítve)
    cart = request.session.get("cart", {})
    cart_total = 0

    for item in cart.values():
        cart_total += item["price"] * item["quantity"]

    if not coupon.is_valid(cart_total):
        messages.error(request, "Ez a kupon jelenleg nem használható.")
        return redirect("cart_view")

    # 👉 ITT kerül be a session-be
    request.session["coupon_id"] = coupon.id

    messages.success(request, "Kupon sikeresen alkalmazva!")
    return redirect("cart_view")

def remove_coupon(request):
    request.session.pop("coupon_id", None)
    messages.info(request, "Kupon eltávolítva.")
    return redirect("cart_view")


def cart_view(request):
    cart = request.session.get('cart', {})  # Get the cart from the session
    cart_items = []
    nettó_price = 0
    shipping_cost_obj = get_object_or_404(ShippingCost, id=1)
    shipping_cost = shipping_cost_obj.cost
    vat_rate = 0.27

    # Calculate total price for each item based on quantity
    for item_id, item_data in cart.items():
        item = Product.objects.get(id=item_id)  # Get the product from the database
        gross_price = item_data['price']  # Gross price from the database
        
        # Calculate Nettó (Net price) by removing VAT from the Gross price
        net_price = gross_price / (1 + vat_rate)
        
        # Calculate the total price of the item based on quantity
        item_total_price = net_price * item_data['quantity']  # Nettó price * quantity
        nettó_price += item_total_price  # Add to Nettó price

        cart_items.append({
            'id': item_id,  # Add product_id here
            'name': item_data['name'],
            'quantity': item_data['quantity'],
            'price': gross_price,
            'net_price': round(item_total_price, 2),  # Total price without VAT (Nettó)
            'total_price': round(item_total_price * (1 + vat_rate), 2)  # Total price with VAT (Bruttó)
        })

    # Calculate Bruttó (Gross price) including VAT
    bruttó_price = nettó_price * (1 + vat_rate)

    # ---------------------------
    # Ellenőrzés: termék elérhetőség
    # ---------------------------
    removed_items = []
    for product_id_str, item_data in list(cart.items()):
        try:
            product_id = int(product_id_str)
            product = get_object_or_404(Product, id=product_id)
        except ValueError:
            continue

        if not product.available or product.stock < item_data["quantity"]:
            removed_items.append(product.name)
            del cart[product_id_str]

    if removed_items:
        request.session["cart"] = cart
        messages.error(request, f"Ezeket a termékeket eltávolítottuk a kosárból, mert jelenleg nem elérhetők: {', '.join(removed_items)}")
        return redirect("cart_view")

    # ---------------------------
    # Kupon kezelés
    # ---------------------------
    coupon = None
    discount_amount = 0
    coupon_id = request.session.get("coupon_id")

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            # ellenőrizzük, hogy kosárértékre érvényes-e
            if coupon.is_valid(bruttó_price):
                if coupon.discount_type == "percent":
                    discount_amount = bruttó_price * coupon.discount_value / 100
                else:
                    discount_amount = coupon.discount_value
            else:
                # ha már nem érvényes, töröljük a session-ből
                request.session.pop("coupon_id", None)
                coupon = None
                discount_amount = 0
        except Coupon.DoesNotExist:
            request.session.pop("coupon_id", None)
            coupon = None
            discount_amount = 0

    # Calculate total including shipping and discount
    összesen_price = bruttó_price + shipping_cost - discount_amount

    # Send the cart data to the template
    context = {
        'cart_items': cart_items,
        'nettó_price': round(nettó_price, 2),
        'bruttó_price': round(bruttó_price, 2),
        'shipping_cost': shipping_cost,
        'összesen_price': round(összesen_price, 2),
        'coupon': coupon,
        'discount_amount': round(discount_amount, 2)
    }

    return render(request, 'shop/cart.html', context)


def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    nettó_price = 0
    shipping_cost_obj = get_object_or_404(ShippingCost, id=1)
    shipping_cost = shipping_cost_obj.cost
    vat_rate = 0.27

    removed_items = []
    for product_id_str, item_data in list(cart.items()):
        try:
            product_id = int(product_id_str)
            product = get_object_or_404(Product, id=product_id)
        except ValueError:
            continue
        if not product.available or product.stock < item_data["quantity"]:
            removed_items.append(product.name)
            del cart[product_id_str]

    if removed_items:
        request.session["cart"] = cart
        messages.error(request, f"Ezeket a termékeket eltávolítottuk a kosárból: {', '.join(removed_items)}")
        return redirect("cart_view")

    for item_id, item_data in cart.items():
        item = get_object_or_404(Product, id=item_id)
        gross_price = item_data['price']
        net_price = gross_price / (1 + vat_rate)
        item_total_price = net_price * item_data['quantity']
        nettó_price += item_total_price
        cart_items.append({
            'id': item_id,
            'name': item_data['name'],
            'quantity': item_data['quantity'],
            'price': gross_price,
            'net_price': round(item_total_price, 2),
            'total_price': round(item_total_price * (1 + vat_rate), 2)
        })

    bruttó_price = nettó_price * (1 + vat_rate)

    # --------------------------
    # Kupon kezelés
    # --------------------------
    coupon = None
    discount_amount = 0
    coupon_id = request.session.get("coupon_id")
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            if coupon.is_valid(bruttó_price):
                if coupon.discount_type == "percent":
                    discount_amount = bruttó_price * coupon.discount_value / 100
                else:
                    discount_amount = coupon.discount_value
            else:
                request.session.pop("coupon_id", None)
                coupon = None
        except Coupon.DoesNotExist:
            request.session.pop("coupon_id", None)
            coupon = None

    összesen_price = bruttó_price + shipping_cost - discount_amount

    context = {
        'title': 'Rendelés Véglegesítése!',
        'cart_items': cart_items,
        'nettó_price': round(nettó_price, 2),
        'bruttó_price': round(bruttó_price, 2),
        'összesen_price': round(összesen_price, 2),
        'shipping_cost': round(shipping_cost, 2),
        'coupon': coupon,
        'discount_amount': round(discount_amount, 2)
    }

    return render(request, "shop/checkout.html", context)




def create_order(request):
    if request.method == "POST":
        try:
            # --- Get form data and sanitize input ---
            name = request.POST.get("name", "").strip()
            email = request.POST.get("email", "").strip()
            payment_method = request.POST.get("payment_method", "").strip()
            company = request.POST.get("company", "").strip()
            tax = request.POST.get("tax", "").strip()
            billing_address = request.POST.get("billing_address", "").strip()
            shipping_address = request.POST.get("shipping_address", "").strip()
            phone = request.POST.get("phone", "").strip()
            email_trans = request.POST.get("email_trans", "").strip()
            personal = request.POST.get("checkbox", "") == "on"

            required_fields = [name, email, payment_method, billing_address, phone, email_trans, personal]
            if not all(required_fields):
                messages.error(request, 'Sikertelen megrendelés! Kérlek töltsd ki a kötelező mezőket!')
                return redirect('checkout')

            cart = request.session.get("cart", {})

            # --- Check unavailable items ---
            unavailable_items = []
            for product_id_str, item_data in cart.items():
                try:
                    product_id = int(product_id_str)
                    product = get_object_or_404(Product, id=product_id)
                except ValueError:
                    continue

                if not product.available or product.stock < item_data["quantity"]:
                    unavailable_items.append(product.name)

            if unavailable_items:
                messages.error(request, f"Ezek a termékek jelenleg nem elérhetők: {', '.join(unavailable_items)}")
                for product_name in unavailable_items:
                    for pid, item in list(cart.items()):
                        if item["name"] == product_name:
                            del cart[pid]
                request.session["cart"] = cart
                return redirect("cart_view")

            # --- Convert numbers ---
            state_num = request.POST.get("state_num")
            state_num = int(state_num) if state_num and state_num.isdigit() else None

            door_num = request.POST.get("door_num")
            door_num = int(door_num) if door_num and door_num.isdigit() else None

            # --- Price calculations ---
            nettó_price = 0
            vat_rate = 0.27
            shipping_cost_obj = get_object_or_404(ShippingCost, id=1)
            shipping_cost = shipping_cost_obj.cost

            for product_id_str, item_data in cart.items():
                product_id = int(product_id_str)
                product = get_object_or_404(Product, id=product_id)
                gross_price = item_data["price"]
                net_price = gross_price / (1 + vat_rate)
                item_total_price = net_price * item_data["quantity"]
                nettó_price += item_total_price

            bruttó_price = nettó_price * (1 + vat_rate)

            # --- Coupon logic (outside loop!) ---
            coupon = None
            discount_amount = 0
            coupon_id = request.session.get("coupon_id")
            if coupon_id:
                try:
                    coupon = Coupon.objects.get(id=coupon_id, active=True)
                    if coupon.is_valid(bruttó_price):
                        if coupon.discount_type == "percent":
                            discount_amount = bruttó_price * coupon.discount_value / 100
                        else:
                            discount_amount = coupon.discount_value

                        coupon.used_count += 1
                        coupon.save()
                    else:
                        request.session.pop("coupon_id", None)
                        coupon = None
                except Coupon.DoesNotExist:
                    request.session.pop("coupon_id", None)
                    coupon = None

            összesen_price = bruttó_price + shipping_cost - discount_amount

            # --- Create Order ---
            order = Order.objects.create(
                name=name,
                email=email,
                order_id=uuid.uuid4(),
                payment_method=payment_method,
                all_cost=összesen_price,
                tax=vat_rate,
                shipping_cost=shipping_cost_obj,
                brutto_price=bruttó_price,
                net_price=nettó_price,
                coupon=coupon,
                discount_amount=discount_amount
            )

            # --- Create Order Items ---
            for product_id_str, item in cart.items():
                product_id = int(product_id_str)
                product = get_object_or_404(Product, id=product_id)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=item["name"],
                    quantity=item["quantity"],
                    price=item["price"],
                )

                # --- Update stock ---
                product.stock -= item["quantity"]
                if product.stock <= 0:
                    product.stock = 0
                    product.available = False
                product.save()

            # --- Create Billing Address ---
            BillingAddress.objects.create(
                order=order,
                company=company,
                tax=tax,
                address=billing_address,
                created_at=timezone.now(),
                completed=timezone.now(),
                payment_deadline=timezone.now(),
            )

            # --- Create Shipping Address ---
            ShippingAddress.objects.create(
                order=order,
                address=shipping_address,
                phone=phone,
                state_num=state_num,
                door_num=door_num,
                email=email_trans,
                personal=personal,
            )

            # --- Clear cart session ---
            request.session["cart"] = {}
            messages.success(request, 'Sikeres megrendelés!')

            # --- Send emails ---
            html = render_to_string("shop/order_email.html", {
                "title": "Rendelése megérkezett!",
                "order": order,
                "items": order.items.all(),
                "customer_name": name,
                "total": összesen_price,
                "payment_method": payment_method,
                "shipping_address": shipping_address,
                "billing_address": billing_address,
                "year": datetime.now().year,
            })

            msg = EmailMultiAlternatives(
                subject="Rendelés visszaigazolása",
                body="A leveled HTML-t tartalmaz.",
                from_email="noreply@sussmann.hu",
                to=[email],
            )
            msg.attach_alternative(html, "text/html")
            msg.send()

            send_mail(
                subject="Új megrendelés érkezett",
                message=f"Egy új rendelés érkezett a webáruházba.\nRendelő neve: {name}\nEmail: {email}",
                from_email="noreply@sussmann.hu",
                recipient_list=["notices@sussmann.hu"],
                fail_silently=False,
            )

            return JsonResponse({"success": True, "message": "Sikeres megrendelés!"})

        except Exception as e:
            print("Error in create_order:", str(e))
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
