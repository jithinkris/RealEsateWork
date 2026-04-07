from functools import wraps

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404, redirect, render

from .models import Admin, Contact, Installment, Property, PropertyImage, PropertySale, Requirement, User


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_id'):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# Create your views here.


def home(request):
    properties = Property.objects.filter(status='available').order_by('-created_at')
    return render(request, 'home.html', {'properties': properties})


def contact(request):
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            requirement_type=request.POST.get('requirement_type'),
            message=request.POST.get('message')
        )

        messages.success(request, "✅ Your request has been submitted successfully!")
        return redirect('contact')   # PRG pattern

    return render(request, 'contact.html')


def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # ✅ Check empty fields
        if not name or not email or not phone or not password:
            return render(request, 'register.html', {'error': 'All fields are required'})

        # ✅ Email exists
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already registered'})

        # ✅ Password match
        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        # ✅ Password strength
        if len(password) < 6:
            return render(request, 'register.html', {'error': 'Password must be at least 6 characters'})

        # ✅ Save user (hashed password)
        User.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=make_password(password)
        )

        return render(request, 'register.html', {'success': 'Registration successful! You can login now.'})

    return render(request, 'register.html')



from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from .models import User

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

            # ✅ check password
            if check_password(password, user.password):

                # ✅ check active status
                if not user.status:
                    return render(request, 'login.html', {'error': 'Account inactive'})

                # ✅ create session
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name

                return redirect('user_home')

            else:
                return render(request, 'login.html', {'error': 'Invalid password'})

        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'User not found'})

    return render(request, 'login.html')



def logout_view(request):
    request.session.flush()   # 🔥 clears session
    return redirect('/login/')


from .models import Property

@user_required
def user_home(request):
    query = request.GET.get('q')

    properties = Property.objects.filter(status='available').order_by('-created_at')

    if query:
        properties = properties.filter(location__icontains=query)

    return render(request, 'user_home.html', {
        'properties': properties
    })

@user_required
def user_contact(request):
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            requirement_type=request.POST.get('requirement_type'),
            message=request.POST.get('message')
        )

        return render(request, 'user-contact.html', {
            'success': 'Request submitted successfully!'
        })

    return render(request, 'user-contact.html')




from .models import Requirement, Property, User

@user_required
def submit_requirement(request):
    if request.method == "POST":
        user = User.objects.get(id=request.session['user_id'])

        property_obj = Property.objects.get(id=request.POST.get('property_id'))

        Requirement.objects.create(
            user=user,
            property=property_obj,
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            message=request.POST.get('message'),
        )

        return redirect('user_home')




############################### Admin Views ###############################


from django.contrib.auth.hashers import check_password
from .models import Admin

def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            admin = Admin.objects.get(email=email)

            if not admin.is_active:
                return render(request, 'admin_login.html', {'error': 'Admin inactive'})

            if check_password(password, admin.password):
                request.session['admin_id'] = admin.id
                request.session['admin_name'] = admin.name
                return redirect('admin_dashboard')
            else:
                return render(request, 'admin_login.html', {'error': 'Invalid password'})

        except Admin.DoesNotExist:
            return render(request, 'admin_login.html', {'error': 'Admin not found'})

    return render(request, 'admin_login.html')



from .models import Contact



def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')






@admin_required
def admin_dashboard(request):

    query = request.GET.get('q')

    contacts = Contact.objects.all().order_by('-created_at')

    if query:
        contacts = contacts.filter(name__icontains=query) | contacts.filter(phone__icontains=query)

    context = {
        'contacts': contacts,
        'total': Contact.objects.count(),
        'waiting': Contact.objects.filter(status='waiting').count(),
        'contacted': Contact.objects.filter(status='contacted').count(),
        'closed': Contact.objects.filter(status='closed').count(),
    }

    return render(request, 'admin_dashboard.html', context)



@admin_required
def update_status(request, id):
    if request.method == "POST":
        contact = Contact.objects.get(id=id)
        contact.status = request.POST.get('status')
        contact.save()

    return redirect('admin_dashboard')




from .models import Property, PropertyImage,Requirement

@admin_required
def add_property(request):

    if request.method == "POST":

        property_obj = Property.objects.create(
            title=request.POST.get('title'),
            property_type=request.POST.get('property_type'),
            price=request.POST.get('price') or None,
            location=request.POST.get('location'),
            description=request.POST.get('description'),

            area=request.POST.get('area') or None,
            bedrooms=request.POST.get('bedrooms') or None,
            bathrooms=request.POST.get('bathrooms') or None,

            parking=True if request.POST.get('parking') else False,
            furnished=True if request.POST.get('furnished') else False,

            status=request.POST.get('status'),
        )

        # 📸 handle multiple images
        images = request.FILES.getlist('images')
        for img in images:
            PropertyImage.objects.create(property=property_obj, image=img)

        return redirect('admin_dashboard')

    return render(request, 'add_property.html')



@admin_required
def property_list(request):

    properties = Property.objects.all()

    return render(request, 'property-list.html', {
        'properties': properties
    })


@admin_required
def property_detail(request, id):

    property_obj = Property.objects.get(id=id)

    return render(request, 'property_detail.html', {
        'property': property_obj
    })


@admin_required
def edit_property(request, id):
    property_obj = Property.objects.get(id=id)

    if request.method == "POST":
        property_obj.title = request.POST.get('title')
        property_obj.price = request.POST.get('price')
        property_obj.location = request.POST.get('location')
        property_obj.save()

        return redirect('property_list')

    return render(request, 'edit_property.html', {'property': property_obj})



@admin_required
def delete_property(request, id):

    Property.objects.get(id=id).delete()
    return redirect('property_list')


@admin_required
def property_leads(request, id):

    property_obj = Property.objects.get(id=id)
    leads = Requirement.objects.filter(property=property_obj)

    return render(request, 'property_leads.html', {
        'property': property_obj,
        'leads': leads
    })



from .models import Property, PropertyImage

@admin_required
def edit_property(request, id):
    property_obj = Property.objects.get(id=id)

    if request.method == "POST":

        property_obj.title = request.POST.get('title')
        property_obj.property_type = request.POST.get('property_type')
        property_obj.price = request.POST.get('price') or None
        property_obj.location = request.POST.get('location')
        property_obj.description = request.POST.get('description')

        property_obj.area = request.POST.get('area') or None
        property_obj.bedrooms = request.POST.get('bedrooms') or None
        property_obj.bathrooms = request.POST.get('bathrooms') or None

        property_obj.parking = True if request.POST.get('parking') else False
        property_obj.furnished = True if request.POST.get('furnished') else False

        property_obj.status = request.POST.get('status')

        property_obj.save()

        # 📸 ADD NEW IMAGES
        images = request.FILES.getlist('images')
        for img in images:
            PropertyImage.objects.create(property=property_obj, image=img)

        return redirect('property_list')

    return render(request, 'edit_property.html', {
        'property': property_obj
    })




from django.contrib.auth.hashers import make_password, check_password
from .models import Admin

@admin_required
def edit_admin(request):

    admin = Admin.objects.get(id=request.session['admin_id'])

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        admin.name = name
        admin.email = email

        # 🔐 Change password only if entered
        if old_password and new_password:
            if check_password(old_password, admin.password):
                admin.password = make_password(new_password)
            else:
                return render(request, 'edit_admin.html', {
                    'admin': admin,
                    'error': 'Old password incorrect'
                })

        admin.save()

        return render(request, 'edit_admin.html', {
            'admin': admin,
            'success': 'Profile updated successfully'
        })

    return render(request, 'edit_admin.html', {'admin': admin})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import PropertyImage


@admin_required
@admin_required
def delete_image(request, id):
    img = get_object_or_404(PropertyImage, id=id)


    img.delete()  # delete DB record also

    messages.success(request, "Image deleted successfully")

    return redirect('property_list')




from django.shortcuts import render, get_object_or_404
from .models import PropertySale, Installment


@admin_required
@admin_required
def sold_properties(request):
    sales = PropertySale.objects.select_related('property', 'buyer').all().order_by('-sale_date')
    return render(request, 'sold_properties.html', {'sales': sales})



@admin_required
@admin_required
def installments_list(request):
    installments = Installment.objects.select_related('sale__property', 'sale__buyer').all().order_by('-payment_date')
    return render(request, 'installments.html', {'installments': installments})


@admin_required
@admin_required
def sale_detail(request, sale_id):
    sale = get_object_or_404(PropertySale, id=sale_id)
    installments = sale.installments.all().order_by('-payment_date')

    context = {
        'sale': sale,
        'installments': installments
    }
    return render(request, 'sale_detail.html', context)




from django.shortcuts import render, redirect
from .models import PropertySale, Property, User

@admin_required
@admin_required
def add_sale(request):
    if request.method == "POST":
        property_id = request.POST.get('property')
        buyer_id = request.POST.get('buyer')
        buyer_name = request.POST.get('buyer_name')
        total_price = request.POST.get('total_price')
        advance_paid = request.POST.get('advance_paid')

        property_obj = Property.objects.get(id=property_id)
        buyer = None
        if buyer_id and buyer_id != 'other':
            buyer = User.objects.get(id=buyer_id)

        properties = Property.objects.filter(status='available')
        users = User.objects.all()

        if not buyer and not buyer_name:
            return render(request, 'add_sale.html', {
                'properties': properties,
                'users': users,
                'error': 'Please select an existing buyer or enter a buyer name.'
            })

        remaining = int(total_price) - int(advance_paid)

        PropertySale.objects.create(
            property=property_obj,
            buyer=buyer,
            buyer_name=buyer_name if not buyer else None,
            total_price=total_price,
            advance_paid=advance_paid,
            remaining_amount=remaining
        )

        return redirect('sold_properties')

    properties = Property.objects.filter(status='available')
    users = User.objects.all()

    return render(request, 'add_sale.html', {
        'properties': properties,
        'users': users
    })



from .models import Installment, PropertySale

@admin_required
@admin_required
def add_installment(request, sale_id):
    sale = PropertySale.objects.get(id=sale_id)

    if request.method == "POST":
        amount = request.POST.get('amount')
        method = request.POST.get('payment_method')

        Installment.objects.create(
            sale=sale,
            amount=amount,
            payment_method=method
        )

        return redirect('sale_detail', sale_id=sale.id)

    return render(request, 'add_installment.html', {'sale': sale})