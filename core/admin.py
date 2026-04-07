from django.contrib import admin
from django.contrib import admin
from .models import *


# Register your models here.


# USER ADMIN
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('status',)


# CONTACT ADMIN
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'requirement_type', 'status', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('requirement_type', 'status')
    ordering = ('-created_at',)


# ADMIN MODEL (your custom admin)
@admin.register(Admin)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('is_active',)


# PROPERTY IMAGE INLINE (VERY IMPORTANT 🔥)
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


# PROPERTY ADMIN
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'price', 'location', 'status', 'created_at')
    search_fields = ('title', 'location')
    list_filter = ('property_type', 'status', 'parking', 'furnished')
    inlines = [PropertyImageInline]


# PROPERTY IMAGE ADMIN (optional separate view)
@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'image')


# REQUIREMENT ADMIN
@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'property', 'phone', 'status', 'created_at')
    search_fields = ('name', 'phone')
    list_filter = ('status',)
    ordering = ('-created_at',)


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 1

@admin.register(PropertySale)
class PropertySaleAdmin(admin.ModelAdmin):
    list_display = ('property', 'buyer', 'total_price', 'advance_paid', 'remaining_amount', 'sale_date')
    inlines = [InstallmentInline]


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ('sale', 'amount', 'payment_method', 'payment_date')