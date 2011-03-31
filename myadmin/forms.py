          # -*- coding: utf-8 -*-
from django.forms.widgets import CheckboxSelectMultiple, RadioSelect
from cart.models import Client, STATUS_CHOICES
from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django import forms
from models import Cash, TYPE_CHOICES
from cart.models import Client

class ClientForm(ModelForm):
    name = forms.CharField(label='Имя*',error_messages={'required': 'Имя обязательно для заполнения'})
    phone = forms.CharField(label='Телефон*', error_messages={'required': 'Телефон обязателен для заполнения'})
    class Meta:
        model = Client
        exclude = ('cart', 'referrer')
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

def get_status():
    STATUS_CHOICES = (
        ('PROCESS', 'Обработать(%s)' % Client.objects.filter(status='PROCESS').count()),
        ('POSTSEND', 'Отправить почтой(%s)' % Client.objects.filter(status='POSTSEND').count()),
        ('POSTSENDED', 'Отправлено почтой(%s)' % Client.objects.filter(status='POSTSENDED').count()),
        ('COURIER_SEND', 'Отправить курьером(%s)' % Client.objects.filter(status='COURIER_SEND').count()),
        ('COURIER_TAKE', 'Передано курьеру(%s)' % Client.objects.filter(status='COURIER_TAKE').count()),
        ('BUYER_TAKE', 'Передано покупателю(%s)' % Client.objects.filter(status='BUYER_TAKE').count()),
        ('WAYT_PRODUCT', 'Ожидание поступления товара(%s)' % Client.objects.filter(status='WAYT_PRODUCT').count()),
        ('CHANGE', 'Обменять(%s)' % Client.objects.filter(status='CHANGE').count()),
        ('BACK', 'Вернуть(%s)' % Client.objects.filter(status='BACK').count()),
        ('CONTACT_AT', 'Связаться в назначенное время(%s)' % Client.objects.filter(status='CONTACT_AT').count()),
        ('REFUSED', 'Снятие заявки клиентом(%s)' % Client.objects.filter(status='REFUSED').count()),
        ('CASH_IN', 'Деньги внесены(%s)' % Client.objects.filter(status='CASH_IN').count()),
    )
    return STATUS_CHOICES

class StatusForm(forms.Form):
    status = forms.MultipleChoiceField(widget=CheckboxSelectMultiple,choices=get_status)


class CashForm(ModelForm):
    class Meta:
        model = Cash
        exclude = ('balance')

class BalanceForm(forms.Form):
    from_type = forms.ChoiceField(choices=TYPE_CHOICES)
    to_type = forms.ChoiceField(choices=TYPE_CHOICES)
    amount = forms.DecimalField()

