from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product, Subsc
from Home.models import DealOfMonth, YouTube, Quotes, Team, Category
from datetime import date
from .forms import ContactForm
from django.contrib import messages
from django.http import JsonResponse

def home_view(request):
    products = Product.objects.all().order_by('-created_at')[0:3]
    deals = DealOfMonth.objects.filter(exp_date__gte = date.today()).order_by('-created_at')[:1]
    youtubes = YouTube.objects.all().order_by('-created_at')[0:1]
    quotes = Quotes.objects.all().order_by('-created_at')
    title = 'Home'

    context = {'products': products,
               'deals': deals,
               'youtubes': youtubes,
               'quotes': quotes,
               'title': title,
               }
    return render(request, 'index.html', context)


def About(request):
    quotes = Quotes.objects.all().order_by('-created_at')
    teams = Team.objects.filter(on=True).order_by('-created_at')

    title = 'Rólunk'
    context = {
        'title': title,
        'quotes': quotes,
        'teams': teams,
    }

    return render(request, 'about.html', context)

def ProductSingle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    similar_products = Product.objects.filter(categories=product.categories).exclude(id=product_id)[0:3] 
    context = {'product': product,
               'similar_products': similar_products,
               }
    return render(request, 'single-product.html', context)


def Shop(request):
    product = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    print(product)
    title = 'Bolt'
    context= {'products': product,
              'categories': categories,
              'title': title
              }
    return render(request, 'shop.html', context)


def CatPage(request, name):
    products = Product.objects.filter(categories__name=name)
    title = name
    context = {'products': products,
               'title': title,
               }
    
    return render(request, 'shop.html', context)

def Contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('success')  # Success page
    else:
        form = ContactForm() 
    
    context = {'form': form}
    return render(request, 'contact.html', context)

def Success(request):
    title = 'Sikeres Művelet!'
    title1 = 'A művelet sikeresen végrehajtva!'
    back = 'Vissza a kezdőoldalra!'

    context = {
        'title': title,
        'title1': title1,
        'back': back,
    }
    return render(request, 'success.html', context)

def subscribe_view(request):
    if request.method == 'POST':
        subsc = request.POST.get("email", "").strip()

        Subsc.objects.create(
            email=subsc
        )
        messages.success(request, 'A feliratkozás megtörtént!')

    return redirect('home')
