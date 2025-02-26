from django.contrib import admin
from django.contrib.auth.models import User, Group
from import_export.admin import ImportExportModelAdmin, ImportExportMixin
from commerce.models import *
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin
from import_export import resources


@admin.register(OrderItem)
class OrderItemAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('customer', 'status')
    inlines = [OrderItemInline]

@admin.register(ProductImage)
class ProductImageAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('image', 'product')

@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'email', 'content', 'product', 'is_negative', 'created_at')
    search_fields = ('name', 'email', 'content', 'product__name')

@admin.register(Attribute)
class AttributeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(AttributeValue)
class AttributeValueAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('value',)
    search_fields = ('value',)

@admin.register(ProductAttribute)
class ProductAttributeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('product', 'attribute', 'attribute_value')
    search_fields = ('product__name', 'attribute__name', 'attribute_value__value')
    list_filter = ('attribute',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    search_fields = ('name', 'price')
    list_filter = ['category', 'quantity', 'rating']
    autocomplete_fields = ['category']
    inlines = [ProductImageInline, ProductAttributeInline]
    prepopulated_fields = {'slug': ('name',)}

class ProductInline(admin.TabularInline):
    model = Product

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('title', 'created_at', 'product_count')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

    inlines = [
        ProductInline,
    ]

    def product_count(self, category):
        return category.products.count()


class CustomerResource(resources.ModelResource):
    class Meta:
        model = Customer
        fields = ('id', 'full_name', 'seria', 'email', 'description', 'vat_number', 'send_email_to', 'address', 'phone_number', 'invoice_prefix', 'invoice_number')

class CustomerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('full_name', 'invoice_id', 'email')
    fields = ('full_name', 'email', 'description', 'vat_number', 'send_email_to', 'address', 'phone_number', 'invoice_number')

    def invoice_id(self, obj):
        return obj.generate_invoice_id()
    invoice_id.short_description = 'Invoice ID'

admin.site.register(Customer, CustomerAdmin)

admin.site.site_header = 'Alibaba Admin'
admin.site.site_title = 'Alibaba Admin Portal'
admin.site.index_title = 'Welcome To Alibaba Researcher Portal'