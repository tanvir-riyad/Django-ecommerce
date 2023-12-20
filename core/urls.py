from django.urls import path
from .views import (HomeView, ItemDetailView, CheckoutView, OrderSummaryView,
 PaymentView, add_to_cart, remove_from_cart, remove_single_item_from_cart)

app_name = 'core'

urlpatterns =[
    path('', HomeView.as_view(), name = 'item-list'),
    path('product/<slug>/', ItemDetailView.as_view(), name = 'product'),
    path('checkout/', CheckoutView.as_view(), name = 'checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name = 'order-summary'),
    path('add_to_cart/<slug>',add_to_cart, name = 'add-to-cart'),
    path('remove_from_cart/<slug>', remove_from_cart, name = 'remove-from-cart'),
    path('payment/', PaymentView.as_view(), name = 'payment'),
    path('remove_single_item_from_cart/<slug>', remove_single_item_from_cart, name = 'remove-single-item-from-cart'),

]
