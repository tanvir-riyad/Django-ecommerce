from django import forms
#from django_countries.fields import CountryField


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

class CheckOutForm(forms.Form):
    street_address = forms.CharField(widget= forms.TextInput(attrs= {
        'placeholder': '1234 main st'
    }))
    apartment_address = forms.CharField(required = False, widget= forms.TextInput(attrs= {
        'placeholder': 'apartment or suite number'
    }))
    #country = CountryField(blank_label = '(select country)')
    zip = forms.CharField()
    same_shipping_address = forms.BooleanField(widget= forms.CheckboxInput())
    save_info = forms.BooleanField(widget= forms.CheckboxInput())
    payment_option = forms.ChoiceField(widget= forms.RadioSelect(), choices = PAYMENT_CHOICES)

