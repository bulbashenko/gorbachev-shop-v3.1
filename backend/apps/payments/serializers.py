from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'payment_method',
            'status', 'transaction_id', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'transaction_id',
            'created_at'
        ]

class PaymentMethodSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(
        choices=Payment.PaymentMethod.choices
    )