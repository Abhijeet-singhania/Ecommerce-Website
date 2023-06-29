from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.db.models import Sum

# from django.contrib.postgres.fields import ArrayField

#  value to be changed according to needs
LABEL_CHOICES = (
    ('New', 'New'),
    ('Top', 'Top'),
    ('Out of stock', 'Out of stock')
)


class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(default='xyz.jpg')

    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
class Review(models.Model):
    # product = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    verified_status = models.BooleanField(default=True)
    rating = models.IntegerField()
    review = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    available_stock = models.IntegerField(default=0)
    rating = models.IntegerField()


    def __str__(self):
        return self.title
    
class ItemReviewMapping(models.Model):
    review = models.ForeignKey(Review,on_delete=models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.review.user.username}'s review of {self.item.title}" 
    
class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    def __str__(self):
        return self.item.title


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    delievery_charge = models.IntegerField(default=100)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total
    def get_total_with_delivery(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total+self.delievery_charge
        


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    town = models.CharField(max_length = 100)
    state = models.CharField(max_length = 100)
    contact = models.IntegerField(max_length=12)
    
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"





def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)






    
class ProductCategoryMapping(models.Model):
    product = models.ForeignKey('Item', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'Product: {self.product}, Category: {self.category}'

# class UserProfile(models.Model):
#     user = models.OneToOneField(
#         User, on_delete=models.CASCADE)
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     email = models.EmailField()
#     stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
#     # gender = models.CharField(max_length=10)
#     # age = models.PositiveIntegerField(default=18)
#     verified_status = models.BooleanField(default=True)
#     # status = models.IntegerField(default=1)
#     created = models.DateTimeField(auto_now_add=True)
#     last_updated = models.DateTimeField(auto_now=True)
    

#     def __str__(self):
#         return self.user.username





    

    
# class Product(models.Model):
#     title = models.CharField(max_length=100)
#     price = models.FloatField()
#     discount_price = models.FloatField(blank=True, null=True)
#     label = models.CharField(choices=LABEL_CHOICES, max_length=100)
#     slug = models.SlugField()
#     description = models.TextField()
#     additional_information = models.TextField()
#     image = models.ImageField(upload_to='products/')
#     
#     available_stock = models.IntegerField(default=0)
#     # sizes = ArrayField(models.IntegerField(null=True,blank=True))

#     def __str__(self):
#         return self.title
#     def get_absolute_url(self):
#         return reverse("mainapp:product", kwargs={
#             'slug': self.slug
#         })

#     def get_add_to_cart_url(self):
#         return reverse("mainapp:add-to-cart", kwargs={
#             'slug': self.slug
#         })

#     def get_remove_from_cart_url(self):
#         return reverse("mainapp:remove-from-cart", kwargs={
#             'slug': self.slug
#         })


# class OrderProduct(models.Model):
#     user = models.ForeignKey(User,
#                              on_delete=models.CASCADE)
#     ordered = models.BooleanField(default=False)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.IntegerField(default=1)

#     def __str__(self):
#         return f"{self.quantity} of {self.product.title}"

#     def get_total_item_price(self):
#         return self.quantity * self.product.price

#     def get_total_discount_item_price(self):
#         return self.quantity * self.product.discount_price

#     def get_amount_saved(self):
#         return self.get_total_item_price() - self.get_total_discount_item_price()

#     def get_final_price(self):
#         if self.product.discount_price:
#             return self.get_total_discount_item_price()
#         return self.get_total_item_price()
    
# class Order(models.Model):
#     user = models.ForeignKey(User,
#                              on_delete=models.CASCADE)
#     items = models.ManyToManyField(OrderProduct)
#     ordered_date = models.DateTimeField()
#     ordered = models.BooleanField(default=False)
#     shipping_address = models.ForeignKey(
#         'Address', on_delete=models.SET_NULL, blank=True, null=True)
    
#     payment = models.ForeignKey(
#         'Payment', on_delete=models.SET_NULL, blank=True, null=True)
#     coupon = models.ForeignKey(
#         'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
#     is_delivered = models.BooleanField(default=False)
#     refund_requested = models.BooleanField(default=False)
#     refund_granted = models.BooleanField(default=False)

    

#     def __str__(self):
#         return self.user.username

#     def get_total(self):
#         total = 0
#         for order_item in self.items.all():
#             total += order_item.get_final_price()
#         if self.coupon:
#             total -= self.coupon.amount
#         return total



# class Address(models.Model):
#     user = models.ForeignKey(User,
#                              on_delete=models.CASCADE)
#     street_address = models.CharField(max_length=100)
#     apartment_address = models.CharField(max_length=100)
#     country = CountryField(multiple=False)
#     # state = StateField(multiple = False)
#     zip = models.CharField(max_length=100)
#     default = models.BooleanField(default=False)
#     contact_no = models.CharField(max_length=20)


#     def __str__(self):
#         return self.user.username

#     class Meta:
#         verbose_name_plural = 'Addresses'

# class Payment(models.Model):
#     stripe_charge_id = models.CharField(max_length=50)
#     user = models.ForeignKey(User,
#                              on_delete=models.SET_NULL, blank=True, null=True)
#     amount = models.FloatField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.user.username
    
# class Refund(models.Model):
#     # order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     reason = models.TextField()
#     status = models.BooleanField(default=False)
#     email = models.EmailField()

#     def __str__(self):
#         return f"{self.pk}"


# class Coupon(models.Model):
#     code = models.CharField(max_length=15)
#     amount = models.FloatField()
#     valid_from = models.DateField()
#     valid_till = models.DateField()

#     def __str__(self):
#         return self.code




# # signals
# def userprofile_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         userprofile = UserProfile.objects.create(user=instance)


# post_save.connect(userprofile_receiver, sender=User)


