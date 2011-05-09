          # -*- coding: utf-8 -*-
from django.forms.widgets import RadioSelect
from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django import forms
from models import Cash, TYPE_CHOICES
from cart.models import Client

class ClientForm(ModelForm):
    name = forms.CharField(label='Имя*',error_messages={'required': 'Имя обязательно для заполнения'})
    phone = forms.CharField(label='Телефон*', error_messages={'required': 'Телефон обязателен для заполнения'})
    address = forms.CharField(label='Адрес', widget=forms.Textarea(attrs={'rows':'2'}), required=False)
    class Meta:
        model = Client
        exclude = ('cart', 'referrer', 'tracking_status', 'last_user', 'change_log')
        widgets = {
            'delivery' : RadioSelect(),
        }

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row = u'<tr%(html_class_attr)s><th>%(label)s</th><td colspan="2" class="text">%(errors)s%(field)s%(help_text)s</td></tr>',
            error_row = u'<tr><td colspan="2"> class="send_input"%s</td></tr>',
            row_ender = u'</td></tr>',
            help_text_html = u'<br />%s',
            errors_on_separate_row = False)

class BaseProductFormset(BaseInlineFormSet):
    def clean(self):
        self.validate_unique()
        products = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if form.cleaned_data:
                product = form.cleaned_data['product']
                if product in products:
                    raise ValidationError('test')
                products.append(product)

class CashForm(ModelForm):
    class Meta:
        model = Cash
        exclude = ('balance')

class BalanceForm(forms.Form):
    from_type = forms.ChoiceField(choices=TYPE_CHOICES)
    to_type = forms.ChoiceField(choices=TYPE_CHOICES)
    amount = forms.DecimalField()

