from django.db import models
from catalog.models import Product

class ProductInStore(models.Model):
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
