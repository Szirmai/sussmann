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

def cart_view(request):
    cart = request.session.get('cart', {})  # Get the cart from the session
    cart_items = []
    nettó_price = 0
    shipping_cost = get_object_or_404(ShippingCost, id=1).cost
    vat_rate = 0.27

    # Calculate total price for each item based on quantity
    for item_id, item_data in cart.items():
        item = Product.objects.get(id=item_id)  # Get the product from the database
        gross_price = item_data['price']  # Gross price from the database
        vat_rate = 0.27  # VAT rate (27% for Hungary)
        
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

    # Calculate Összesen (Total) including shipping
    összesen_price = bruttó_price + shipping_cost

    # Send the cart data to the template
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'nettó_price': round(nettó_price, 2),
        'bruttó_price': round(bruttó_price, 2),
        'shipping_cost': shipping_cost,
        'összesen_price': round(összesen_price, 2),
    })


def checkout(request):
    cart = request.session.get('cart', {})  # Get the cart from the session
    cart_items = []
    nettó_price = 0
    shipping_cost = get_object_or_404(ShippingCost, id=1).cost
    vat_rate = 0.27  # VAT rate (27% for Hungary)

    # Calculate total price for each item based on quantity
    for item_id, item_data in cart.items():
        item = get_object_or_404(Product, id=item_id)  # Get the product from the database
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

    # Calculate Összesen (Total) including shipping
    összesen_price = bruttó_price + shipping_cost

    title = 'Rendelés Véglegesítése!'

    context = {
        'title': title,
        'cart_items': cart_items,
        'nettó_price': round(nettó_price, 2),
        'bruttó_price': round(bruttó_price, 2),
        'összesen_price': round(összesen_price, 2),
        'shipping_cost': round(shipping_cost, 2)
    }

    return render(request, "shop/checkout.html", context)



def create_order(request):
    if request.method == "POST":
        try:
            # Get form data and sanitize input
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

            required_fields = [name, email, payment_method, billing_address, phone, email_trans]
            if not all(required_fields):
                messages.error(request, 'Sikertelen megrendelés! Kérlek Töltsd ki a kötelező mezőket!!! *-gal vannak jelölve!')
                return redirect('checkout')
                

            # Convert numbers properly
            state_num = request.POST.get("state_num")
            state_num = int(state_num) if state_num and state_num.isdigit() else None

            door_num = request.POST.get("door_num")
            door_num = int(door_num) if door_num and door_num.isdigit() else None

            # Retrieve cart data
            cart = request.session.get("cart", {})

            # Price calculations
            nettó_price = 0
            shipping_cost_obj = get_object_or_404(ShippingCost, id=1)  # ✅ ShippingCost objektum
            shipping_cost = shipping_cost_obj.cost
            vat_rate = 0.27  # VAT rate (27% for Hungary)

            for product_id_str, item_data in cart.items():
                try:
                    product_id = int(product_id_str)  # ✅ Stringből int konvertálás
                    product = get_object_or_404(Product, id=product_id)  # ✅ Termék lekérése
                except ValueError:
                    print(f"Hibás product ID: {product_id_str}")  # Debugging
                    continue  # Ha a termék ID rossz, kihagyjuk ezt az elemet
                
                gross_price = item_data["price"]
                net_price = gross_price / (1 + vat_rate)
                item_total_price = net_price * item_data["quantity"]
                nettó_price += item_total_price

            bruttó_price = nettó_price * (1 + vat_rate)
            összesen_price = bruttó_price + shipping_cost

            # Create the order
            order = Order.objects.create(
                name=name,
                email=email,
                order_id=uuid.uuid4(),
                payment_method=payment_method,
                all_cost=összesen_price,
                tax=vat_rate,
                shipping_cost=shipping_cost_obj,
                brutto_price=bruttó_price,
                net_price=nettó_price,  # 🔄 Javítva (net_price helyett nettó_price kell)
            )

            # Create order items
            for product_id_str, item in cart.items():
                try:
                    product_id = int(product_id_str)  # ✅ Konverzió
                    product = get_object_or_404(Product, id=product_id)  # ✅ Helyesen lekérve a termék
                except ValueError:
                    continue  # Ha valamiért nem sikerül, kihagyjuk az elemet
                
                OrderItem.objects.create(
                    order=order,
                    product=product,  # ✅ Most már minden OrderItem-hez lesz termék
                    product_name=item["name"],
                    quantity=item["quantity"],
                    price=item["price"],
                )

            # Create billing address
            BillingAddress.objects.create(
                order=order,
                company=company,
                tax=tax,
                address=billing_address,
                created_at=timezone.now(),
                completed=timezone.now(),
                payment_deadline=timezone.now(),
            )

            # Create shipping address
            ShippingAddress.objects.create(
                order=order,
                address=shipping_address,
                phone=phone,
                state_num=state_num,
                door_num=door_num,
                email=email_trans,
                personal=personal,
            )

            # Clear the cart session
            request.session["cart"] = {}

            messages.success(request, 'Sikeres megrendelés!')
            # innen kell emilt kuldeni ....
            return JsonResponse({"success": True, "message": "Sikeres megrendelés!"})  # Return JSON response
        
        except Exception as e:
            print("Error in create_order:", str(e))  # Log error in the Django terminal
            return JsonResponse({"success": False, "error": str(e)}, status=500)  # Return JSON error response

    messages.error(request, 'Sikertelen megrendelés!')
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)