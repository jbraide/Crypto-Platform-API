from django.contrib.auth.models import User
from django.utils.timezone import now
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, \
    GenericAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Transactions
from .serializers import CreateTransactionSerializer, ViewTransactionSerializer, \
    UpdateTransactionSerializer


class UserMixin:
    def get_user(self):
        return User.objects.get(username=self.request.user)
    
    def get_queryset(self):
        user = self.get_user()
        return Transactions.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ViewTransactionSerializer
        else:
            return self.serializer_class

class CreateListTransactionView(UserMixin, ListCreateAPIView):
    queryset = Transactions.objects.all()
    permission_classes = [IsAuthenticated,]
    serializer_class = CreateTransactionSerializer

    def perform_create(self, serializer):
        user = self.get_user()
        serializer.save(user=user)     

class RetrieveTransactionView(UserMixin, RetrieveAPIView):
    queryset = Transactions.objects.all()
    permission_classes = [IsAuthenticated,]
    # serializer_class = UpdateTransactionSerializer

class UpdateTransactionStatusView(UserMixin, UpdateAPIView):
    queryset = Transactions.objects.all()
    permission_classes = [IsAuthenticated,]
    serializer_class = UpdateTransactionSerializer

    def perform_update(self, serializer):
        user = self.get_user()
        serializer.save(user=user, paid_date_time=now())