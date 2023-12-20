#from re import template
from cmath import log
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import generic
from django.contrib import messages
from .forms import CheckOutForm
import stripe, logging


stripe.api_key = settings.STRIPE_SECRET_KEY

from .models import Order, Item, OrderItem, BillingAddress, Payment

# class ItemListView(generic.ListView):

#     model = Item
#     context_object_name = 'item_list'
#     queryset = Item.objects.all()
#     template_name = 'core/home-page.html'
#     paginate_by = 5

class CheckoutView(generic.View):
    def get(self, *args, **kwargs):
        form = CheckOutForm()
        context = {
            'form' : form
        }
        return render(self.request, 'core/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckOutForm(self.request.POST or None)
        print(self.request.POST)
        try:
            order = Order.objects.get(user = self.request.user, ordered = False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                zip = form.cleaned_data.get("zip")
                country = form.cleaned_data.get('country')
                #same_billing_address = form.cleaned_data.get('same_billing_address')
                #save_info = form.cleaned_data.get('save_info')
                billing_address = BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    country = country,
                    zip  = zip

                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                payment_option = form.cleaned_data.get('payment_option') 
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, 'you do not have any active order.')
            return redirect('core:order-summary')       


class PaymentView(generic.View):
    def get(self, *args, **kwargs):
        return render(self.request, 'core/payment.html')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user = self.request.user, ordered = False)
        token = self.request.POST.get('stripeToken')
        amount = order.get_total() * 100
        
        try:
            charge = stripe.Charge.create(
                amount = amount,
                currency = 'eur',
                source = token
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = amount
            payment.save()

            #assign the payment to order
            order.ordered = True
            order.Payment = payment
            order.save()
            messages.success(self.request, 'your order was successful!')
            return redirect('/')
        except stripe.error.CardError as e:
            logging.error("A payment error occurred: {}".format(e.user_message))
            return redirect('/')
        except stripe.error.InvalidRequestError:
            logging.error("An invalid request occurred.")
            return redirect('/')
        except stripe.error.AuthenticationError:
            logging.error("Not authenticated.")
            return redirect('/')
        except Exception:
            logging.error("Another problem occurred, maybe unrelated to Stripe.")
            return redirect('/')
        

class HomeView(generic.ListView):
    model = Item
    context_object_name = 'item_list'
    queryset = Item.objects.all()
    paginate_by = 10
    template_name = "core/home.html"

class OrderSummaryView(LoginRequiredMixin, generic.View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user = self.request.user, ordered = False)
            context = {
                'object' : order
            }
            return render(self.request, 'core/order_summary.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, 'you do not have any active order.')
            return redirect('/')
        
    #model = Order
    #template_name = 'home.html'


class ItemDetailView(generic.DetailView):
    model = Item
    context_object_name = 'item_details'
    queryset = Item.objects.all()
    paginate_by = 10
    template_name = "core/product.html"

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug = slug)
    order_item, created = OrderItem.objects.get_or_create(item = item,
    user = request.user,
    ordered = False)
    order_qs = Order.objects.filter(user = request.user, ordered = False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug = item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'this item qunatity is updated.')
            return redirect('core:order-summary')
        else:           
            order.items.add(order_item)
            messages.info(request, 'this item is added to your cart.')
            return redirect('core:order-summary')

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user = request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        messages.info(request, 'this item qunatity is updated.')
    return redirect('core:order-summary')

@login_required
def remove_from_cart(request, slug):

    item = get_object_or_404(Item, slug = slug)
    order_qs = Order.objects.filter(user = request.user, ordered = False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug = item.slug).exists():
            order_item= OrderItem.objects.filter(item = item,
                    user = request.user,
                    ordered = False)[0]
            order.items.remove(order_item)
            messages.info(request, 'this item is removed from your cart.')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'this item is not in your cart.')
            return redirect('core:product',slug = slug)

    else:
        messages.info(request, 'you do not have any active order.')
        return redirect('core:product', slug = slug)


@login_required
def remove_single_item_from_cart(request, slug):

    item = get_object_or_404(Item, slug = slug)
    order_qs = Order.objects.filter(user = request.user, ordered = False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug = item.slug).exists():
            order_item= OrderItem.objects.filter(item = item,
                    user = request.user,
                    ordered = False)[0]
            if order_item.quantity >1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, 'this item was updated.')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'this item is not in your cart.')
            return redirect('core:product', slug = slug)

    else:
        messages.info(request, 'you do not have any active order.')
        return redirect('core:product', slug = slug)





