from django.db import models

# Create your models here.
## user model for storing user information and authentication details

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    status=models.IntegerField(default=1)  # 1 for active, 0 for inactive



    def __str__(self):
        return self.email
    



class Contact(models.Model):

    REQUIREMENT_CHOICES = [
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('plot', 'Plot / Land'),
        ('commercial', 'Commercial'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    requirement_type = models.CharField(
        max_length=20,
        choices=REQUIREMENT_CHOICES
    )

    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('waiting', 'Waiting'),
            ('contacted', 'Contacted')
        ],
        default='waiting'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.requirement_type}"
    



class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    


class Property(models.Model):

    PROPERTY_TYPE = [
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('plot', 'Plot / Land'),
        ('commercial', 'Commercial'),
    ]

    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE)

    price = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=200)

    description = models.TextField(null=True, blank=True)

    area = models.IntegerField(null=True, blank=True)  # sq ft
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.IntegerField(null=True, blank=True)

    parking = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('sold', 'Sold'),
            ('upcoming', 'Upcoming')
        ],
        default='available'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property/')

    def __str__(self):
        return self.property.title
    




class Requirement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=[
            ('waiting', 'Waiting'),
            ('contacted', 'Contacted'),
            ('closed', 'Closed')
        ],
        default='waiting'
    )

    created_at = models.DateTimeField(auto_now_add=True)



class PropertySale(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    buyer_name = models.CharField(max_length=100, null=True, blank=True)

    total_price = models.IntegerField()
    advance_paid = models.IntegerField(default=0)
    remaining_amount = models.IntegerField()

    sale_date = models.DateField(auto_now_add=True)

    def __str__(self):
        buyer_label = self.buyer.name if self.buyer else self.buyer_name or 'Unknown Buyer'
        return f"{self.property.title} - {buyer_label}"
    



class Installment(models.Model):
    sale = models.ForeignKey(PropertySale, on_delete=models.CASCADE, related_name='installments')

    amount = models.IntegerField()
    payment_date = models.DateField(auto_now_add=True)

    PAYMENT_METHOD = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer')
    ]

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)

    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.sale.property.title} - ₹{self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        sale = self.sale
        total_paid = sum(i.amount for i in sale.installments.all()) + sale.advance_paid
        sale.remaining_amount = sale.total_price - total_paid
        sale.save()