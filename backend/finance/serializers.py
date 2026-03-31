from rest_framework import serializers
from .models import Category, Transaction, TransactionType
from django.db.models import Sum
from decimal import Decimal

class CategorySerializer(serializers.ModelSerializer):
  transaction_count = serializers.SerializerMethodField()

  class Meta:
    model  = Category
    fields = [
      'id', 'name', 'type', 'icon',
      'color', 'is_default', 'transaction_count', 'created_at'
    ]
    read_only_fields = ['id', 'is_default', 'created_at']

  def get_transaction_count(self, obj):
    return obj.transactions.count()

  def validate_name(self, value):
    """Category name must be at least 2 characters."""
    if len(value.strip()) < 2:
      raise serializers.ValidationError(
        "Category name must be at least 2 characters."
      )
    return value.strip()

  def validate_color(self, value):
    """Color must be a valid hex code like #FF5733."""
    if not value.startswith('#') or len(value) != 7:
      raise serializers.ValidationError(
          "Color must be a valid hex code e.g. #FF5733"
      )
    return value

  def create(self, validated_data):
    validated_data['user'] = self.context['request'].user
    return super().create(validated_data)

class TransactionSerializer(serializers.ModelSerializer):
  category_name  = serializers.CharField(source='category.name',  read_only=True)
  category_icon  = serializers.CharField(source='category.icon',  read_only=True)
  category_color = serializers.CharField(source='category.color', read_only=True)

  class Meta:
    model  = Transaction
    fields = [
      'id', 'transaction_type', 'amount', 'description',
      'date', 'notes', 'category', 'category_name',
      'category_icon', 'category_color', 'created_at', 'updated_at'
    ]
    read_only_fields = ['id', 'created_at', 'updated_at']

  def validate_amount(self, value):
    """Amount must be greater than zero."""
    if value <= Decimal('0'):
      raise serializers.ValidationError("Amount must be greater than zero.")
    return value

  def validate_description(self, value):
    """Description cannot be empty."""
    if not value.strip():
      raise serializers.ValidationError("Description cannot be empty.")
    return value.strip()

  def validate(self, data):
    """
    Cross-field validation:
    If a category is provided, make sure it matches the transaction type.
    E.g. You can't use a 'Salary' (income) category on an expense transaction.
    """
    category = data.get('category')
    transaction_type = data.get('transaction_type')

    if category and transaction_type:
      if category.type != transaction_type:
        raise serializers.ValidationError({
          'category': (
              f"This category is for '{category.type}' transactions, "
              f"but you selected '{transaction_type}'."
          )
        })
    return data

  def create(self, validated_data):
    validated_data['user'] = self.context['request'].user
    return super().create(validated_data)

class TransactionDetailSerializer(TransactionSerializer):
  category = CategorySerializer(read_only=True)
  category_id = serializers.PrimaryKeyRelatedField(
    queryset=Category.objects.all(),
    source='category',
    write_only=True,
    required=False
  )

  class Meta(TransactionSerializer.Meta):
    fields = TransactionSerializer.Meta.fields + ['category_id']


class FinancialSummarySerializer(serializers.Serializer):
  total_income       = serializers.DecimalField(max_digits=12, decimal_places=2)
  total_expense      = serializers.DecimalField(max_digits=12, decimal_places=2)
  balance            = serializers.DecimalField(max_digits=12, decimal_places=2)
  total_transactions = serializers.IntegerField()
  income_count       = serializers.IntegerField()
  expense_count      = serializers.IntegerField()

class MonthlySummarySerializer(serializers.Serializer):
  month         = serializers.IntegerField()
  year          = serializers.IntegerField()
  month_name    = serializers.CharField()
  total_income  = serializers.DecimalField(max_digits=12, decimal_places=2)
  total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
  balance       = serializers.DecimalField(max_digits=12, decimal_places=2)


class CategorySpendingSerializer(serializers.Serializer):
  category_id   = serializers.IntegerField()
  category_name = serializers.CharField()
  category_icon = serializers.CharField()
  category_color = serializers.CharField()
  total_amount  = serializers.DecimalField(max_digits=12, decimal_places=2)
  percentage    = serializers.FloatField()
  count         = serializers.IntegerField()