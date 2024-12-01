from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from cryptography.fernet import Fernet
import logging
import json

logger = logging.getLogger('payment')

class PaymentEncryption:
    def __init__(self):
        self.fernet = Fernet(settings.PAYMENT_ENCRYPTION_KEY)

    def encrypt_data(self, data):
        """Шифрование платежных данных"""
        json_data = json.dumps(data)
        return self.fernet.encrypt(json_data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        """Расшифровка платежных данных"""
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Failed to decrypt payment data: {str(e)}")
            raise ValidationError("Invalid payment data")

class FraudDetection:
    def __init__(self, user, payment_data):
        self.user = user
        self.payment_data = payment_data
        self.risk_score = 0

    def check_risk(self):
        """Проверка рисков мошенничества"""
        self._check_user_history()
        self._check_payment_pattern()
        self._check_location()
        self._check_velocity()
        
        return {
            'risk_score': self.risk_score,
            'is_suspicious': self.risk_score > 80,
            'requires_review': self.risk_score > 60
        }

    def _check_user_history(self):
        """Проверка истории пользователя"""
        if not self.user.email_verified:
            self.risk_score += 20
        
        if self.user.failed_login_attempts > 3:
            self.risk_score += 15
            
        # Проверка возраста аккаунта
        account_age = (timezone.now() - self.user.date_joined).days
        if account_age < 1:
            self.risk_score += 25
        elif account_age < 7:
            self.risk_score += 15

    def _check_payment_pattern(self):
        """Проверка паттернов платежей"""
        from .models import Payment
        
        # Проверка необычных сумм
        recent_payments = Payment.objects.filter(
            order__user=self.user
        ).order_by('-created_at')[:5]
        
        if recent_payments.exists():
            avg_amount = sum(p.amount for p in recent_payments) / len(recent_payments)
            current_amount = self.payment_data.get('amount', 0)
            
            if current_amount > avg_amount * 3:
                self.risk_score += 20

    def _check_location(self):
        """Проверка геолокации"""
        user_country = self.user.default_shipping_address.country if self.user.default_shipping_address else None
        payment_country = self.payment_data.get('country')
        
        if user_country and payment_country and user_country != payment_country:
            self.risk_score += 30

    def _check_velocity(self):
        """Проверка скорости транзакций"""
        from .models import Payment
        
        recent_attempts = Payment.objects.filter(
            order__user=self.user,
            created_at__gte=timezone.now() - timezone.timedelta(hours=1)
        ).count()
        
        if recent_attempts > 5:
            self.risk_score += 25

class PaymentProcessor:
    def __init__(self, order, payment_data):
        self.order = order
        self.payment_data = payment_data
        self.encryption = PaymentEncryption()
        self.fraud_detection = FraudDetection(order.user, payment_data)

    @transaction.atomic
    def process_payment(self):
        """Обработка платежа"""
        try:
            # Проверка мошенничества
            risk_assessment = self.fraud_detection.check_risk()
            if risk_assessment['is_suspicious']:
                raise ValidationError("Payment flagged as suspicious")
            
            # Шифрование данных
            encrypted_data = self.encryption.encrypt_data(self.payment_data)
            
            # Создание платежа
            from .models import Payment
            payment = Payment.objects.create(
                order=self.order,
                amount=self.order.total,
                payment_method=self.payment_data['method'],
                encrypted_data=encrypted_data
            )
            
            # Здесь будет интеграция с платежным шлюзом
            success = self._process_with_payment_gateway()
            
            if success:
                payment.status = 'paid'
                payment.save()
                
                self.order.payment_status = 'paid'
                self.order.status = 'processing'
                self.order.save()
                
                logger.info(f"Payment {payment.id} processed successfully")
                return payment
            else:
                raise ValidationError("Payment processing failed")
                
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            raise

    def _process_with_payment_gateway(self):
        """
        Здесь будет реальная интеграция с платежным шлюзом
        Сейчас возвращаем True для демонстрации
        """
        return True

    def refund_payment(self, payment):
        """Возврат платежа"""
        try:
            # Здесь будет интеграция с платежным шлюзом для возврата
            success = True  # В реальности зависит от ответа платежного шлюза
            
            if success:
                payment.status = 'refunded'
                payment.save()
                
                self.order.payment_status = 'refunded'
                self.order.status = 'cancelled'
                self.order.save()
                
                logger.info(f"Payment {payment.id} refunded successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Refund processing error: {str(e)}")
            raise
