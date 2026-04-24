from django.contrib import admin
from .models import (
    Category, Company, Product, FeatureProductImage,
    ProductDescription, Review,
    Cart, CustomerInfo, Order, Contact
)

# تخصيص واجهة لوحة التحكم
admin.site.site_header = "إدارة متجر ITQAN Tech"
admin.site.site_title = "بوابة الإدارة"
admin.site.index_title = "لوحة تحكم منصة إتقان تيك"

# Register Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category',)
    search_fields = ('category',)

# Register Company
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company', 'category')
    list_filter = ('category',)
    search_fields = ('company',)

# Register Product
class FeatureProductImageInline(admin.TabularInline):
    model = FeatureProductImage
    extra = 1

class ProductDescriptionInline(admin.StackedInline):
    model = ProductDescription
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'company', 'orignal_price', 'discount_percentage', 'is_stock', 'is_active', 'is_hot_sale', 'has_gift_wrap')
    list_filter = ('is_active', 'is_stock', 'is_hot_sale', 'has_gift_wrap', 'category', 'company')
    search_fields = ('product_name', 'product_description')
    list_editable = ('orignal_price', 'discount_percentage', 'is_stock', 'is_active', 'is_hot_sale', 'has_gift_wrap')
    readonly_fields = ('slug', 'created_at')
    inlines = [FeatureProductImageInline, ProductDescriptionInline, ReviewInline]
    fieldsets = (
        ('معلومات المنتج الأساسية', {
            'fields': ('product_name', 'slug', 'product_description', 'category', 'company')
        }),
        ('التسعير والخصم', {
            'fields': ('orignal_price', 'discount_percentage')
        }),
        ('الصورة الأساسية', {
            'fields': ('product_image',)
        }),
        ('حالة المنتج والعروض', {
            'fields': ('is_stock', 'is_active', 'is_hot_sale', 'sale_end_time', 'has_gift_wrap', 'created_at')
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

# Register Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('name', 'review', 'product__product_name')

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
    list_display = ('full_name', 'phone', 'city')
    search_fields = ('full_name', 'phone')
    fieldsets = (
        ('معلومات العميل', {
            'fields': ('full_name', 'phone')
        }),
        ('العنوان', {
            'fields': ('address', 'city')
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )

# Register Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'customer_phone', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'customer__full_name', 'customer__phone')
    readonly_fields = ('order_id', 'created_at', 'products_data')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    actions = ['mark_as_completed', 'mark_as_processing']

    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('order_id', 'customer', 'status', 'created_at')
        }),
        ('التفاصيل المالية والمنتجات', {
            'fields': ('total_amount', 'products_data')
        }),
    )

    def customer_phone(self, obj):
        return obj.customer.phone
    customer_phone.short_description = 'الهاتف'

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "تحديد الطلبات كـ 'مكتمل'"

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = "تحديد الطلبات كـ 'قيد المعالجة'"

# Register Contact
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('created_at',)
