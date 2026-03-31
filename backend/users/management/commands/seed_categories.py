from django.core.management.base import BaseCommand
from finance.models import Category, TransactionType


class Command(BaseCommand):
  help = 'Seeds the database with default income and expense categories'

  def handle(self, *args, **kwargs):
    income_categories = [
      {'name': 'Salary',      'icon': '💼', 'color': '#4CAF50'},
      {'name': 'Freelance',   'icon': '💻', 'color': '#2196F3'},
      {'name': 'Business',    'icon': '🏢', 'color': '#9C27B0'},
      {'name': 'Investment',  'icon': '📈', 'color': '#FF9800'},
      {'name': 'Bonus',       'icon': '🎁', 'color': '#E91E63'},
      {'name': 'Rental',      'icon': '🏠', 'color': '#00BCD4'},
      {'name': 'Other Income','icon': '💰', 'color': '#607D8B'},
    ]

    expense_categories = [
      {'name': 'Food & Dining',   'icon': '🍔', 'color': '#F44336'},
      {'name': 'Travel',          'icon': '✈️',  'color': '#3F51B5'},
      {'name': 'Shopping',        'icon': '🛍️',  'color': '#E91E63'},
      {'name': 'Bills & Utilities','icon': '⚡', 'color': '#FF5722'},
      {'name': 'Health',          'icon': '🏥', 'color': '#009688'},
      {'name': 'Entertainment',   'icon': '🎬', 'color': '#673AB7'},
      {'name': 'Education',       'icon': '📚', 'color': '#2196F3'},
      {'name': 'Groceries',       'icon': '🛒', 'color': '#4CAF50'},
      {'name': 'Rent',            'icon': '🏠', 'color': '#795548'},
      {'name': 'Fuel',            'icon': '⛽', 'color': '#FF9800'},
      {'name': 'Other Expense',   'icon': '💸', 'color': '#9E9E9E'},
    ]

    created_count = 0

    for cat in income_categories:
      obj, created = Category.objects.get_or_create(
        name=cat['name'],
        type=TransactionType.INCOME,
        user=None,
        defaults={
          'icon': cat['icon'],
          'color': cat['color'],
          'is_default': True,
        }
      )
      if created:
        created_count += 1
        self.stdout.write(
          self.style.SUCCESS(f"  ✅ Created income category: {cat['icon']} {cat['name']}")
        )

    for cat in expense_categories:
      obj, created = Category.objects.get_or_create(
        name=cat['name'],
        type=TransactionType.EXPENSE,
        user=None,
        defaults={
          'icon': cat['icon'],
          'color': cat['color'],
          'is_default': True,
        }
      )
      if created:
        created_count += 1
        self.stdout.write(
          self.style.SUCCESS(f"  ✅ Created expense category: {cat['icon']} {cat['name']}")
        )

    self.stdout.write(
      self.style.SUCCESS(f"\n Seeding complete! {created_count} categories created.")
    )