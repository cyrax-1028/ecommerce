import random
import string
import uuid
from email.policy import default
from itertools import product
from django.db.models import Avg

from django.db import models
from decimal import Decimal

from django.template.defaulttags import comment
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = "categories"


class Product(BaseModel):
    class RatingChoice(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(null=True, blank=True)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, related_name="products", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    rating = models.PositiveIntegerField(choices=RatingChoice.choices, default=RatingChoice.ONE)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    stock = models.CharField(max_length=20, default="Not Available")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    model = models.CharField(max_length=255, null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)

    @property
    def discounted_price(self):
        if self.discount > 0:
            return (self.price * (1 - Decimal(self.discount) / 100)).quantize(Decimal("0.01"))
        return self.price

    @property
    def get_rating(self):
        avg_rating = self.comments.aggregate(average=Avg("rating"))["average"]
        return round(avg_rating) if avg_rating is not None else 1

    @property
    def is_new(self):
        return (now() - self.created_at).total_seconds() < 86400

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.stock = "Available" if self.quantity > 0 else "Sold Out"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"


class Comment(BaseModel):
    class RatingChoice(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5

    name = models.CharField(max_length=255, null=True, blank=True)
    rating = models.PositiveIntegerField(choices=RatingChoice.choices, default=RatingChoice.ONE)
    email = models.EmailField()
    content = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    is_negative = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} => {self.created_at}"

    class Meta:
        ordering = ["-created_at"]


class ProductImage(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='media/products/')

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"


class Attribute(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.value


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='product_attributes', null=True,
                                blank=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.SET_NULL, null=True, blank=True)
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.SET_NULL, null=True, blank=True)


def generate_random_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))


def generate_invoice_prefix():
    return ''.join(random.choices(string.ascii_uppercase, k=5))


class Customer(BaseModel):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    description = models.TextField(blank=True, null=True, default="No Description")
    vat_number = models.CharField(max_length=50, blank=True, null=True, default="No VAT number")

    send_email_to = models.EmailField()
    address = models.TextField()
    phone_number = PhoneNumberField(region="UZ")
    invoice_prefix = models.CharField(max_length=5, default=generate_invoice_prefix, unique=True)
    invoice_number = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.invoice_prefix:
            self.invoice_prefix = generate_invoice_prefix()

        if not self.invoice_number:
            self.invoice_number = 1

        super().save(*args, **kwargs)

    def generate_invoice_id(self):
        return f"{self.invoice_prefix}-{self.invoice_number:05d}"

    def __str__(self):
        return f'{self.full_name} -> {self.generate_invoice_id()}'


class Order(BaseModel):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)



    def save(self, *args, **kwargs):
        if self.id:
            self.subtotal = sum(
                item.quantity * item.product.discounted_price for item in self.order_items.all()
            )
            self.tax_amount = (self.subtotal * self.tax_rate / Decimal(100)).quantize(Decimal('0.01'))
            self.total = self.subtotal + self.tax_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_items(self):
        return self.quantity * self.product.discounted_price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.token}"