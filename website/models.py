from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django_countries.fields import CountryField
from django.contrib.auth.models import User

#  value to be changed according to needs
LABEL_CHOICES = (
    ('New', 'New'),
    ('Top', 'Top'),
    ('Out of stock', 'Out of stock')
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    gender = models.CharField(max_length=10)
    age = models.PositiveIntegerField()
    contact_no = models.CharField(max_length=20)
    verified_status = models.BooleanField()
    status = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductCategoryMapping(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'Product: {self.product}, Category: {self.category}'

    
class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    additional_information = models.TextField()
    image = models.ImageField()
    rating = models.IntegerField()

    def __str__(self):
        return self.title


class OrderProduct(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.title}"

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_total_discount_item_price(self):
        return self.quantity * self.product.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
    
class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderProduct)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', on_delete=models.SET_NULL, blank=True, null=True)
    
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    is_delivered = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total



class Address(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    # state = StateField(multiple = False)
    zip = models.CharField(max_length=100)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'

class Payment(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class Refund(models.Model):
    # order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    valid_from = models.DateField()
    valid_till = models.DateField()

    def __str__(self):
        return self.code


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verified_status = models.BooleanField()
    rating = models.IntegerField()
    review = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


# signals
def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=User)


