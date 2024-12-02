import uuid
from .models import Cart

class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_anonymous:
            cart_session_id = request.session.get('cart_id')
            if not cart_session_id:
                cart_session_id = str(uuid.uuid4())
                request.session['cart_id'] = cart_session_id
            
            try:
                cart = Cart.objects.get(session_id=cart_session_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(session_id=cart_session_id)
            
            request.cart = cart
        else:
            cart, created = Cart.objects.get_or_create(user=request.user)
            # Если пользователь только что авторизовался
            if 'cart_id' in request.session:
                guest_cart = Cart.objects.filter(
                    session_id=request.session['cart_id']
                ).first()
                if guest_cart:
                    guest_cart.transfer_to_user(request.user)
                del request.session['cart_id']
            request.cart = cart

        response = self.get_response(request)
        return response