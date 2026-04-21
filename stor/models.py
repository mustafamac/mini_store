from django.db import models
from django.utils.text import slugify
import uuid

# ------------------------------------------------------------
# 1. نماذج المنتجات والفئات (كما هي تقريباً، بدون تغيير)
# ------------------------------------------------------------
class Category(models.Model):
    category = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.category

class Company(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='companies', null=True, blank=True)
    company = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-company']

    def __str__(self):
        return self.company

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=100)
    product_description = models.TextField()
    orignal_price = models.PositiveIntegerField(default=0)
    discount_percentage = models.PositiveIntegerField(default=0)
    warranty = models.IntegerField(default=1)
    product_image = models.ImageField(upload_to='product_images/')
    is_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_trending = models.BooleanField(default=False)
    slug = models.SlugField(blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def discounted_price(self):
        discount_amount = (float(self.discount_percentage) / 100) * float(self.orignal_price)
        discounted_price = float(self.orignal_price) - discount_amount
        return round(discounted_price, 2)

    def formatted_price(self):
        return "{:.2f}".format(self.orignal_price)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name

# ------------------------------------------------------------
# 2. سلة تسوق بدون مستخدم (تعتمد على session_key)
# ------------------------------------------------------------
class Cart(models.Model):
    session_key = models.CharField(max_length=100, db_index=True)  # معرف الجلسة
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session_key', 'product')  # منتج واحد لكل جلسة

    def get_total_price(self):
        return self.quantity * self.product.discounted_price

    def __str__(self):
        return f"Session {self.session_key} - {self.product.product_name} x{self.quantity}"

# ------------------------------------------------------------
# 3. بيانات العميل (للطلب الواحد)
# ------------------------------------------------------------
class CustomerInfo(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name

# ------------------------------------------------------------
# 4. الطلب النهائي (يحتوي على نسخة من السلة + بيانات العميل)
# ------------------------------------------------------------
class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'قيد الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    )
    order_id = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, related_name='orders')
    products_data = models.JSONField()  # تخزين قائمة المنتجات: [{"product_id":1, "name":"...", "price":..., "quantity":2}]
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            # إنشاء رقم طلب فريد (مكون من 10 أحرف/أرقام)
            self.order_id = str(uuid.uuid4()).replace('-', '')[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id} - {self.customer.full_name}"



# باقي النماذج (FeatureProductImage, ProductDescription, AdditionalInformation, Review, Profile) 

class FeatureProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feature_product_images')
    image = models.ImageField(upload_to='feature_product_images/')

    def __str__(self):
        return self.product.product_name

class ProductDescription(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_descriptions')
    feature = models.CharField(max_length=100)
    product_description = models.TextField()
    product_image = models.ImageField(upload_to='product_description_images/')

    def __str__(self):
        return self.product.product_name

class AdditionalInformation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_informations')
    new_product_name = models.CharField(max_length=100, blank=True, null=True)
    feature = models.CharField(max_length=100)
    exisiting_product_description1 = models.TextField(null=True, blank=True)
    new_product_description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['feature']
        
    def __str__(self):
        return f"{self.product.product_name} - {self.feature}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_review')
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    review = models.TextField()
    rating = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} - {self.product.product_name}"

class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200, default='رسالة من موقع ITQAN')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"