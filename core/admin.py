from django.contrib import admin

from .models import Order, Item, OrderItem

# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price')

admin.site.register(Order)
admin.site.register(OrderItem)