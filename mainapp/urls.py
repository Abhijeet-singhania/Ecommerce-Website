from django.contrib import admin
from django.urls import path
from mainapp import views
from django.conf.urls.static import static
from django.conf import settings


from .views import (
    item_detail_view,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    # PaymentView,
    AddCouponView,
    RequestRefundView,
    index,
    ProductsView,
    add_to_wishlist,
    WishlistSummaryView,
    remove_from_wishlist,
    add_review,
    AllProductsView
    
)

app_name = 'mainapp'

urlpatterns = [
    path('',index,name = 'index'),
    path('category/', HomeView.as_view(), name='home'),
    path('products/<int:id>', ProductsView, name='products'),
    path('products/', AllProductsView, name='products'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('wishlist-summary/', WishlistSummaryView, name='wishlist-summary'),
    path('product/<slug>/', item_detail_view, name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-to-wishlist/<slug>/', add_to_wishlist, name='add-to-wishlist'),
    path('add-review/<slug>/', add_review, name='add-review'),
    path('add-coupon/', AddCouponView.as_view(http_method_names=['post']), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-from-wishlist/<slug>/', remove_from_wishlist, name='remove-from-wishlist'),
    path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart,name= 'remove-single-item-from-cart'),
    # path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('cart', views.cart, name='cart'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    