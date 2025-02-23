from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Product

@receiver(post_save, sender=Product)
def product_created(sender, instance, created, **kwargs):
    if created:
        print(f"Yangi mahsulot yaratildi: {instance.name}")

@receiver(post_save, sender=Product)
def product_updated(sender, instance, created, **kwargs):
    if not created:
        print(f"Mahsulot yangilandi: {instance.name}")

@receiver(pre_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    print(f"Mahsulot o'chirildi: {instance.name}")