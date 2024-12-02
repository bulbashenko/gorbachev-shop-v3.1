from django.utils.deprecation import MiddlewareMixin
from .models import Cart
import uuid

class CartMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        Добавляет корзину к запросу.
        Для авторизованных пользователей использует их корзину.
        Для гостей создает сессионную корзину.
        """
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            if created:
                # Если у пользователя была гостевая корзина, переносим товары
                session_id = request.session.get('cart_id')
                if session_id:
                    try:
                        guest_cart = Cart.objects.get(session_id=session_id)
                        guest_cart.transfer_to_user(request.user)
                        request.session.pop('cart_id')
                    except Cart.DoesNotExist:
                        pass
        else:
            session_id = request.session.get('cart_id')
            if session_id:
                try:
                    cart = Cart.objects.get(session_id=session_id)
                except Cart.DoesNotExist:
                    cart = self._create_guest_cart(request)
            else:
                cart = self._create_guest_cart(request)

        request.cart = cart

    def _create_guest_cart(self, request):
        """Создание корзины для гостя"""
        session_id = str(uuid.uuid4())
        cart = Cart.objects.create(session_id=session_id)
        request.session['cart_id'] = session_id
        return cart
