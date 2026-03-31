from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from decimal import Decimal
from datetime import date
import calendar

from .models import Category, Transaction, TransactionType
from .serializers import (
    CategorySerializer,
    TransactionSerializer,
    TransactionDetailSerializer,
    FinancialSummarySerializer,
    MonthlySummarySerializer,
    CategorySpendingSerializer,
)


# ============================================================
# HELPER: get a zero-safe decimal total
# ============================================================
def safe_total(queryset, field='amount'):
    result = queryset.aggregate(total=Sum(field))['total']
    return result if result is not None else Decimal('0.00')


# ============================================================
# CATEGORY VIEWSET
# Handles: list, create, retrieve, update, destroy
# ============================================================
class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing categories.
    
    A user can see:
    - All default (system) categories
    - Their own custom categories
    
    A user can only edit/delete their OWN categories.
    """
    serializer_class   = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['name']

    def get_queryset(self):
        """
        Return categories that belong to the current user
        OR are system default categories.
        """
        user = self.request.user
        queryset = Category.objects.filter(
            Q(user=user) | Q(is_default=True)
        )

        # Optional filter by type: ?type=income or ?type=expense
        category_type = self.request.query_params.get('type')
        if category_type in ['income', 'expense']:
            queryset = queryset.filter(type=category_type)

        return queryset

    def destroy(self, request, *args, **kwargs):
        """Prevent deletion of default system categories."""
        category = self.get_object()
        if category.is_default:
            return Response(
                {'error': 'Default categories cannot be deleted.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


# ============================================================
# TRANSACTION VIEWSET
# Handles: list, create, retrieve, update, destroy
# + custom actions: summary, monthly-summary, category-spending
# ============================================================
class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing transactions (income + expenses).
    
    Features:
    - Full CRUD on transactions
    - Filter by type, category, date range
    - Search by description
    - Summary endpoint
    - Monthly breakdown
    - Category spending breakdown (for charts)
    """
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['description', 'notes']
    ordering_fields    = ['date', 'amount', 'created_at']
    ordering           = ['-date']

    def get_queryset(self):
        """
        Return only the current user's transactions.
        Supports multiple query filters.
        """
        user     = self.request.user
        queryset = Transaction.objects.filter(user=user).select_related('category')

        # Filter by transaction type: ?type=income or ?type=expense
        t_type = self.request.query_params.get('type')
        if t_type in ['income', 'expense']:
            queryset = queryset.filter(transaction_type=t_type)

        # Filter by category: ?category=3
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Filter by date range: ?start_date=2024-01-01&end_date=2024-01-31
        start_date = self.request.query_params.get('start_date')
        end_date   = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Filter by month and year: ?month=1&year=2024
        month = self.request.query_params.get('month')
        year  = self.request.query_params.get('year')
        if month and year:
            queryset = queryset.filter(date__month=month, date__year=year)

        return queryset

    def get_serializer_class(self):
        """Use detail serializer for single object views."""
        if self.action in ['retrieve', 'update', 'partial_update']:
            return TransactionDetailSerializer
        return TransactionSerializer

    # ----------------------------------------------------------
    # CUSTOM ACTION: /api/finance/transactions/summary/
    # Returns: total income, total expense, balance
    # ----------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Returns financial summary for the current user.
        Optional filter: ?month=1&year=2024
        """
        queryset = self.get_queryset()

        income_qs  = queryset.filter(transaction_type=TransactionType.INCOME)
        expense_qs = queryset.filter(transaction_type=TransactionType.EXPENSE)

        total_income  = safe_total(income_qs)
        total_expense = safe_total(expense_qs)
        balance       = total_income - total_expense

        data = {
            'total_income'      : total_income,
            'total_expense'     : total_expense,
            'balance'           : balance,
            'total_transactions': queryset.count(),
            'income_count'      : income_qs.count(),
            'expense_count'     : expense_qs.count(),
        }

        serializer = FinancialSummarySerializer(data)
        return Response(serializer.data)

    # ----------------------------------------------------------
    # CUSTOM ACTION: /api/finance/transactions/monthly-summary/
    # Returns: month-wise income vs expense breakdown
    # ----------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='monthly-summary')
    def monthly_summary(self, request):
        """
        Returns the last 6 months of income vs expense data.
        Perfect for rendering charts in React Native.
        """
        user     = request.user
        queryset = Transaction.objects.filter(user=user)

        # Optional year filter: ?year=2024
        year = request.query_params.get('year', date.today().year)

        monthly_data = (
            queryset
            .filter(date__year=year)
            .annotate(month=TruncMonth('date'))
            .values('month', 'transaction_type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        # Reshape raw data into a clean month-by-month structure
        months_map = {}
        for entry in monthly_data:
            month_dt   = entry['month']
            month_key  = month_dt.strftime('%Y-%m')
            month_num  = month_dt.month
            month_name = calendar.month_name[month_num]

            if month_key not in months_map:
                months_map[month_key] = {
                    'month'        : month_num,
                    'year'         : month_dt.year,
                    'month_name'   : month_name,
                    'total_income' : Decimal('0.00'),
                    'total_expense': Decimal('0.00'),
                    'balance'      : Decimal('0.00'),
                }

            if entry['transaction_type'] == TransactionType.INCOME:
                months_map[month_key]['total_income'] = entry['total']
            else:
                months_map[month_key]['total_expense'] = entry['total']

        # Calculate balance for each month
        result = []
        for key in sorted(months_map.keys()):
            item = months_map[key]
            item['balance'] = item['total_income'] - item['total_expense']
            result.append(item)

        serializer = MonthlySummarySerializer(result, many=True)
        return Response(serializer.data)

    # ----------------------------------------------------------
    # CUSTOM ACTION: /api/finance/transactions/category-spending/
    # Returns: spending per category (used for pie chart)
    # ----------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='category-spending')
    def category_spending(self, request):
        """
        Returns expense breakdown by category.
        Optional filters: ?month=1&year=2024 or ?type=expense
        """
        queryset = self.get_queryset()

        # Default to expense breakdown for charts
        t_type = request.query_params.get('type', 'expense')
        queryset = queryset.filter(transaction_type=t_type)

        # Aggregate spending per category
        spending = (
            queryset
            .values(
                'category__id',
                'category__name',
                'category__icon',
                'category__color',
            )
            .annotate(
                total_amount=Sum('amount'),
                count=Count('id')
            )
            .order_by('-total_amount')
        )

        # Calculate the grand total to get percentages
        grand_total = safe_total(queryset)

        result = []
        for item in spending:
            total  = item['total_amount'] or Decimal('0')
            pct    = float((total / grand_total * 100)) if grand_total > 0 else 0.0
            result.append({
                'category_id'   : item['category__id'],
                'category_name' : item['category__name'] or 'Uncategorized',
                'category_icon' : item['category__icon'] or '💰',
                'category_color': item['category__color'] or '#607D8B',
                'total_amount'  : total,
                'percentage'    : round(pct, 2),
                'count'         : item['count'],
            })

        serializer = CategorySpendingSerializer(result, many=True)
        return Response(serializer.data)