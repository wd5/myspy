from cart.models import CartProduct, Client
import decimal

def subtotal(cartid):
    products = CartProduct.objects.filter(cartitem=cartid)
    cart_total = decimal.Decimal('0.00')
    cart_discount_total = 0
    discount = 0
    discount_quantity = 0
    for item in products:
        if item.product.is_discount:
            discount_quantity += item.quantity
            cart_discount_total += item.product.price * item.quantity
        cart_total += item.product.price * item.quantity
    if discount_quantity or len(products) >= 2:
        discount = (cart_discount_total * 10)/100
    cart_total -= discount
    ci = Client.objects.get(cart=cartid)
    ci.subtotal = cart_total
    ci.discount = discount
    ci.save()
