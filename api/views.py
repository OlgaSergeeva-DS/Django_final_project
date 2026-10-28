from django.db.models import Prefetch
from django.shortcuts import render
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Collect, Payment
from .serializers import CollectSerializer, PaymentSerializer
# 1. Меняем импорт send_mail на импорт нашей задачи
from .tasks import send_donation_email_task


# Create your views here.
class CollectViewSet(viewsets.ModelViewSet):
    serializer_class = CollectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # К5: Оптимизация запросов
        return Collect.objects.select_related("author").prefetch_related(
            Prefetch("payments", queryset=Payment.objects.select_related("donor"))
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def donate(self, request, pk=None):
        collect = self.get_object()
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save(collect=collect, donor=request.user)
            collect.collected_amount += payment.amount
            collect.save()

            # 2. Вместо send_mail вызываем задачу через .delay
            if request.user.email:
                send_donation_email_task.delay(
                    payment.amount, collect.title, request.user.email
                )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
