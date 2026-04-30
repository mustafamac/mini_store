import json
import urllib.error
import urllib.request
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .models import Product, Category, Contact, Cart, CustomerInfo, Order
from .forms import CustomerInfoForm
from django.http import HttpResponse

def send_test_email(request):
    send_mail(
        subject='Test Email',
        message='This is a test email from Django.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['recipient@example.com'],
        fail_silently=False,
    )
    return HttpResponse('Email sent!')

def index(request):
    """
    الصفحة الرئيسية: تعرض جميع المنتجات النشطة والمتوفرة في المخزون
    """
    products = Product.objects.filter(
        is_active=True,
        is_stock=True
    ).order_by('-created_at')  # الأحدث أولاً

    hot_sale_products = Product.objects.filter(
        is_active=True,
        is_stock=True,
        is_hot_sale=True
    ).order_by('-created_at')

    context = {
        'products': products,
        'hot_sale_products': hot_sale_products,
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
    
    cart_items = Cart.objects.filter(session_key=session_key).select_related('product')
    total = sum(item.get_total_price() for item in cart_items)
    total_quantity = sum(item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total': total,
        'total_quantity': total_quantity,
    }
    return render(request, 'stor/cart.html', context)


def add_to_cart(request, product_id):
    """
    إضافة منتج إلى السلة (عبر POST فقط لأسباب أمنية)
    """
    if request.method != 'POST':
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
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


def cart_update_ajax(request):
    """
    تحديث كمية المنتج في السلة عبر AJAX
    """
    from django.http import JsonResponse
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_id = data.get('cart_id')
            change = data.get('change', 0)
            
            cart = get_object_or_404(Cart, id=cart_id)
            
            if change > 0:
                cart.quantity += change
            elif change < 0 and cart.quantity > 1:
                cart.quantity += change  # negative value will decrease
                if cart.quantity < 1:
                    cart.quantity = 1
            
            cart.save()
            
            # Recalculate totals
            session_key = request.session.session_key
            carts = Cart.objects.filter(session_key=session_key)
            total = sum(c.get_total_price() for c in carts)
            total_quantity = sum(c.quantity for c in carts)
            
            return JsonResponse({
                'success': True,
                'quantity': cart.quantity,
                'item_total': cart.get_total_price(),
                'total': total,
                'total_quantity': total_quantity
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False}, status=400)


def cart_remove_ajax(request):
    """
    حذف منتج من السلة عبر AJAX
    """
    from django.http import JsonResponse
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_id = data.get('cart_id')
            
            cart = get_object_or_404(Cart, id=cart_id)
            cart.delete()
            
            # Recalculate totals
            session_key = request.session.session_key
            carts = Cart.objects.filter(session_key=session_key)
            total = sum(c.get_total_price() for c in carts)
            total_quantity = sum(c.quantity for c in carts)
            
            return JsonResponse({
                'success': True,
                'total': total,
                'total_quantity': total_quantity,
                'items_count': carts.count()
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False}, status=400)


def checkout(request):
    """
    إعادة توجيه إلى صفحة السلة — الطلب يتم من خلال السلة مباشرة
    """
    return redirect('stor:cart')


def place_order(request):
    """
    معالجة طلب الشراء عبر AJAX — ريكوست واحد فقط من صفحة السلة
    """
    from django.http import JsonResponse

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        customer_name = data.get('customer_name', '').strip()
        phone = data.get('phone', '').strip()
        address = data.get('address', '').strip()
        notes = data.get('notes', '').strip()
        items = data.get('items', [])
        total = data.get('total', 0)

        if not customer_name or not phone or not address or not items:
            return JsonResponse({'success': False, 'error': 'بيانات ناقصة'}, status=400)

        # إنشاء بيانات العميل
        customer = CustomerInfo.objects.create(
            full_name=customer_name,
            phone=phone,
            address=address,
            notes=notes,
        )

        # بناء بيانات المنتجات
        products_data = []
        for item in items:
            products_data.append({
                'product_id': item.get('product_id'),
                'name': item.get('product_name', ''),
                'price': float(item.get('unit_price', 0)),
                'quantity': int(item.get('quantity', 0)),
            })

        # إنشاء الطلب
        order = Order.objects.create(
            customer=customer,
            products_data=products_data,
            total_amount=total,
        )

        # إرسال إشعار بالبريد الإلكتروني
        subject = f'طلب جديد #{order.order_id} من {customer.full_name}'
        order_lines = [
            'تفاصيل الطلب:',
            f'رقم الطلب: {order.order_id}',
            f'اسم العميل: {customer.full_name}',
            f'الهاتف: {customer.phone}',
            f'العنوان: {customer.address}',
            '',
            'المنتجات:'
        ]
        for item in products_data:
            line_total = item['price'] * item['quantity']
            order_lines.append(
                f"- {item['name']} | الكمية: {item['quantity']} | السعر: {item['price']} ج.م | الإجمالي: {line_total} ج.م"
            )
        order_lines.append('')
        order_lines.append(f'الإجمالي الكلي: {total} ج.م')
        message = '\n'.join(order_lines)

        email_recipients = getattr(settings, 'ORDER_NOTIFICATION_EMAILS', [])
        if email_recipients:
            try:
                from django.template.loader import render_to_string
                html_message = render_to_string('stor/email/order_notification.html', {
                    'order': order,
                    'customer': customer,
                    'products_data': products_data,
                    'total': total,
                })
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    email_recipients,
                    fail_silently=True,
                    html_message=html_message,
                )
            except Exception as e:
                logger.error(f"Failed to send email for order {order.order_id}: {e}")

        # مسح السلة بعد إتمام الطلب
        session_key = request.session.session_key
        if session_key:
            Cart.objects.filter(session_key=session_key).delete()

        return JsonResponse({'success': True, 'order_id': order.order_id})

    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return JsonResponse({'success': False, 'error': 'حدث خطأ في الخادم'}, status=500)

def update_cart_quantity(request, cart_id, action):
    """
    تحديث كمية المنتج في السلة (زيادة أو نقصان) - يدعم AJAX
    """
    from django.http import JsonResponse
    
    cart = get_object_or_404(Cart, id=cart_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if action == 'increase':
            cart.quantity += 1
            cart.save()
        elif action == 'decrease':
            if cart.quantity > 1:
                cart.quantity -= 1
                cart.save()
            else:
                cart.delete()
        
        # Recalculate totals
        session_key = request.session.session_key
        carts = Cart.objects.filter(session_key=session_key)
        total = sum(c.get_total_price() for c in carts)
        total_quantity = sum(c.quantity for c in carts)
        
        return JsonResponse({
            'success': True,
            'quantity': cart.quantity if cart.pk else 0,
            'item_total': cart.get_total_price() if cart.pk else 0,
            'total': total,
            'total_quantity': total_quantity
        })
    
    # Regular redirect for non-AJAX
    if action == 'increase':
        cart.quantity += 1
        cart.save()
    elif action == 'decrease':
        if cart.quantity > 1:
            cart.quantity -= 1
            cart.save()
        else:
            cart.delete()
    return redirect('stor:cart')

def remove_from_cart(request, cart_id):
    """
    حذف منتج من السلة نهائياً - يدعم AJAX
    """
    from django.http import JsonResponse
    
    cart = get_object_or_404(Cart, id=cart_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart.delete()
        
        # Recalculate totals
        session_key = request.session.session_key
        carts = Cart.objects.filter(session_key=session_key)
        total = sum(c.get_total_price() for c in carts)
        total_quantity = sum(c.quantity for c in carts)
        
        return JsonResponse({
            'success': True,
            'total': total,
            'total_quantity': total_quantity,
            'items_count': carts.count()
        })
    
    cart.delete()
    return redirect('stor:cart')


def order_success(request, order_id):
    """
    صفحة تأكيد الطلب
    """
    order = get_object_or_404(Order, order_id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'stor/order_success.html', context)