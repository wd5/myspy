          # -*- coding: utf-8 -*-
from cart.models import Client, CartProduct
from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

class ClientForm(ModelForm):
    class Meta:
        model = Client
        exclude = ('cart, referrer')

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
                print form.cleaned_data
