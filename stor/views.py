import json
import urllib.error
import urllib.request
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .models import Product, Category, Contact, Cart, CustomerInfo, Order
from .forms import CustomerInfoForm

def index(request):
    """
    الصفحة الرئيسية: تعرض جميع المنتجات النشطة والمتوفرة في المخزون
    """
    products = Product.objects.filter(
        is_active=True,
        is_stock=True
    ).order_by('-created_at')  # الأحدث أولاً

    featured_products = Product.objects.filter(
        is_active=True,
        is_stock=True,
        is_trending=True
    ).order_by('-created_at')

    context = {
        'products': products,
        'featured_products': featured_products,
    }
    return render(request, 'stor/index.html', context)


def product_detail(request, slug):
    """
    صفحة تفاصيل المنتج (عند النقر على أي منتج في السلايدر)
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    context = {
        'product': product,
    }
    return render(request, 'stor/product_detail.html', context)


def contact(request):
    """
    صفحة التواصل - عرض النموذج ومعالجة الإرسال
    """
    if request.method == 'POST':
        name = request.POST.get('first_name', '') + ' ' + request.POST.get('last_name', '')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'رسالة من موقع ITQAN')
        message = request.POST.get('message')
        
        if name.strip() and email and message:
            Contact.objects.create(
                name=name.strip(),
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'تم إرسال رسالتك بنجاح، سوف نتواصل معك قريباً.')
        else:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة.')
        
        return redirect('stor:contact')
    
    return render(request, 'stor/contact.html')


def product_list(request):
    """
    صفحة قائمة المنتجات مع قسم المنتجات المميزة
    """
    products = Product.objects.filter(is_active=True, is_stock=True)
    featured_products = Product.objects.filter(is_active=True, is_stock=True).order_by('-created_at')[:8]  # أحدث 8 منتجات كمميزة
    
    context = {
        'products': products,
        'featured_products': featured_products,
    }
    return render(request, 'stor/product_list.html', context)


def cart_view(request):
    """
    عرض محتويات السلة (تعتمد على session)
    """
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    carts = Cart.objects.filter(session_key=session_key)
    total = sum(cart.get_total_price() for cart in carts)
    context = {
        'carts': carts,
        'total': total,
    }
    return render(request, 'stor/cart.html', context)


def add_to_cart(request, product_id):
    """
    إضافة منتج إلى السلة (via AJAX أو POST)
    """
    product = get_object_or_404(Product, id=product_id, is_active=True, is_stock=True)
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    cart, created = Cart.objects.get_or_create(
        session_key=session_key,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart.quantity += 1
        cart.save()
    
    messages.success(request, f'تم إضافة {product.product_name} إلى السلة.')
    return redirect('stor:cart')


def checkout(request):
    """
    صفحة الدفع: نموذج بيانات العميل
    """
    session_key = request.session.session_key
    if not session_key:
        return redirect('stor:cart')
    
    carts = Cart.objects.filter(session_key=session_key)
    if not carts:
        messages.error(request, 'السلة فارغة.')
        return redirect('stor:cart')
    
    total = sum(cart.get_total_price() for cart in carts)
    
    if request.method == 'POST':
        form = CustomerInfoForm(request.POST)
        if form.is_valid():
            customer = form.save()
            products_data = []
            for cart in carts:
                products_data.append({
                    'product_id': cart.product.id,
                    'name': cart.product.product_name,
                    'price': float(cart.product.discounted_price),
                    'quantity': cart.quantity
                })
            order = Order.objects.create(
                customer=customer,
                products_data=products_data,
                total_amount=total
            )

            subject = f'طلب جديد #{order.order_id} من {customer.full_name}'
            order_lines = [
                'تفاصيل الطلب:',
                f'رقم الطلب: {order.order_id}',
                f'اسم العميل: {customer.full_name}',
                f'البريد الإلكتروني: {customer.email}',
                f'الهاتف: {customer.phone}',
                f'المدينة: {customer.city}',
                f'العنوان: {customer.address}',
                f'ملاحظات: {customer.notes or "-"}',
                '',
                'المنتجات:'
            ]
            for item in products_data:
                order_lines.append(
                    f"- {item['name']} | الكمية: {item['quantity']} | السعر للوحدة: {item['price']} ريال | الإجمالي: {item['price'] * item['quantity']} ريال"
                )
            order_lines.append('')
            order_lines.append(f'الإجمالي الكلي: {total} ريال')
            message = '\n'.join(order_lines)

            email_recipients = getattr(settings, 'ORDER_NOTIFICATION_EMAILS', [])
            if email_recipients:
                from django.template.loader import render_to_string
                html_message = render_to_string('stor/email/order_notification.html', {
                    'order': order,
                    'customer': customer,
                    'products_data': products_data,
                    'total': total,
                })
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        email_recipients,
                        fail_silently=True,
                        html_message=html_message
                    )
                except Exception as e:
                    logger.error(f"Failed to send email notification for order {order.order_id}: {str(e)}")

            carts.delete()  # حذف السلة بعد الطلب
            messages.success(request, 'تم استلام طلبك بنجاح.')
            return redirect('stor:order_success', order_id=order.order_id)
    else:
        form = CustomerInfoForm()
    
    context = {
        'form': form,
        'carts': carts,
        'total': total,
    }
    return render(request, 'stor/checkout.html', context)


def order_success(request, order_id):
    """
    صفحة تأكيد الطلب
    """
    order = get_object_or_404(Order, order_id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'stor/order_success.html', context)