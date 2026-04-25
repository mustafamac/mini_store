import random, uuid, requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from stor.models import Category, Company, Product, FeatureProductImage, ProductDescription, Review

PEXELS_KEY = "VGl8IQJ59qhTPpEuqvq0TeNMX8cQzT9kTmW8Hpc4jfvzLII9MMlYCwP3"

CATS = [
    "ماوس وكيبورد",
    "سماعات وهيدسيت",
    "شاشات",
    "كاميرات ويب",
    "هاردات وفلاشات",
    "حوامل وكابلات",
    "كروت شبكة وراوتر",
    "مراوح وتبريد",
]

COS = [
    {"name": "Logitech",        "cat": "ماوس وكيبورد"},
    {"name": "Razer",           "cat": "ماوس وكيبورد"},
    {"name": "HyperX",          "cat": "سماعات وهيدسيت"},
    {"name": "SteelSeries",     "cat": "سماعات وهيدسيت"},
    {"name": "Samsung",         "cat": "شاشات"},
    {"name": "LG",              "cat": "شاشات"},
    {"name": "Logitech",        "cat": "كاميرات ويب"},
    {"name": "Western Digital", "cat": "هاردات وفلاشات"},
    {"name": "Kingston",        "cat": "هاردات وفلاشات"},
    {"name": "Anker",           "cat": "حوامل وكابلات"},
    {"name": "TP-Link",         "cat": "كروت شبكة وراوتر"},
    {"name": "Cooler Master",   "cat": "مراوح وتبريد"},
]

PRODUCTS = [
    # ماوس وكيبورد
    {"name": "Logitech MX Master 3S ماوس لاسلكي",           "cat": "ماوس وكيبورد",    "co": "Logitech",        "q": "logitech wireless mouse",          "price": 1850, "disc": 10,
     "desc": "ماوس لاسلكي احترافي بدقة 8000 DPI وعجلة تمرير مغناطيسية. مثالي للتصميم والبرمجة. يعمل 70 يوم على شحنة واحدة. متوفر على جوميا مصر.",
     "features": ["دقة 8000 DPI قابلة للتعديل", "اتصال Bluetooth و USB Receiver", "عجلة تمرير مغناطيسية صامتة", "بطارية تدوم 70 يوماً", "متوافق مع Windows و Mac"]},

    {"name": "Razer DeathAdder V3 ماوس جيمنج",              "cat": "ماوس وكيبورد",    "co": "Razer",           "q": "razer gaming mouse",               "price": 1650, "disc": 15,
     "desc": "ماوس جيمنج خفيف الوزن 59 جرام بدقة 30,000 DPI وسرعة استجابة 0.2ms. الخيار الأول للاعبين المحترفين.",
     "features": ["دقة 30,000 DPI", "وزن 59 جرام فقط", "زر ضغط بضمان 90 مليون نقرة", "إضاءة Razer Chroma RGB", "كابل Speedflex مرن"]},

    {"name": "Logitech G Pro X Mechanical Keyboard",        "cat": "ماوس وكيبورد",    "co": "Logitech",        "q": "mechanical gaming keyboard",       "price": 2800, "disc": 10,
     "desc": "كيبورد ميكانيكي احترافي TKL بمفاتيح GX Blue قابلة للتبديل. يستخدمه محترفو البطولات العالمية.",
     "features": ["مفاتيح GX قابلة للتبديل", "تصميم TKL مدمج", "إضاءة RGB لكل مفتاح", "كابل مفصول", "ضمان سنتين"]},

    {"name": "Razer BlackWidow V4 Keyboard ميكانيكي",       "cat": "ماوس وكيبورد",    "co": "Razer",           "q": "razer mechanical keyboard rgb",    "price": 3200, "disc": 0,
     "desc": "كيبورد ميكانيكي بمفاتيح Razer Green الشهيرة وإضاءة Chroma RGB بـ 16.8 مليون لون. مع عجلة تحكم بالصوت.",
     "features": ["مفاتيح Razer Green الميكانيكية", "إضاءة Chroma RGB", "عجلة تحكم بالصوت", "مسند راحة مغناطيسي", "USB Pass-through"]},

    {"name": "Logitech G840 XL Gaming Mouse Pad",           "cat": "ماوس وكيبورد",    "co": "Logitech",        "q": "gaming mouse pad xl desk",         "price": 550,  "disc": 20,
     "desc": "ماوس باد XL يغطي المكتب بالكامل 90×40 سم. سطح ناعم لأقصى دقة وقاعدة مطاط مانعة للانزلاق.",
     "features": ["مقاس XL 90x40 سم", "سطح قماشي ناعم", "قاعدة مطاط مانعة للانزلاق", "حواف مخيطة لمنع التآكل", "مناسب لجميع أنواع الماوس"]},

    # سماعات وهيدسيت
    {"name": "HyperX Cloud II Wireless هيدسيت جيمنج",       "cat": "سماعات وهيدسيت", "co": "HyperX",          "q": "hyperx gaming headset wireless",   "price": 2200, "disc": 15,
     "desc": "هيدسيت جيمنج لاسلكي بصوت 7.1 Surround وبطارية 30 ساعة. ميكروفون معزول للضوضاء بجودة حسابية عالية.",
     "features": ["صوت 7.1 Virtual Surround", "بطارية 30 ساعة", "ميكروفون معزول للضوضاء", "وسادات ذاكرة مريحة", "تردد 10Hz - 21kHz"]},

    {"name": "SteelSeries Arctis Nova Pro هيدسيت",          "cat": "سماعات وهيدسيت", "co": "SteelSeries",     "q": "steelseries gaming headset",       "price": 4500, "disc": 10,
     "desc": "هيدسيت احترافي بنظام ANC وميكروفون ClearCast قابل للسحب. نظام شحن مزدوج للاستخدام المتواصل.",
     "features": ["Active Noise Cancellation", "ميكروفون ClearCast", "نظام بطارية مزدوج", "DAC خارجي عالي الجودة", "متوافق مع PC و PlayStation"]},

    {"name": "HyperX Cloud Stinger 2 سماعة جيمنج",          "cat": "سماعات وهيدسيت", "co": "HyperX",          "q": "gaming headset pc",                "price": 899,  "disc": 25,
     "desc": "هيدسيت جيمنج بسعر مناسب وجودة صوت ممتازة. ميكروفون قابل للتعديل مع زر كتم صوت على الكأس.",
     "features": ["درايفر 40mm عالي الدقة", "ميكروفون قابل للكسر 90 درجة", "زر كتم صوت على الكأس", "وزن خفيف 275 جرام", "توصيل 3.5mm و USB"]},

    # شاشات
    {"name": "Samsung 27 inch IPS FHD 165Hz شاشة جيمنج",   "cat": "شاشات",           "co": "Samsung",         "q": "samsung gaming monitor 27 inch",   "price": 4200, "disc": 10,
     "desc": "شاشة جيمنج 27 بوصة IPS بمعدل تحديث 165Hz واستجابة 1ms MPRT. تقنية AMD FreeSync Premium لصورة سلسة.",
     "features": ["165Hz refresh rate", "1ms MPRT response", "AMD FreeSync Premium", "HDR10 support", "Eye Saver Mode"]},

    {"name": "LG 24 inch IPS FHD 75Hz شاشة مكتب",          "cat": "شاشات",           "co": "LG",              "q": "lg office monitor 24 inch",        "price": 2800, "disc": 5,
     "desc": "شاشة مكتبية 24 بوصة IPS بألوان حقيقية 99% sRGB. مثالية للعمل والتصميم بميزة Reader Mode.",
     "features": ["لوحة IPS 99% sRGB", "Reader Mode للعين", "OnScreen Control", "HDMI و DisplayPort", "قابلة للتعديل في الارتفاع"]},

    # كاميرات ويب
    {"name": "Logitech C920 HD Pro Webcam 1080p",           "cat": "كاميرات ويب",     "co": "Logitech",        "q": "logitech webcam 1080p hd",         "price": 1600, "disc": 10,
     "desc": "كاميرا ويب احترافية 1080p 30fps مع ميكروفون ستيريو مدمج. مثالية للاجتماعات والستريم ومكالمات الفيديو.",
     "features": ["دقة 1080p Full HD", "ميكروفون ستيريو مدمج", "تركيز تلقائي", "ضغط H.264", "متوافق مع Zoom و Teams"]},

    {"name": "Logitech StreamCam USB-C كاميرا ستريم",       "cat": "كاميرات ويب",     "co": "Logitech",        "q": "streaming webcam usb-c",           "price": 2400, "disc": 15,
     "desc": "كاميرا ستريم احترافية 1080p 60fps بمنفذ USB-C. AI Face Tracking لتتبع وجهك تلقائياً. الخيار الأول للكونتنت كريتورز.",
     "features": ["1080p 60fps", "AI Face Tracking", "منفذ USB-C", "تركيز ذكي تلقائي", "تثبيت أفقي وعمودي"]},

    # هاردات وفلاشات
    {"name": "WD Blue SSD 1TB SATA هارد داخلي",             "cat": "هاردات وفلاشات",  "co": "Western Digital", "q": "ssd internal hard drive",          "price": 1900, "disc": 10,
     "desc": "هارد SSD داخلي 1TB بسرعة قراءة 560 MB/s. يرفع أداء الكمبيوتر بشكل ملحوظ مع ضمان 5 سنوات.",
     "features": ["سرعة قراءة 560 MB/s", "سرعة كتابة 530 MB/s", "ضمان 5 سنوات", "واجهة SATA III", "مناسب للابتوب والديسكتوب"]},

    {"name": "Kingston 32GB USB 3.2 فلاشة سريعة",           "cat": "هاردات وفلاشات",  "co": "Kingston",        "q": "kingston usb flash drive",         "price": 320,  "disc": 0,
     "desc": "فلاشة USB 3.2 بسرعة نقل 200 MB/s بتصميم معدني متين ومدمج. ضمان مدى الحياة من كينجستون.",
     "features": ["USB 3.2 Gen 1", "سرعة قراءة 200 MB/s", "تصميم معدني مدمج", "ضمان مدى الحياة", "متوافق مع Windows و Mac"]},

    {"name": "WD My Passport 2TB هارد خارجي",               "cat": "هاردات وفلاشات",  "co": "Western Digital", "q": "external hard drive portable",     "price": 2100, "disc": 5,
     "desc": "هارد خارجي محمول 2TB بتصميم أنيق وحماية بكلمة سر وتشفير AES 256-bit. USB 3.0 للنقل السريع.",
     "features": ["سعة 2TB", "تشفير AES 256-bit", "USB 3.0", "ضمان 3 سنوات", "متوافق مع PC و Mac"]},

    # حوامل وكابلات
    {"name": "Anker 7-in-1 USB-C Hub هاب متعدد",            "cat": "حوامل وكابلات",   "co": "Anker",           "q": "usb-c hub multiport adapter",      "price": 850,  "disc": 15,
     "desc": "هاب USB-C 7 في 1 مع HDMI 4K و USB 3.0 و SD Card و شحن 100W. مثالي للابتوب.",
     "features": ["HDMI 4K@30Hz", "3 منافذ USB 3.0", "SD و MicroSD Card", "شحن 100W PD", "توصيل فوري بدون درايفر"]},

    {"name": "Anker كابل USB-C شحن سريع 2 متر",             "cat": "حوامل وكابلات",   "co": "Anker",           "q": "usb-c cable fast charging",        "price": 180,  "disc": 0,
     "desc": "كابل USB-C بطول 2 متر يدعم شحن 60W وسرعة نقل بيانات 480 Mbps. مغلف بنايلون متين ضد الالتواء.",
     "features": ["دعم شحن 60W", "نقل بيانات 480 Mbps", "طول 2 متر", "غلاف نايلون متين", "ضمان 18 شهراً"]},

    # كروت شبكة وراوتر
    {"name": "TP-Link Archer AX21 راوتر WiFi 6",            "cat": "كروت شبكة وراوتر","co": "TP-Link",          "q": "tp-link wifi router",              "price": 1650, "disc": 10,
     "desc": "راوتر WiFi 6 بسرعة 1800 Mbps مع 4 هوائيات خارجية. يدعم 80 جهاز في آن واحد بتقنية OFDMA.",
     "features": ["WiFi 6 AX1800", "دعم 80 جهاز متصل", "تقنية OFDMA", "4 هوائيات خارجية", "إعداد سهل عبر تطبيق"]},

    {"name": "TP-Link USB WiFi Adapter كرت شبكة",           "cat": "كروت شبكة وراوتر","co": "TP-Link",          "q": "usb wifi adapter dongle",          "price": 280,  "disc": 0,
     "desc": "كرت شبكة WiFi USB بسرعة 300 Mbps. توصيل ولعب بدون إعداد. يعمل على Windows و Linux.",
     "features": ["سرعة 300 Mbps", "USB 2.0", "Plug and Play", "هوائي قابل للطي", "متوافق مع Windows 11/10/7"]},

    # مراوح وتبريد
    {"name": "Cooler Master Hyper 212 مروحة معالج",         "cat": "مراوح وتبريد",    "co": "Cooler Master",   "q": "cpu cooler fan tower",             "price": 950,  "disc": 15,
     "desc": "مروحة معالج Tower بـ 4 هيت بايب مباشرة وأداء تبريد ممتاز للمعالجات حتى 150W. تثبيت سهل.",
     "features": ["4 Heat Pipes مباشرة", "قدرة تبريد 150W TDP", "مروحة PWM 120mm", "متوافق Intel و AMD", "تركيب بدون أدوات"]},

    {"name": "Cooler Master كيس كمبيوتر MasterBox Q300L",  "cat": "مراوح وتبريد",    "co": "Cooler Master",   "q": "computer case gaming rgb",         "price": 1400, "disc": 10,
     "desc": "كيس كمبيوتر Micro-ATX بجانب شبكي لتدفق هواء ممتاز. يدعم 3 مراوح 120mm وراديتر 240mm.",
     "features": ["هيكل Micro-ATX", "جانب شبكي للتهوية", "يدعم 3 مراوح 120mm", "راديتر 240mm في الأمام", "إدارة كابلات مرتبة"]},
]

REVIEWERS = [
    ("أحمد محمد",     5, "منتج ممتاز وصل بسرعة. الجودة أفضل من توقعاتي وسيشتغل معايا من أول لحظة."),
    ("سارة علي",      4, "جيد جداً والسعر مناسب. التوصيل كان سريع. أنصح به بشدة."),
    ("محمود حسن",     5, "اشتريته من جوميا وأنا سعيد جداً. المنتج أصلي 100%."),
    ("نورا خالد",     4, "الجودة ممتازة والتغليف كان رائع. هشتري تاني من نفس المتجر."),
    ("عمر إبراهيم",   5, "أفضل منتج في الفئة دي. يستاهل كل قرش. التوصيل في 3 أيام."),
    ("ريم أحمد",      3, "المنتج كويس بس التوصيل اتأخر شوية. الجودة مناسبة للسعر."),
]


def pexels_img(query):
    try:
        r = requests.get("https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 5, "size": "large"},
            timeout=15)
        photos = r.json().get("photos", [])
        random.shuffle(photos)
        for p in photos:
            ir = requests.get(p["src"]["large"], timeout=20)
            if ir.status_code == 200 and len(ir.content) > 10000:
                return ContentFile(ir.content, name=uuid.uuid4().hex + ".jpg")
    except Exception as e:
        print("Pexels err: " + str(e))
    return None


def placeholder(label):
    try:
        from PIL import Image, ImageDraw, ImageFont
        clr = random.choice([(30,30,40),(20,50,80),(40,20,60),(10,60,50)])
        img = Image.new("RGB", (800, 800), clr)
        d = ImageDraw.Draw(img)
        d.rectangle([15,15,785,785], outline=(100,180,255), width=3)
        f = ImageFont.load_default()
        t = label[:20]
        bb = d.textbbox((0,0), t, font=f)
        d.text((400-(bb[2]-bb[0])//2, 400-(bb[3]-bb[1])//2), t, fill="white", font=f)
        buf = BytesIO()
        img.save(buf, "JPEG", quality=90)
        buf.seek(0)
        return ContentFile(buf.getvalue(), name=uuid.uuid4().hex + ".jpg")
    except Exception:
        return ContentFile(b"GIF89a", name=uuid.uuid4().hex + ".jpg")


def get_img(name, query):
    img = pexels_img(query)
    if img:
        print("  [IMG] " + name)
        return img
    print("  [PH]  " + name)
    return placeholder(name)


def make_slug(name):
    base = slugify(name) or uuid.uuid4().hex[:8]
    s, n = base, 1
    while Product.objects.filter(slug=s).exists():
        s = base + "-" + str(n); n += 1
    return s


class Command(BaseCommand):
    help = "Seed computer accessories"

    def handle(self, *args, **options):
        hot = list(Product.objects.filter(is_hot_sale=True).values_list("id", flat=True))
        self.stdout.write("Hot Sale saved: " + str(len(hot)))

        Product.objects.exclude(is_hot_sale=True).delete()
        Category.objects.all().delete()
        Company.objects.all().delete()
        self.stdout.write("Cleared.")

        # categories
        cats = {}
        for name in CATS:
            cats[name] = Category.objects.create(category=name)
            self.stdout.write("Cat: " + name)

        # companies - deduplicate by name+cat
        cos = {}
        seen = set()
        for c in COS:
            key = c["name"] + "|" + c["cat"]
            if key in seen:
                continue
            seen.add(key)
            cat_obj = cats.get(c["cat"])
            if not cat_obj:
                continue
            obj = Company.objects.create(category=cat_obj, company=c["name"])
            cos[c["name"]] = obj
            self.stdout.write("Co: " + c["name"])

        # products
        for i, p in enumerate(PRODUCTS, 1):
            cat = cats.get(p["cat"])
            co  = cos.get(p["co"])
            if not cat or not co:
                self.stdout.write("SKIP: " + p["name"])
                continue

            slug = make_slug(p["name"])
            img  = get_img(p["name"], p["q"])

            pr = Product(
                category=cat, company=co,
                product_name=p["name"],
                product_description=p["desc"],
                orignal_price=p["price"],
                discount_percentage=p["disc"],
                is_stock=True, is_active=True,
                is_hot_sale=False, sale_end_time=None,
                has_gift_wrap=random.random() < 0.15,
                slug=slug,
            )
            pr.save()
            pr.product_image.save(slug + ".jpg", img, save=True)

            # feature images
            for feat_q in [p["q"], p["q"] + " detail", p["q"] + " close up"]:
                fi = get_img(p["name"] + " extra", feat_q)
                fimg_obj = FeatureProductImage(product=pr)
                fimg_obj.image.save(uuid.uuid4().hex + ".jpg", fi, save=True)

            # features/descriptions
            for feat in p.get("features", []):
                ProductDescription.objects.create(product=pr, feature=feat)

            # review
            reviewer = random.choice(REVIEWERS)
            Review.objects.create(
                product=pr,
                name=reviewer[0],
                rating=reviewer[1],
                review=reviewer[2],
            )

            self.stdout.write(self.style.SUCCESS(
                str(i) + ". " + p["name"] + " | " + str(p["price"]) + " EGP | " + str(p["disc"]) + "% off"
            ))

        self.stdout.write(self.style.SUCCESS(
            "DONE! " + str(len(PRODUCTS)) + " products. Hot Sale kept: " + str(len(hot))
        ))
