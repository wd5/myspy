          # -*- coding: utf-8 -*-
from django import forms
from catalog.models import Product

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
    def clean_price(self):
        if self.cleaned_data['price'] <= 0:
            raise forms.ValidationError('Price must be greater than zero.')
        return self.cleaned_data['price']

class ProductAddToCartForm(forms.Form):
#    quantity = forms.IntegerField(widget=forms.TextInput(attrs={'size':'2',  'value':'1',
#                                                                'class':'quantity', 'maxlength':'5'}),
#                                  error_messages={'invalid':'Не верное значение.'}, min_value=1)
    product_slug = forms.CharField(widget=forms.HiddenInput())
    # override the default __init__ so we can set the request
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super(ProductAddToCartForm, self).__init__(*args, **kwargs)

    # custom validation to check for cookies
    def clean(self):
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError("Cookies must be enabled.")
        return self.cleaned_data

class OrderForm(forms.Form):
    name = forms.CharField(label='Имя*', error_messages={'required':'Имя обязательно для заполнения'})
    surname = forms.CharField(required=False, label='Фамилия')
    patronymic = forms.CharField(required=False, label='Отчество')
    city = forms.CharField(required=False, label='Город')
    postcode = forms.IntegerField(required=False, label='Индекс')
    phone = forms.CharField(label='Телефон*', error_messages={'required':'Телефон обязателен для заполнения'})
    # Адрес
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':'2'}), label='Адрес')
    # E-mail
    email = forms.EmailField(required=False)

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row = u'<tr%(html_class_attr)s><th>%(label)s</th><td colspan="2" class="text">%(errors)s%(field)s%(help_text)s</td></tr>',
            error_row = u'<tr><td colspan="2"> class="send_input"%s</td></tr>',
            row_ender = u'</td></tr>',
            help_text_html = u'<br />%s',
            errors_on_separate_row = False)
