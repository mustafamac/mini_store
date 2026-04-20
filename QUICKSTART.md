# 🚀 بدء سريع - ITQAN Tech Store

## تشغيل سريع (في دقيقة واحدة)

### Windows 🪟

```bash
# 1. فتح command prompt في المشروع
cd C:\Users\toshiba\Desktop\mini_store

# 2. تفعيل البيئة الافتراضية
mini\Scripts\activate

# 3. تشغيل الخادم
python manage.py runserver

# 4. فتح المتصفح
http://localhost:8000
```

### Linux/Mac 🐧

```bash
# 1. الذهاب للمجلد
cd ~/Desktop/mini_store  # أو المسار الفعلي

# 2. تفعيل البيئة
source mini/bin/activate

# 3. تشغيل الخادم
python manage.py runserver

# 4. فتح متصفحك
http://localhost:8000
```

---

## الوصول لوحة التحكم

**العنوان:** http://localhost:8000/admin/
**المستخدم:** استخدم بيانات المسؤول التي أنشأتها

### إنشاء مسؤول جديد (إذا لم تنشئ واحد)

```bash
python manage.py createsuperuser
```

---

## المشاكل الشائعة

### المشكلة: "Port 8000 is already in use"
```bash
python manage.py runserver 8001
# ثم اذهب للـ http://localhost:8001
```

### المشكلة: "NameError: name 'contact' is not defined"
```bash
python manage.py migrate
```

### المشكلة: الصور لا تظهر
```bash
python manage.py collectstatic --no-input
```

---

## أوامر مهمة

```bash
# فحص الأخطاء
python manage.py check

# إنشاء مسؤول جديد
python manage.py createsuperuser

# تطبيق الهجرات
python manage.py migrate

# إنشاء هجرة جديدة
python manage.py makemigrations

# جمع الملفات الثابتة
python manage.py collectstatic

# فتح برنامج قاعدة البيانات
python manage.py dbshell

# تشغيل الاختبارات
python manage.py test
```

---

## الملفات التي تحتاج لتعديلها قبل النشر

### 1. `.env` (أنشئ نسخة من `.env.example`)
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```

### 2. `src/settings.py`
- غير `SECRET_KEY`
- اضبط `DEBUG = False`
- حدّث `ALLOWED_HOSTS`

### 3. قاعدة البيانات
- انقل من SQLite إلى PostgreSQL

---

## ملفات التعريفات المهمة

- **README.md** → الوثائق الكاملة
- **DEPLOYMENT.md** → خطوات النشر
- **PROJECT_SUMMARY.md** → ملخص شامل
- **requirements.txt** → المتطلبات
- **Procfile** → لنشر Heroku

---

## روابط سريعة

```
الصفحة الرئيسية:     http://localhost:8000/
المنتجات:           http://localhost:8000/products/
عربة التسوق:        http://localhost:8000/cart/
الاتصال:            http://localhost:8000/contact/
لوحة التحكم:        http://localhost:8000/admin/
```

---

## نصائح مهمة

✅ تأكد من تفعيل البيئة الافتراضية قبل كل شيء

✅ لا تعدّل الملفات المهمة مباشرة قبل النسخ الاحتياطية

✅ استخدم `--no-input` مع `collectstatic` في الإنتاج

✅ فعّل `DEBUG = False` فقط بعد التأكد من الإعدادات

✅ احفظ البيانات المهمة قبل أي تحديث

---

**تم!** المشروع جاهز للتشغيل والاستخدام الفوري 🎉

**للمساعدة:** راجع README.md أو DEPLOYMENT.md
