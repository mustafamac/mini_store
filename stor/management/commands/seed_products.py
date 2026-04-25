import random
import uuid
import requests
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
    # ماوس وكيبورد (5 منتجات)
    {
        "name": "Logitech MX Master 3S ماوس لاسلكي",
        "cat": "ماوس وكيبورد", "co": "Logitech",
        "q": "logitech wireless mouse desk",
        "price": 1850, "disc": 10,
        "desc": "ماوس لاسلكي احترافي بدقة 8000 DPI وعجلة تمرير مغناطيسية. مثالي للتصميم والبرمجة. يعمل 70 يوم على شحنة واحدة.",
        "features": ["دقة 8000 DPI قابلة للتعديل", "اتصال Bluetooth و USB Receiver", "عجلة تمرير مغناطيسية صامتة", "بطارية تدوم 70 يوماً", "متوافق مع Windows و Mac"],
    },
    {
        "name": "Razer DeathAdder V3 ماوس جيمنج",
        "cat": "ماوس وكيبورد", "co": "Razer",
        "q": "razer gaming mouse rgb",
        "price": 1650, "disc": 15,
        "desc": "ماوس جيمنج خفيف الوزن 59 جرام بدقة 30,000 DPI وسرعة استجابة 0.2ms. الخيار الأول للاعبين المحترفين.",
        "features": ["دقة 30,000 DPI", "وزن 59 جرام فقط", "زر ضغط بضمان 90 مليون نقرة", "إضاءة Razer Chroma RGB", "كابل Speedflex مرن"],
    },
    {
        "name": "Logitech G Pro X Mechanical Keyboard",
        "cat": "ماوس وكيبورد", "co": "Logitech",
        "q": "mechanical gaming keyboard rgb backlit",
        "price": 2800, "disc": 10,
        "desc": "كيبورد ميكانيكي احترافي TKL بمفاتيح GX Blue قابلة للتبديل. يستخدمه محترفو البطولات العالمية.",
        "features": ["مفاتيح GX قابلة للتبديل", "تصميم TKL مدمج", "إضاءة RGB لكل مفتاح", "كابل مفصول", "ضمان سنتين"],
    },
    {
        "name": "Razer BlackWidow V4 Keyboard ميكانيكي",
        "cat": "ماوس وكيبورد", "co": "Razer",
        "q": "razer keyboard mechanical gaming",
        "price": 3200, "disc": 0,
        "desc": "كيبورد ميكانيكي بمفاتيح Razer Green الشهيرة وإضاءة Chroma RGB بـ 16.8 مليون لون. مع عجلة تحكم بالصوت.",
        "features": ["مفاتيح Razer Green الميكانيكية", "إضاءة Chroma RGB", "عجلة تحكم بالصوت", "مسند راحة مغناطيسي", "USB Pass-through"],
    },
    {
        "name": "Logitech G840 XL Gaming Mouse Pad",
        "cat": "ماوس وكيبورد", "co": "Logitech",
        "q": "large gaming mouse pad desk mat",
        "price": 550, "disc": 20,
        "desc": "ماوس باد XL يغطي المكتب بالكامل 90×40 سم. سطح ناعم لأقصى دقة وقاعدة مطاط مانعة للانزلاق.",
        "features": ["مقاس XL 90x40 سم", "سطح قماشي ناعم", "قاعدة مطاط مانعة للانزلاق", "حواف مخيطة لمنع التآكل", "مناسب لجميع أنواع الماوس"],
    },

    # سماعات وهيدسيت (4 منتجات)
    {
        "name": "HyperX Cloud II Wireless هيدسيت جيمنج",
        "cat": "سماعات وهيدسيت", "co": "HyperX",
        "q": "gaming headset wireless over ear",
        "price": 2200, "disc": 15,
        "desc": "هيدسيت جيمنج لاسلكي بصوت 7.1 Surround وبطارية 30 ساعة. ميكروفون معزول للضوضاء بجودة عالية.",
        "features": ["صوت 7.1 Virtual Surround", "بطارية 30 ساعة", "ميكروفون معزول للضوضاء", "وسادات ذاكرة مريحة", "تردد 10Hz - 21kHz"],
    },
    {
        "name": "SteelSeries Arctis Nova Pro هيدسيت",
        "cat": "سماعات وهيدسيت", "co": "SteelSeries",
        "q": "professional gaming headset noise cancelling",
        "price": 4500, "disc": 10,
        "desc": "هيدسيت احترافي بنظام ANC وميكروفون ClearCast قابل للسحب. نظام شحن مزدوج للاستخدام المتواصل.",
        "features": ["Active Noise Cancellation", "ميكروفون ClearCast", "نظام بطارية مزدوج", "DAC خارجي عالي الجودة", "متوافق مع PC و PlayStation"],
    },
    {
        "name": "HyperX Cloud Stinger 2 سماعة جيمنج",
        "cat": "سماعات وهيدسيت", "co": "HyperX",
        "q": "hyperx headset gaming pc",
        "price": 899, "disc": 25,
        "desc": "هيدسيت جيمنج بسعر مناسب وجودة صوت ممتازة. ميكروفون قابل للتعديل مع زر كتم صوت على الكأس.",
        "features": ["درايفر 40mm عالي الدقة", "ميكروفون قابل للكسر 90 درجة", "زر كتم صوت على الكأس", "وزن خفيف 275 جرام", "توصيل 3.5mm و USB"],
    },
    {
        "name": "SteelSeries Arctis 1 Wireless سماعة",
        "cat": "سماعات وهيدسيت", "co": "SteelSeries",
        "q": "steelseries headset gaming wireless",
        "price": 1800, "disc": 5,
        "desc": "سماعة لاسلكية خفيفة بصوت نقي وميكروفون قابل للفصل. تدعم Nintendo Switch و PC و Android.",
        "features": ["لاسلكي USB-C", "ميكروفون قابل للفصل", "متوافق مع Switch و PC", "وزن خفيف جداً", "بطارية 20 ساعة"],
    },

    # شاشات (4 منتجات)
    {
        "name": "Samsung 27 inch IPS 165Hz شاشة جيمنج",
        "cat": "شاشات", "co": "Samsung",
        "q": "samsung gaming monitor 27 inch curved",
        "price": 4200, "disc": 10,
        "desc": "شاشة جيمنج 27 بوصة IPS بمعدل تحديث 165Hz واستجابة 1ms MPRT. تقنية AMD FreeSync Premium لصورة سلسة.",
        "features": ["165Hz refresh rate", "1ms MPRT response", "AMD FreeSync Premium", "HDR10 support", "Eye Saver Mode"],
    },
    {
        "name": "LG 24 inch IPS FHD 75Hz شاشة مكتب",
        "cat": "شاشات", "co": "LG",
        "q": "lg office monitor 24 inch desktop",
        "price": 2800, "disc": 5,
        "desc": "شاشة مكتبية 24 بوصة IPS بألوان حقيقية 99% sRGB. مثالية للعمل والتصميم بميزة Reader Mode.",
        "features": ["لوحة IPS 99% sRGB", "Reader Mode للعين", "OnScreen Control", "HDMI و DisplayPort", "قابلة للتعديل في الارتفاع"],
    },
    {
        "name": "Samsung 32 inch QHD 144Hz شاشة كيرفد",
        "cat": "شاشات", "co": "Samsung",
        "q": "samsung curved monitor 32 inch gaming",
        "price": 6500, "disc": 8,
        "desc": "شاشة منحنية 32 بوصة QHD 2560x1440 بمعدل 144Hz. تجربة غمر كاملة مع تقنية Samsung VA Panel.",
        "features": ["دقة QHD 2560x1440", "144Hz refresh rate", "تصميم منحني 1000R", "HDR10", "AMD FreeSync"],
    },
    {
        "name": "LG UltraWide 29 inch شاشة عريضة",
        "cat": "شاشات", "co": "LG",
        "q": "lg ultrawide monitor 29 inch",
        "price": 3900, "disc": 12,
        "desc": "شاشة عريضة 29 بوصة 21:9 IPS بدقة 2560x1080. مثالية للإنتاجية والألعاب مع HDR10.",
        "features": ["نسبة عرض 21:9", "دقة 2560x1080", "IPS بألوان دقيقة", "HDR10", "USB-C و HDMI"],
    },

    # كاميرات ويب (3 منتجات)
    {
        "name": "Logitech C920 HD Pro Webcam 1080p",
        "cat": "كاميرات ويب", "co": "Logitech",
        "q": "webcam 1080p hd streaming",
        "price": 1600, "disc": 10,
        "desc": "كاميرا ويب احترافية 1080p 30fps مع ميكروفون ستيريو مدمج. مثالية للاجتماعات والستريم.",
        "features": ["دقة 1080p Full HD", "ميكروفون ستيريو مدمج", "تركيز تلقائي", "ضغط H.264", "متوافق مع Zoom و Teams"],
    },
    {
        "name": "Logitech StreamCam USB-C كاميرا ستريم",
        "cat": "كاميرات ويب", "co": "Logitech",
        "q": "streaming camera usb-c content creator",
        "price": 2400, "disc": 15,
        "desc": "كاميرا ستريم احترافية 1080p 60fps بمنفذ USB-C. AI Face Tracking لتتبع وجهك تلقائياً.",
        "features": ["1080p 60fps", "AI Face Tracking", "منفذ USB-C", "تركيز ذكي تلقائي", "تثبيت أفقي وعمودي"],
    },
    {
        "name": "Logitech Brio 4K Ultra HD Webcam",
        "cat": "كاميرات ويب", "co": "Logitech",
        "q": "4k webcam professional video call",
        "price": 3800, "disc": 0,
        "desc": "كاميرا ويب 4K مع HDR وتقنية RightLight 3 للإضاءة التلقائية. الأفضل لمؤتمرات الفيديو الاحترافية.",
        "features": ["دقة 4K Ultra HD", "HDR و RightLight 3", "زاوية رؤية 90 درجة", "Windows Hello", "تكبير رقمي 5x"],
    },

    # هاردات وفلاشات (4 منتجات)
    {
        "name": "WD Blue SSD 1TB SATA هارد داخلي",
        "cat": "هاردات وفلاشات", "co": "Western Digital",
        "q": "ssd internal storage hard drive",
        "price": 1900, "disc": 10,
        "desc": "هارد SSD داخلي 1TB بسرعة قراءة 560 MB/s. يرفع أداء الكمبيوتر بشكل ملحوظ مع ضمان 5 سنوات.",
        "features": ["سرعة قراءة 560 MB/s", "سرعة كتابة 530 MB/s", "ضمان 5 سنوات", "واجهة SATA III", "مناسب للابتوب والديسكتوب"],
    },
    {
        "name": "Kingston 32GB USB 3.2 فلاشة سريعة",
        "cat": "هاردات وفلاشات", "co": "Kingston",
        "q": "usb flash drive storage",
        "price": 320, "disc": 0,
        "desc": "فلاشة USB 3.2 بسرعة نقل 200 MB/s بتصميم معدني متين ومدمج. ضمان مدى الحياة من كينجستون.",
        "features": ["USB 3.2 Gen 1", "سرعة قراءة 200 MB/s", "تصميم معدني مدمج", "ضمان مدى الحياة", "متوافق مع Windows و Mac"],
    },
    {
        "name": "WD My Passport 2TB هارد خارجي",
        "cat": "هاردات وفلاشات", "co": "Western Digital",
        "q": "external portable hard drive",
        "price": 2100, "disc": 5,
        "desc": "هارد خارجي محمول 2TB بتصميم أنيق وحماية بكلمة سر وتشفير AES 256-bit. USB 3.0 للنقل السريع.",
        "features": ["سعة 2TB", "تشفير AES 256-bit", "USB 3.0", "ضمان 3 سنوات", "متوافق مع PC و Mac"],
    },
    {
        "name": "Kingston NV2 500GB NVMe SSD",
        "cat": "هاردات وفلاشات", "co": "Kingston",
        "q": "nvme m2 ssd fast storage",
        "price": 1200, "disc": 0,
        "desc": "هارد NVMe M.2 بسرعة قراءة 3500 MB/s. أسرع بـ 6 مرات من SSD العادي. مثالي للألعاب والإنتاج.",
        "features": ["سرعة قراءة 3500 MB/s", "واجهة PCIe 4.0 NVMe", "تصميم M.2 2280", "ضمان 3 سنوات", "استهلاك طاقة منخفض"],
    },

    # حوامل وكابلات (3 منتجات)
    {
        "name": "Anker 7-in-1 USB-C Hub هاب متعدد",
        "cat": "حوامل وكابلات", "co": "Anker",
        "q": "usb-c hub multiport adapter laptop",
        "price": 850, "disc": 15,
        "desc": "هاب USB-C 7 في 1 مع HDMI 4K و USB 3.0 و SD Card و شحن 100W. مثالي للابتوب.",
        "features": ["HDMI 4K@30Hz", "3 منافذ USB 3.0", "SD و MicroSD Card", "شحن 100W PD", "توصيل فوري بدون درايفر"],
    },
    {
        "name": "Anker كابل USB-C شحن سريع 2 متر",
        "cat": "حوامل وكابلات", "co": "Anker",
        "q": "usb-c charging cable braided",
        "price": 180, "disc": 0,
        "desc": "كابل USB-C بطول 2 متر يدعم شحن 60W وسرعة نقل بيانات 480 Mbps. مغلف بنايلون متين ضد الالتواء.",
        "features": ["دعم شحن 60W", "نقل بيانات 480 Mbps", "طول 2 متر", "غلاف نايلون متين", "ضمان 18 شهراً"],
    },
    {
        "name": "Anker حامل لابتوب قابل للتعديل",
        "cat": "حوامل وكابلات", "co": "Anker",
        "q": "laptop stand adjustable aluminum desk",
        "price": 450, "disc": 10,
        "desc": "حامل لابتوب ألومنيوم قابل للتعديل في 6 زوايا. يحسن التهوية ويريح الرقبة أثناء العمل.",
        "features": ["6 زوايا قابلة للتعديل", "هيكل ألومنيوم متين", "قواعد مطاطية مانعة للانزلاق", "قابل للطي للحمل", "يدعم لابتوب حتى 17 بوصة"],
    },

    # كروت شبكة وراوتر (3 منتجات)
    {
        "name": "TP-Link Archer AX21 راوتر WiFi 6",
        "cat": "كروت شبكة وراوتر", "co": "TP-Link",
        "q": "wifi router wireless network home",
        "price": 1650, "disc": 10,
        "desc": "راوتر WiFi 6 بسرعة 1800 Mbps مع 4 هوائيات خارجية. يدعم 80 جهاز في آن واحد بتقنية OFDMA.",
        "features": ["WiFi 6 AX1800", "دعم 80 جهاز متصل", "تقنية OFDMA", "4 هوائيات خارجية", "إعداد سهل عبر تطبيق"],
    },
    {
        "name": "TP-Link USB WiFi Adapter كرت شبكة",
        "cat": "كروت شبكة وراوتر", "co": "TP-Link",
        "q": "usb wifi adapter network dongle",
        "price": 280, "disc": 0,
        "desc": "كرت شبكة WiFi USB بسرعة 300 Mbps. توصيل ولعب بدون إعداد. يعمل على Windows و Linux.",
        "features": ["سرعة 300 Mbps", "USB 2.0", "Plug and Play", "هوائي قابل للطي", "متوافق مع Windows 11/10/7"],
    },
    {
        "name": "TP-Link TL-SG108 سويتش شبكة 8 منافذ",
        "cat": "كروت شبكة وراوتر", "co": "TP-Link",
        "q": "network switch ethernet 8 port",
        "price": 420, "disc": 5,
        "desc": "سويتش شبكة 8 منافذ Gigabit بسرعة 1000 Mbps لكل منفذ. مثالي لربط أجهزة المنزل والمكتب.",
        "features": ["8 منافذ Gigabit 1000Mbps", "Plug and Play", "هيكل معدني متين", "توفير الطاقة التلقائي", "بدون إعداد"],
    },

    # مراوح وتبريد (4 منتجات)
    {
        "name": "Cooler Master Hyper 212 مروحة معالج",
        "cat": "مراوح وتبريد", "co": "Cooler Master",
        "q": "cpu cooler fan tower heatsink",
        "price": 950, "disc": 15,
        "desc": "مروحة معالج Tower بـ 4 هيت بايب مباشرة وأداء تبريد ممتاز للمعالجات حتى 150W. تثبيت سهل.",
        "features": ["4 Heat Pipes مباشرة", "قدرة تبريد 150W TDP", "مروحة PWM 120mm", "متوافق Intel و AMD", "تركيب بدون أدوات"],
    },
    {
        "name": "Cooler Master MasterBox Q300L كيس كمبيوتر",
        "cat": "مراوح وتبريد", "co": "Cooler Master",
        "q": "pc computer case gaming tower",
        "price": 1400, "disc": 10,
        "desc": "كيس كمبيوتر Micro-ATX بجانب شبكي لتدفق هواء ممتاز. يدعم 3 مراوح 120mm وراديتر 240mm.",
        "features": ["هيكل Micro-ATX", "جانب شبكي للتهوية", "يدعم 3 مراوح 120mm", "راديتر 240mm في الأمام", "إدارة كابلات مرتبة"],
    },
    {
        "name": "Cooler Master RGB مروحة كيس 120mm",
        "cat": "مراوح وتبريد", "co": "Cooler Master",
        "q": "rgb case fan 120mm cooling",
        "price": 320, "disc": 0,
        "desc": "مروحة كيس 120mm بإضاءة RGB قابلة للتحكم. هادئة في التشغيل مع أداء تهوية ممتاز.",
        "features": ["إضاءة RGB قابلة للتحكم", "سرعة 650-1800 RPM", "ضوضاء منخفضة 8-27 dBA", "تدفق هواء 38 CFM", "ضمان سنتين"],
    },
    {
        "name": "Cooler Master AIO تبريد مائي 240mm",
        "cat": "مراوح وتبريد", "co": "Cooler Master",
        "q": "aio liquid cpu cooler 240mm radiator",
        "price": 2200, "disc": 8,
        "desc": "تبريد مائي AIO بـ 240mm راديتر ومروحتين RGB. يبرد المعالجات حتى 250W بصمت تام.",
        "features": ["راديتر 240mm", "مروحتان 120mm RGB", "تبريد حتى 250W TDP", "رأس تبريد نحاسي", "متوافق Intel LGA1700 و AMD AM5"],
    },
]

REVIEWERS = [
    ("أحمد محمد",   5, "منتج ممتاز وصل بسرعة. الجودة أفضل من توقعاتي وشغل من أول لحظة."),
    ("سارة علي",    4, "جيد جداً والسعر مناسب. التوصيل كان سريع. أنصح به بشدة."),
    ("محمود حسن",   5, "المنتج أصلي 100% وجودته عالية جداً. هشتري منكم تاني."),
    ("نورا خالد",   4, "الجودة ممتازة والتغليف كان رائع. هشتري تاني من نفس المتجر."),
    ("عمر إبراهيم", 5, "أفضل منتج في الفئة دي. يستاهل كل قرش. التوصيل في 3 أيام."),
    ("ريم أحمد",    3, "المنتج كويس بس التوصيل اتأخر شوية. الجودة مناسبة للسعر."),
    ("كريم سامي",   5, "اشتريته وأنا سعيد جداً. بيشتغل بكفاءة عالية ويستاهل السعر."),
    ("منى حسين",    4, "منتج جيد جداً. التغليف محترم والتوصيل كان في الوقت المحدد."),
]


def pexels_img(query, used_ids=None):
    """جلب صورة من Pexels مع تجنب الصور المكررة"""
    if used_ids is None:
        used_ids = set()
    try:
        for page in [1, 2]:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": query, "per_page": 10, "size": "large", "page": page},
                timeout=20,
            )
            if r.status_code != 200:
                continue
            photos = r.json().get("photos", [])
            random.shuffle(photos)
            for p in photos:
                if p["id"] in used_ids:
                    continue
                ir = requests.get(p["src"]["large"], timeout=25)
                if ir.status_code == 200 and len(ir.content) > 15000:
                    used_ids.add(p["id"])
                    return ContentFile(ir.content, name=uuid.uuid4().hex + ".jpg"), used_ids
    except Exception as e:
        print("  [Pexels ERR] " + str(e))
    return None, used_ids


def placeholder(label):
    """صورة بديلة لو Pexels ما ردش"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        colors = [(30, 30, 60), (20, 50, 80), (40, 20, 60), (10, 60, 50), (60, 30, 20)]
        clr = random.choice(colors)
        img = Image.new("RGB", (800, 800), clr)
        d = ImageDraw.Draw(img)
        d.rectangle([15, 15, 785, 785], outline=(100, 180, 255), width=3)
        f = ImageFont.load_default()
        t = label[:25]
        bb = d.textbbox((0, 0), t, font=f)
        d.text((400 - (bb[2] - bb[0]) // 2, 400 - (bb[3] - bb[1]) // 2), t, fill="white", font=f)
        buf = BytesIO()
        img.save(buf, "JPEG", quality=90)
        buf.seek(0)
        return ContentFile(buf.getvalue(), name=uuid.uuid4().hex + ".jpg")
    except Exception:
        return ContentFile(b"\xff\xd8\xff\xe0" + b"\x00" * 100, name=uuid.uuid4().hex + ".jpg")


def get_img(name, query, used_ids=None):
    img, used_ids = pexels_img(query, used_ids)
    if img:
        print("  [IMG OK] " + name)
        return img, used_ids
    print("  [PLACEHOLDER] " + name)
    return placeholder(name), used_ids


def make_slug(name):
    base = slugify(name) or uuid.uuid4().hex[:8]
    s, n = base, 1
    while Product.objects.filter(slug=s).exists():
        s = base + "-" + str(n)
        n += 1
    return s


class Command(BaseCommand):
    help = "Seed 30 computer accessories with Pexels images"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=== بدء رفع المنتجات ==="))

        # حفظ المنتجات Hot Sale
        hot = list(Product.objects.filter(is_hot_sale=True).values_list("id", flat=True))
        self.stdout.write(f"Hot Sale محفوظة: {len(hot)}")

        # مسح القديم
        Product.objects.exclude(is_hot_sale=True).delete()
        Category.objects.all().delete()
        Company.objects.all().delete()
        self.stdout.write("تم مسح البيانات القديمة.")

        # إنشاء الفئات
        cats = {}
        for name in CATS:
            cats[name] = Category.objects.create(category=name)
        self.stdout.write(f"تم إنشاء {len(cats)} فئة.")

        # إنشاء الشركات (بدون تكرار)
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
        self.stdout.write(f"تم إنشاء {len(cos)} شركة.")

        # إنشاء المنتجات
        used_pexels_ids = set()
        success_count = 0

        for i, p in enumerate(PRODUCTS, 1):
            cat = cats.get(p["cat"])
            co = cos.get(p["co"])
            if not cat or not co:
                self.stdout.write(self.style.WARNING(f"SKIP: {p['name']}"))
                continue

            self.stdout.write(f"\n[{i}/{len(PRODUCTS)}] {p['name']}")

            slug = make_slug(p["name"])

            # الصورة الرئيسية
            main_img, used_pexels_ids = get_img(p["name"], p["q"], used_pexels_ids)

            pr = Product(
                category=cat,
                company=co,
                product_name=p["name"],
                product_description=p["desc"],
                orignal_price=p["price"],
                discount_percentage=p["disc"],
                is_stock=True,
                is_active=True,
                is_hot_sale=False,
                sale_end_time=None,
                has_gift_wrap=random.random() < 0.2,
                slug=slug,
            )
            pr.save()
            pr.product_image.save(slug + ".jpg", main_img, save=True)

            # صور إضافية (3 صور)
            extra_queries = [
                p["q"] + " closeup",
                p["q"] + " product detail",
                p["q"] + " white background",
            ]
            for eq in extra_queries:
                fi, used_pexels_ids = get_img(p["name"] + " extra", eq, used_pexels_ids)
                fimg_obj = FeatureProductImage(product=pr)
                fimg_obj.image.save(uuid.uuid4().hex + ".jpg", fi, save=True)

            # المميزات
            for feat in p.get("features", []):
                ProductDescription.objects.create(product=pr, feature=feat)

            # تقييم عشوائي
            reviewer = random.choice(REVIEWERS)
            Review.objects.create(
                product=pr,
                name=reviewer[0],
                rating=reviewer[1],
                review=reviewer[2],
            )

            success_count += 1
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {p['name']} | {p['price']} EGP | خصم {p['disc']}%"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"\n=== تم! {success_count} منتج من {len(PRODUCTS)} ==="
        ))