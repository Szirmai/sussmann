from django.contrib import admin
from .models import Product, DealOfMonth, YouTube, Quotes, Team, Category, Contact, Subsc, ProductImage, New, CategoryNew

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

# --- FIX: helyes regisztráció ---
admin.site.register(Product, ProductAdmin)

# --- többi modell ---
admin.site.register(DealOfMonth)
admin.site.register(YouTube)
admin.site.register(Quotes)
admin.site.register(Team)
admin.site.register(Category)
admin.site.register(Contact)
admin.site.register(Subsc)
admin.site.register(ProductImage)
admin.site.register(New)
admin.site.register(CategoryNew)