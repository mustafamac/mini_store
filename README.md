# ITQAN Tech Store - متجر اتقان تك

**أسم المتجر:** ITQAN Tech Store
**الوصف:** متجر إلكتروني متقدم لبيع المنتجات التقنية

## مميزات المشروع

✅ **واجهة تجارة إلكترونية كاملة**
- صفحة رئيسية مع عرض المنتجات
- تفاصيل المنتج الشاملة
- عربة تسوق (حفظ في الجلسة)
- عملية الدفع مع نموذج بيانات العميل
- قائمة الاتصال والرسائل

✅ **لوحة التحكم الإدارية**
- إدارة المنتجات والفئات
- إدارة الطلبات والعملاء
- إدارة التقييمات والملاحظات
- عرض رسائل الاتصال

✅ **التصميم المتجاوب**
- متوافق مع جميع الأجهزة (مكتب، تابلت، موبايل)
- هوية بصرية حديثة وموحدة
- ألوان: تركواز #1F9EAA، برتقالي #F18722

✅ **قاعدة البيانات**
- 11 نموذج مترابط
- شامل للمنتجات والطلبات والعملاء والتقييمات

## متطلبات التثبيت

```bash
Python 3.11+
Django 6.0.4
Pillow (معالجة الصور)
```

## خطوات التثبيت المحلي

### 1. استنساخ المستودع
```bash
git clone <repository-url>
cd mini_store
```

### 2. إنشاء البيئة الافتراضية
```bash
python -m venv mini
source mini/bin/activate  # على Linux/Mac
# أو
mini\Scripts\activate  # على Windows
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. تطبيق الهجرات
```bash
python manage.py migrate
```

### 5. إنشاء حساب مسؤول
```bash
python manage.py createsuperuser
```

### 6. جمع الملفات الثابتة (للإنتاج)
```bash
python manage.py collectstatic
```

### 7. تشغيل الخادم المحلي
```bash
python manage.py runserver
```

ثم زيارة: http://localhost:8000

## الوصول لوحة التحكم

اذهب إلى `http://localhost:8000/admin/` واستخدم بيانات المسؤول

## هيكل المشروع

```
mini_store/
├── src/                    # إعدادات المشروع الرئيسية
│   ├── settings.py        # إعدادات Django
│   ├── urls.py            # التوجيهات الرئيسية
│   └── wsgi.py            # محرك WSGI
├── stor/                  # تطبيق المتجر
│   ├── models.py          # نماذج قاعدة البيانات
│   ├── views.py           # وظائف المعالجة
│   ├── urls.py            # توجيهات التطبيق
│   ├── admin.py           # لوحة التحكم
│   ├── forms.py           # النماذج المستخدمة
│   └── templates/         # الصفحات HTML
├── templates/             # الصفحات الأساسية
├── static/                # الملفات الثابتة (CSS, JS)
├── media/                 # صور المنتجات والملفات
├── manage.py              # أداة Django
└── requirements.txt       # المتطلبات
```

## نماذج قاعدة البيانات

| النموذج | الوصف |
|---------|-------|
| **Category** | فئات المنتجات |
| **Company** | الشركات المصنعة |
| **Product** | المنتجات بجميع التفاصيل |
| **FeatureProductImage** | صور إضافية للمنتل |
| **ProductDescription** | وصف ميزات المنتج |
| **AdditionalInformation** | معلومات إضافية |
| **Review** | تقييمات العملاء |
| **Cart** | عربة التسوق |
| **CustomerInfo** | معلومات العميل |
| **Order** | الطلبات |
| **Contact** | رسائل الاتصال |

## الألوان والهوية البصرية

```
اللون الأساسي:    #1F9EAA (تركواز)
اللون الثانوي:    #F18722 (برتقالي)
اللون الرمادي:    #6B6B6B
خلفية فاتحة:      #f7f7f7
```

## عجيهات الـ API

### المنتجات
- `GET /` - الصفحة الرئيسية
- `GET /products/` - قائمة المنتجات
- `GET /product/<slug>/` - تفاصيل المنتج

### عربة التسوق
- `GET /cart/` - عرض العربة
- `POST /add-to-cart/<id>/` - إضافة منتج

### الطلبات
- `GET /checkout/` - صفحة الدفع
- `POST /checkout/` - تأكيد الطلب
- `GET /order-success/<order_id>/` - تأكيد النجاح

### الاتصال
- `GET /contact/` - نموذج الاتصال
- `POST /contact/` - إرسال الرسالة

## التخطيط للإنتاج

### قبل النشر

1. **تحديث أمان الإعدادات:**
   - غيّر `SECRET_KEY` إلى مفتاح عشوائي قوي
   - اضبط `DEBUG = False`
   - حدّث `ALLOWED_HOSTS` بنطاقك

2. **تكوين البريد الإلكتروني:**
   ```python
   EMAIL_HOST = 'your-smtp-server'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your-email'
   EMAIL_HOST_PASSWORD = 'your-password'
   ```

3. **قاعدة البيانات:**
   - استخدم PostgreSQL للإنتاج بدلاً من SQLite
   - أنشئ نسخة احتياطية من البيانات

4. **الملفات الثابتة:**
   ```bash
   python manage.py collectstatic --no-input
   ```

5. **HTTPS و SSL:**
   - استخدم شهادة SSL صحيحة
   - اجعل `SECURE_SSL_REDIRECT = True` في الإنتاج

### النشر على Heroku

```bash
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### النشر على PythonAnywhere

1. اصنع حساب على PythonAnywhere
2. حمّل الملفات
3. اضبط الإعدادات في ملف WSGI
4. أعد تشغيل التطبيق

## معالجة الأخطاء الشائعة

### TemplateDoesNotExist
```
تأكد من اسم المجلد: templates/stor/
```

### ميجريشن معطلة
```bash
python manage.py showmigrations
python manage.py migrate --fake stor 0001
```

### الصور لا تظهر
```bash
python manage.py collectstatic
تأكد من: MEDIA_URL و MEDIA_ROOT
```

## التطوير المستقبلي

- [ ] نظام الدفع الحقيقي (Stripe, PayPal)
- [ ] نظام حسابات المستخدمين
- [ ] تتبع الطلبات
- [ ] نظام التقييمات المتقدم
- [ ] تحسين محرك البحث
- [ ] إضافة قائمة الرغبات
- [ ] نظام الكوبونات والخصومات

## المساهمة والدعم

للإبلاغ عن الأخطاء أو الاقتراحات، تواصل معنا.

## الترخيص

هذا المشروع محمي بموجب الترخيص المناسب.

---

**آخر تحديث:** 2024
**الإصدار:** 1.0
