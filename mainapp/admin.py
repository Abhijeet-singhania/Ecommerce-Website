from django.contrib import admin
from .models import Category,ProductCategoryMapping,Item,OrderItem,Order,Address,Payment,Refund,Coupon,Review,UserProfile,ItemReviewMapping
# Register your models here.


admin.site.register(Category)
admin.site.register(ProductCategoryMapping)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address)
admin.site.register(UserProfile)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(ItemReviewMapping)
