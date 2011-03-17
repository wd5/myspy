          # -*- coding: utf-8 -*-
from cart.models import Client, CartProduct
from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet


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
        super(BaseProductFormset, self).clean()
        raise forms.ValidationError('test')
