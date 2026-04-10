"""
URL configuration for realestate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from core.views import *


urlpatterns = [
    path('Admin/', admin.site.urls),

    ## Admin
    path('admin/login/', admin_login, name='admin_login'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/logout/', admin_logout, name='admin_logout'),
    path('admin/update-status/<int:id>/', update_status),
    path('admin/profile/', edit_admin, name='edit_admin'),
    
    path('admin/add-property/', add_property, name='add_property'),
    path('admin/properties/', property_list, name='property_list'),
    path('admin/property/<int:id>/', property_detail),
    path('admin/property/edit/<int:id>/', edit_property),
    path('admin/property/delete/<int:id>/', delete_property),
    path('admin/property/leads/<int:id>/', property_leads),
    path('admin/delete-image/<int:id>/', delete_image, name='delete_image'),
    path('admin/sold-properties/', sold_properties, name='sold_properties'),
    path('admin/sales/', sold_properties, name='sales'),
    path('admin/installments/', installments_list, name='installments'),
    path('admin/sale/<int:sale_id>/', sale_detail, name='sale_detail'),
    path('admin/add-sale/', add_sale, name='add_sale'),
    path('admin/add-installment/<int:sale_id>/', add_installment, name='add_installment'),


    ## User
    path('user/home/', user_home, name='user_home'),
    path('user/contact/', user_contact, name='user_contact'),
    path('submit-requirement/', submit_requirement, name='submit_requirement'),


    ### Guest
    path('', home, name='home'),
    path('contact/', contact, name='contact'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    ## for health
    path('health/', health)


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
