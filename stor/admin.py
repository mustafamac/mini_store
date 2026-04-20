from django.contrib import admin
from .models import (
    Category, Company, Product, FeatureProductImage,
    ProductDescription, AdditionalInformation, Review,
    Cart, CustomerInfo, Order, Contact
)

# Register Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('category',)

# Register Company
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company', 'category', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('company',)

# Register Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'company', 'orignal_price', 'discount_percentage', 'is_stock', 'is_active', 'is_trending')
    list_filter = ('is_active', 'is_stock', 'is_trending', 'category', 'company')
    search_fields = ('product_name', 'product_description')
    readonly_fields = ('slug', 'created_at')
    fieldsets = (
        ('معلومات المنتج', {
            'fields': ('product_name', 'slug', 'product_description', 'category', 'company')
        }),
        ('التسعير والخصم', {
            'fields': ('orignal_price', 'discount_percentage')
        }),
        ('الصورة', {
            'fields': ('product_image',)
        }),
        ('الحالة', {
            'fields': ('is_stock', 'is_active', 'is_trending', 'warranty', 'created_at')
        }),
    )

# Register FeatureProductImage
@admin.register(FeatureProductImage)
class FeatureProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    search_fields = ('product__product_name',)

# Register ProductDescription
@admin.register(ProductDescription)
class ProductDescriptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'feature')
    search_fields = ('product__product_name', 'feature')

# Register AdditionalInformation
@admin.register(AdditionalInformation)
class AdditionalInformationAdmin(admin.ModelAdmin):
    list_display = ('product', 'feature')
    search_fields = ('product__product_name', 'feature')

# Register Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'rating', 'title')
    list_filter = ('rating',)
    search_fields = ('name', 'product__product_name')

# Register Cart
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'product', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('session_key', 'product__product_name')
    readonly_fields = ('created_at',)

# Register CustomerInfo
@admin.register(CustomerInfo)
class CustomerInfoAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'city')
    search_fields = ('full_name', 'email', 'phone')
    fieldsets = (
        ('معلومات العميل', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('العنوان', {
            'fields': ('address', 'city', 'zip_code')
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )

# Register Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'customer_email', 'customer_phone', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'customer__full_name', 'customer__email', 'customer__phone')
    readonly_fields = ('order_id', 'created_at', 'products_data')
    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('order_id', 'customer', 'status', 'created_at')
        }),
        ('التفاصيل المالية', {
            'fields': ('total_amount', 'products_data')
        }),
    )

    def customer_email(self, obj):
        return obj.customer.email
    customer_email.short_description = 'البريد الإلكتروني'

    def customer_phone(self, obj):
        return obj.customer.phone
    customer_phone.short_description = 'الهاتف'

# Register Contact
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('created_at',)
