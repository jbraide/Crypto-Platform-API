from django.urls import path
from .views import CreateListTransactionView, RetrieveTransactionView, UpdateTransactionStatusView

app_name = 'transactions'

urlpatterns = [
    path('transaction/list-create/', CreateListTransactionView.as_view(),),
    path('transaction/<str:pk>/', RetrieveTransactionView.as_view()),
    path('transaction/update/<str:pk>/', UpdateTransactionStatusView.as_view()),
]