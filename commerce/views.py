from lib2to3.fixes.fix_input import context
from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.core.mail import send_mail
from commerce.models import *
from typing import Optional
from commerce.forms import *
import uuid
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site


# //////////////////// P R O D U C T //// C R U D ////////////////////
def product_list(request):
    search_query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', '')

    if filter_type == 'date':
        products = Product.objects.all().order_by('-created_at')
    elif filter_type == 'price':
        products = Product.objects.all().order_by('-price')
    elif filter_type == 'rating':
        products = Product.objects.all().order_by('-rating')

    else:
        products = Product.objects.all().order_by('-created_at')

    if search_query:
        products = Product.objects.filter(name__icontains=search_query)

    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'commerce/Products/product-list.html', context=context)


def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    comments = Comment.objects.filter(product=product, is_negative=False)
    formatted_date = product.created_at.strftime("%B %d, %Y")

    context = {
        'product': product,
        'comments': comments,
        'formatted_date': formatted_date,
    }
    return render(request, 'commerce/Products/product-details.html', context)


def product_grid(request):
    search_query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', '')

    if filter_type == 'date':
        products = Product.objects.all().order_by('-created_at')
    elif filter_type == 'price':
        products = Product.objects.all().order_by('-price')
    elif filter_type == 'rating':
        products = Product.objects.all().order_by('-rating')

    else:
        products = Product.objects.all()

    if search_query:
        products = Product.objects.filter(name__icontains=search_query)

    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'commerce/Products/product-grid.html', context=context)


def comment_view(request, pk):
    product = get_object_or_404(Product, id=pk)
    form = CommentModelForm()
    if request.method == 'POST':
        form = CommentModelForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = product
            comment.save()
            return redirect('product_details', product_id=pk)

        else:
            print(form.errors)

    context = {
        'product': product,
        'form': form
    }
    return render(request, 'commerce/Products/product-details.html', context=context)


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product has been successfully added.')
            return redirect('product_list')
    else:
        form = ProductModelForm()

    categories = Category.objects.all()
    context = {
        'form': form,
        'categories': categories
    }

    return render(request, 'commerce/Products/add_product.html', context=context)


# class CreateProduct(CreateView):
#     model = Product
#     template_name = 'commerce/Products/add_product.html'
#     form_class = ProductModelForm
#     success_url = reverse_lazy('product_list')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["categories"] = Category.objects.all()
#         return context


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    if request.method == "POST":
        form = ProductModelForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect('product_list')
    else:
        form = ProductModelForm(instance=product)

    categories = Category.objects.all()
    context = {
        'categories': categories,
        'form': form
    }

    return render(request, 'commerce/Products/edit_product.html', context=context)


@login_required
def delete_product(request, pk):
    try:
        product = Product.objects.get(id=pk)
        product.delete()
        return redirect('product_list')
    except Product.DoesNotExist as e:
        print(e)


# //////////////////// C U S T O M E R //// C R U D ////////////////////
def customer_list(request):
    search_query = request.GET.get('q', '')
    customers = Customer.objects.all()

    for customer in customers:
        customer.created_date = customer.created_at.strftime("%B %d, %Y")

    if search_query:
        customers = Customer.objects.filter(full_name__icontains=search_query)

    context = {
        'customers': customers,
    }

    return render(request, template_name='commerce/customers/customers.html', context=context)


def customer_details(request, pk):
    customer = get_object_or_404(Customer, id=pk)
    created_date = customer.created_at.strftime("%b %d, %I:%M %p")

    context = {
        'customer': customer,
        'created_date': created_date,
    }

    return render(request, template_name='commerce/customers/customer-details.html', context=context)


@login_required
def add_customer(request):
    if request.method == "POST":
        form = CustomerModelForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.invoice_prefix = generate_invoice_prefix()
            customer.invoice_number = 1
            customer.save()
            return redirect('customer_list')
    else:
        form = CustomerModelForm()

    return render(request, 'commerce/Customers/add_customer.html', {'form': form})


@login_required
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, id=pk)

    if request.method == "POST":
        form = CustomerModelForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            return redirect('customer_list')
    else:
        form = CustomerModelForm(instance=customer)

    return render(request, 'commerce/Customers/edit_customer.html', {'form': form})


@login_required
def delete_customer(request, pk):
    try:
        customer = Customer.objects.get(id=pk)
        customer.delete()
        return redirect('customer_list')
    except Customer.DoesNotExist as e:
        print(e)


def customer_info(request, pk):
    customer = get_object_or_404(Customer, id=pk)

    return render(request, "commerce/Customers/customer_info.html", {"customer": customer})


# //////////////////// O R D E R //// C R U D ////////////////////
def order_list(request):
    search_query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', '')

    if filter_type == 'Pending':
        orders = Order.objects.filter(status='Pending')
    elif filter_type == 'Completed':
        orders = Order.objects.filter(status='Completed')
    elif filter_type == 'Cancelled':
        orders = Order.objects.filter(status='Cancelled')
    elif filter_type == 'Clear':
        orders = Order.objects.filter(status='Clear')
    else:
        orders = Order.objects.all().order_by('-created_at')

    if search_query:
        orders = Order.objects.filter(customer__full_name__icontains=search_query)

    context = {
        'orders': orders,
    }
    return render(request, template_name='commerce/Orders/order-list.html', context=context)


def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    context = {
        'order': order,
    }

    return render(request, 'commerce/Orders/order-details.html', context)


def change_order_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id)

    if new_status in ['Pending', 'Completed', 'Cancelled']:
        order.status = new_status
        order.save()

    return redirect('order_list')


@login_required
def add_order(request):
    customers = Customer.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        product_id = request.POST.get("product")
        quantity = int(request.POST.get("quantity", 1))
        status = request.POST.get("status", "Pending")

        customer = get_object_or_404(Customer, id=customer_id)
        product = get_object_or_404(Product, id=product_id)

        order, created = Order.objects.get_or_create(customer=customer, status=status)

        OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return redirect("order_list")

    return render(request, "commerce/Orders/add_order.html", {"customers": customers, "products": products})


@login_required
def order_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customers = Customer.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        quantity = int(request.POST.get("quantity", 1))

        customer = get_object_or_404(Customer, id=customer_id)

        if product.quantity < quantity:
            messages.error(request, "Yetarli mahsulot yo'q!")
            return redirect('order_product', product_id=product_id)

        order, created = Order.objects.get_or_create(customer=customer, status="Pending")
        OrderItem.objects.create(order=order, product=product, quantity=quantity)

        product.quantity -= quantity
        product.save()

        return redirect('order_summary')

    context = {
        'product': product,
        'customers': customers,
    }

    return render(request, "commerce/Products/order_product.html", context=context)


def order_summary(request):
    return render(request, "commerce/Products/order_summary.html")


def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('order_list')


# //////////////////// A B O U T ////////////////////////
def about(request):
    return render(request, 'commerce/about.html')


def about_alibaba(request):
    return render(request, 'commerce/about_alibaba.html')


# //////////////////// A U T H E N T I C A T I O N ////////////////////////
# def register(request):
#     if request.method == "POST":
#         username = request.POST["username"]
#         email = request.POST["email"]
#         password1 = request.POST["password1"]
#         password2 = request.POST["password2"]
#
#         if password1 != password2:
#             messages.error(request, "Parollar mos kelmadi!")
#             return redirect("register")
#
#         if User.objects.filter(username=username).exists():
#             messages.error(request, "Bu foydalanuvchi nomi allaqachon mavjud!")
#             return redirect("register")
#
#         if User.objects.filter(email=email).exists():
#             messages.error(request, "Bu email allaqachon ro‘yxatdan o‘tgan!")
#             return redirect("register")
#
#         user = User.objects.create_user(username=username, email=email, password=password1)
#         user.save()
#
#         send_mail(
#             "Ro‘yxatdan o‘tish muvaffaqiyatli!",
#             f"Hurmatli {username}, siz Alibaba.com onlayn do'konidan muvaffaqiyatli ro‘yxatdan o‘tdingiz!",
#             settings.EMAIL_HOST_USER,
#             [email],
#             fail_silently=False,
#         )
#
#         new_user = authenticate(request, username=username, password=password1)
#         if new_user:
#             login(request, new_user)
#             return redirect("product_list")
#
#         messages.success(request, "Ro‘yxatdan o‘tish muvaffaqiyatli yakunlandi!")
#         return redirect("login")
#
#     return render(request, "commerce/Authentication/register.html")


def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Parollar mos kelmadi!")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu email allaqachon ro‘yxatdan o‘tgan!")
            return redirect("register")

        user = User.objects.create_user(username=email, email=email, password=password1, is_active=False)
        user.save()

        token = str(uuid.uuid4())
        EmailConfirmation.objects.create(user=user, token=token)

        confirmation_link = request.build_absolute_uri(reverse("confirm_email", args=[token]))

        send_mail(
            "Email tasdiqlash",
            f"Hurmatli foydalanuvchi, iltimos, quyidagi havola orqali ro‘yxatdan o‘tishni tasdiqlang: {confirmation_link}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, "Tasdiqlash havolasi emailingizga yuborildi!")
        return render(request, "commerce/Authentication/email_confirmation_sent.html")

    return render(request, "commerce/Authentication/register.html")


def confirm_email(request, token):
    try:
        confirmation = EmailConfirmation.objects.get(token=token)
        user = confirmation.user
        user.is_active = True
        user.save()
        confirmation.delete()

        backend = 'django.contrib.auth.backends.ModelBackend'
        user.backend = backend

        login(request, user)
        messages.success(request, "Email tasdiqlandi! Xush kelibsiz!")
        return redirect("product_list")

    except EmailConfirmation.DoesNotExist:
        messages.error(request, "Noto‘g‘ri yoki eskirgan tasdiqlash havolasi!")
        return redirect("register")


def user_login(request):
    if request.method == "POST":
        email = request.POST["email"]  # username -> email
        password = request.POST["password"]

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            send_mail(
                "Kirish muvaffaqiyatli!",
                f"Hurmatli {user.username}, siz Alibaba.com tizimiga muvaffaqiyatli kirdingiz!",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return redirect("product_list")
        else:
            messages.error(request, "Login yoki parol noto‘g‘ri!")
            return redirect("login")

    return render(request, "commerce/Authentication/login.html")


def user_logout(request):
    if request.user.is_authenticated:
        send_mail(
            "Chiqish amalga oshirildi!",
            f"Hurmatli {request.user.username}, siz Alibaba.com tizimidan chiqdingiz!",
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=False,
        )
    logout(request)
    return redirect("product_list")
