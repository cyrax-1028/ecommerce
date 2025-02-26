import json
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.mail import EmailMessage
from .models import Product, User


@receiver(post_save, sender=Product)
def product_created(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()
        email_of_users = [user.email for user in users]
        email = EmailMessage(
            'Product Created',
            f'{instance.name.title()} successfully saved',
            to=email_of_users
        )
        email.send()
        print('Notifications sent')

@receiver(post_save, sender=Product)
def product_updated(sender, instance, created, **kwargs):
    if not created:
        users = User.objects.all()
        email_of_users = [user.email for user in users]
        email = EmailMessage(
            'Product Updated',
            f'{instance.name.title()} has been updated',
            to=email_of_users
        )
        email.send()
        print(f"Mahsulot yangilandi: {instance.name}")


@receiver(pre_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    users = User.objects.all()
    email_of_users = [user.email for user in users]
    email = EmailMessage(
        'Product Deleted',
        f'{instance.name.title()} has been deleted',
        to=email_of_users
    )
    email.send()
    print(f"Mahsulot o'chirildi: {instance.name}")