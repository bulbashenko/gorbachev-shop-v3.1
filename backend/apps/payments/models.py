from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Index
from apps.orders.models import Order
import uuid

class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CARD = 'card', _('Credit/Debit Card')
        BANK = 'bank', _('Bank Transfer')
        CASH = 'cash', _('Cash on Delivery')
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')
        CANCELLED = 'cancelled', _('Cancelled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Зашифрованные данные платежа
    encrypted_data = models.TextField(
        help_text=_('Encrypted payment details'),
        null=True,
        blank=True
    )
    
    # Информация о транзакции
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    gateway_response = models.JSONField(
        null=True,
        blank=True,
        help_text=_('Response from payment gateway')
    )
    
    # Метаданные для анализа и безопасности
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_('IP address of the customer')
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        help_text=_('Browser User Agent')
    )
    risk_score = models.IntegerField(
        default=0,
        help_text=_('Fraud detection risk score')
    )
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    # Аудит
    error_message = models.TextField(blank=True)
    attempts = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['created_at']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['risk_score']),
            # Составной индекс для часто используемых полей в запросах
            models.Index(fields=['status', 'payment_method', 'created_at']),
        ]
        permissions = [
            ('can_process_refunds', 'Can process refunds'),
            ('can_view_payment_details', 'Can view payment details'),
        ]

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"

    def save(self, *args, **kwargs):
        if self.risk_score > 80:
            raise ValidationError("Payment blocked due to high risk score")
        super().save(*args, **kwargs)

    @property
    def is_refundable(self):
        """Проверка возможности возврата"""
        return (
            self.status == self.PaymentStatus.COMPLETED and
            not self.refunded_at and
            (self.created_at - self.created_at).days <= 30
        )

    def mark_as_failed(self, error_message):
        """Отметить платеж как неудачный"""
        self.status = self.PaymentStatus.FAILED
        self.error_message = error_message
        self.save()

class PaymentLog(models.Model):
    """Модель для детального логирования платежей"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    message = models.TextField()
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['payment', 'timestamp']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"Log {self.id} for Payment {self.payment.id}"
