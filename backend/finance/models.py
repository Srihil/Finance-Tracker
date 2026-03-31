from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class TransactionType(models.TextChoices):
  INCOME = 'income', 'Income'
  EXPENSE = 'expense', 'Expense'

class Category(models.Model):
  name = models.CharField(max_length=100)
  
  type = models.CharField(
    max_length=10,
    choices=TransactionType.choices,
    help_text="Is this category for income or expense?"
  )
  
  icon = models.CharField(
    max_length=50,
    default='💰',
    help_text="Emoji icon for the category"
  )
  
  color = models.CharField(
    max_length=7,
    default='#6C63FF',
    help_text="Hex color code, e.g. #FF5733"
  )
  
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='categories',
    help_text="Leave blank for default system categories"
  )
  
  is_default = models.BooleanField(
    default=False,
    help_text="Default categories are shown to all users"
  )
  
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    db_table = 'categories'
    verbose_name = 'Category'
    verbose_name_plural = 'Categories'
    ordering = ['name']
    unique_together = ('name', 'type', 'user')

  def __str__(self):
    owner = 'Default' if self.is_default else self.user.username
    return f"{self.icon} {self.name} ({self.type}) — {owner}"



class Transaction(models.Model):
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='transactions',
    help_text="The user this transaction belongs to"
  )
  
  category = models.ForeignKey(
    Category,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='transactions',
    help_text="Category of this transaction"
  )
  
  transaction_type = models.CharField(
    max_length=10,
    choices=TransactionType.choices,
    help_text="Is this an income or expense?"
  )
  
  amount = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    validators=[MinValueValidator(Decimal('0.01'))],
    help_text="Transaction amount (must be positive)"
  )
  
  description = models.CharField(
    max_length=255,
    help_text="Short description e.g. 'Lunch at office'"
  )
  
  date = models.DateField(
    help_text="Date when the transaction occurred"
  )
  
  notes = models.TextField(
    blank=True,
    null=True,
    help_text="Optional additional notes"
  )
  
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'transactions'
    verbose_name = 'Transaction'
    verbose_name_plural = 'Transactions'
    ordering = ['-date', '-created_at']  

  def __str__(self):
    symbol = '↑' if self.transaction_type == 'income' else '↓'
    return f"{symbol} {self.user.username} — ₹{self.amount} ({self.description})"

  @property
  def is_income(self):
    return self.transaction_type == TransactionType.INCOME

  @property
  def is_expense(self):
    return self.transaction_type == TransactionType.EXPENSE