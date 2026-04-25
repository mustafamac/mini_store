import random
import uuid
import requests
from io import BytesIO
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from stor.models import Category, Company, Product, FeatureProductImage, ProductDescription, Review

PEXELS_KEY = "VGl8IQJ59qhTPpEuqvq0TeNMX8cQzT9kTmW8Hpc4jfvzLII9MMlYCwP3"

CATS = [
    "ماوس وكيبورد", "سماعات وهيدسيت", "شاشات", "كاميرات ويب",
    "هاردات وفلاشات", "حوامل وكابلات", "كروت شبكة وراوتر", "مراوح وتبريد",
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
    {"name": "Logitech MX Master 3S ماوس لاسلكي", "cat": "ماوس وكيبورد", "co": "Logitech", "q": "logitech wireless mouse desk", "price": 1850, "disc": 10, "hot": False,
     "desc": "ماوس لاسلكي احترافي بدقة 8000 DPI وعجلة تمرير مغناطيسية. مثالي للتصميم والبرمجة. يعمل 70 يوم على شحنة واحدة.",
     "features": [("دقة 8000 DPI قابلة للتعديل", "تحكم كامل في حساسية المؤشر بين 200 و 8000 DPI لتناسب كل المهام."), ("اتصال Bluetooth و USB Receiver", "تبديل تلقائي بين 3 أجهزة مختلفة بضغطة زر واحدة."), ("عجلة تمرير مغناطيسية صامتة", "تمرير سلس وصامت يناسب بيئات العمل الهادئة."), ("بطارية تدوم 70 يوماً", "شحن سريع لمدة دقيقتين يكفي 3 ساعات عمل متواصل."), ("متوافق مع Windows و Mac", "يعمل بكفاءة على جميع أنظمة التشغيل الحديثة.")]},

    {"name": "Razer DeathAdder V3 ماوس جيمنج", "cat": "ماوس وكيبورد", "co": "Razer", "q": "razer gaming mouse rgb", "price": 1650, "disc": 15, "hot": True,
     "desc": "ماوس جيمنج خفيف الوزن 59 جرام بدقة 30,000 DPI وسرعة استجابة 0.2ms. الخيار الأول للاعبين المحترفين.",
     "features": [("دقة 30,000 DPI", "سينسور Focus Pro الأدق في فئته لتتبع حركة لا تشوبها شائبة."), ("وزن 59 جرام فقط", "تصميم مريح للإمساك طويل الأمد دون إجهاد اليد."), ("زر ضغط بضمان 90 مليون نقرة", "مفاتيح Razer Optical تتحمل الاستخدام المكثف لسنوات."), ("إضاءة Razer Chroma RGB", "16.8 مليون لون قابل للتخصيص عبر تطبيق Synapse."), ("كابل Speedflex مرن", "كابل مرن لا يعيق الحركة ويحاكي تجربة الماوس اللاسلكي.")]},

    {"name": "Logitech G Pro X Mechanical Keyboard", "cat": "ماوس وكيبورد", "co": "Logitech", "q": "mechanical gaming keyboard rgb", "price": 2800, "disc": 10, "hot": False,
     "desc": "كيبورد ميكانيكي احترافي TKL بمفاتيح GX Blue قابلة للتبديل. يستخدمه محترفو البطولات العالمية.",
     "features": [("مفاتيح GX قابلة للتبديل", "غيّر نوع المفاتيح بدون لحام لتحصل على تجربة الكتابة المثالية."), ("تصميم TKL مدمج", "بدون لوحة أرقام جانبية لمساحة ماوس أوسع على المكتب."), ("إضاءة RGB لكل مفتاح", "تحكم في إضاءة كل مفتاح على حدة عبر تطبيق G HUB."), ("كابل مفصول", "كابل USB-C مفصول لسهولة الحمل والاستبدال."), ("ضمان سنتين", "ضمان رسمي من Logitech مع دعم فني متكامل.")]},

    {"name": "Razer BlackWidow V4 Keyboard ميكانيكي", "cat": "ماوس وكيبورد", "co": "Razer", "q": "razer keyboard mechanical gaming", "price": 3200, "disc": 0, "hot": False,
     "desc": "كيبورد ميكانيكي بمفاتيح Razer Green الشهيرة وإضاءة Chroma RGB بـ 16.8 مليون لون. مع عجلة تحكم بالصوت.",
     "features": [("مفاتيح Razer Green الميكانيكية", "نقرة مميزة وصوت واضح يعطيك تغذية راجعة لكل ضغطة."), ("إضاءة Chroma RGB", "تأثيرات إضاءة متزامنة مع الألعاب لتجربة غمر استثنائية."), ("عجلة تحكم بالصوت", "تحكم سريع في مستوى الصوت دون مغادرة اللعبة."), ("مسند راحة مغناطيسي", "مسند يد مريح قابل للفصل يخفف الإجهاد عند الكتابة الطويلة."), ("USB Pass-through", "منفذ USB إضافي على الكيبورد لتوصيل الماوس أو الفلاشة.")]},

    {"name": "Logitech G840 XL Gaming Mouse Pad", "cat": "ماوس وكيبورد", "co": "Logitech", "q": "large gaming mouse pad desk mat", "price": 550, "disc": 20, "hot": False,
     "desc": "ماوس باد XL يغطي المكتب بالكامل 90×40 سم. سطح ناعم لأقصى دقة وقاعدة مطاط مانعة للانزلاق.",
     "features": [("مقاس XL 90x40 سم", "يغطي كامل المكتب ويوفر مساحة للكيبورد والماوس معاً."), ("سطح قماشي ناعم", "سطح محسّن للسينسور يعطي دقة تتبع قصوى بأي حساسية."), ("قاعدة مطاط مانعة للانزلاق", "تثبيت كامل على السطح حتى أثناء الحركات السريعة."), ("حواف مخيطة لمنع التآكل", "حواف مدعمة تمنع التفتت وتطيل عمر الماوس باد."), ("مناسب لجميع أنواع الماوس", "متوافق مع جميع أنواع السينسور الضوئي والليزري.")]},

    # سماعات وهيدسيت
    {"name": "HyperX Cloud II Wireless هيدسيت جيمنج", "cat": "سماعات وهيدسيت", "co": "HyperX", "q": "gaming headset wireless over ear", "price": 2200, "disc": 15, "hot": True,
     "desc": "هيدسيت جيمنج لاسلكي بصوت 7.1 Surround وبطارية 30 ساعة. ميكروفون معزول للضوضاء بجودة عالية.",
     "features": [("صوت 7.1 Virtual Surround", "تجربة صوت محيطي تساعدك على تحديد اتجاه الأعداء بدقة."), ("بطارية 30 ساعة", "استخدام لاسلكي لجلسات ألعاب طويلة دون انقطاع."), ("ميكروفون معزول للضوضاء", "صوت واضح ونقي خلال المحادثات الصوتية والبث المباشر."), ("وسادات ذاكرة مريحة", "وسادات إسفنجية تتشكل حسب شكل أذنك لراحة قصوى."), ("تردد 10Hz - 21kHz", "نطاق صوتي واسع يلتقط كل التفاصيل الصوتية الدقيقة.")]},

    {"name": "SteelSeries Arctis Nova Pro هيدسيت", "cat": "سماعات وهيدسيت", "co": "SteelSeries", "q": "professional gaming headset noise cancelling", "price": 4500, "disc": 10, "hot": False,
     "desc": "هيدسيت احترافي بنظام ANC وميكروفون ClearCast قابل للسحب. نظام شحن مزدوج للاستخدام المتواصل.",
     "features": [("Active Noise Cancellation", "إلغاء فعّال لضوضاء المحيط للتركيز الكامل في اللعبة."), ("ميكروفون ClearCast", "ميكروفون ثنائي الاتجاه يعزل صوتك بوضوح عن الضوضاء."), ("نظام بطارية مزدوج", "بطاريتان قابلتان للتبادل لاستخدام لا ينتهي أبداً."), ("DAC خارجي عالي الجودة", "محول صوت رقمي خارجي لجودة صوت استوديو حقيقية."), ("متوافق مع PC و PlayStation", "يعمل على جميع المنصات بدون إعداد معقد.")]},

    {"name": "HyperX Cloud Stinger 2 سماعة جيمنج", "cat": "سماعات وهيدسيت", "co": "HyperX", "q": "hyperx headset gaming pc", "price": 899, "disc": 25, "hot": False,
     "desc": "هيدسيت جيمنج بسعر مناسب وجودة صوت ممتازة. ميكروفون قابل للتعديل مع زر كتم صوت على الكأس.",
     "features": [("درايفر 40mm عالي الدقة", "درايفرات كبيرة توفر صوت باس قوي وأصوات عالية واضحة."), ("ميكروفون قابل للكسر 90 درجة", "اكسر الميكروفون لأعلى لكتم الصوت تلقائياً."), ("زر كتم صوت على الكأس", "تحكم سريع في الصوت دون الحاجة للبحث عن الكابل."), ("وزن خفيف 275 جرام", "خفيف جداً لا تشعر بثقله حتى في جلسات الألعاب الطويلة."), ("توصيل 3.5mm و USB", "يعمل مع الكمبيوتر والموبايل والبلاي ستيشن بكابل واحد.")]},

    {"name": "SteelSeries Arctis 1 Wireless سماعة", "cat": "سماعات وهيدسيت", "co": "SteelSeries", "q": "steelseries headset gaming wireless", "price": 1800, "disc": 5, "hot": False,
     "desc": "سماعة لاسلكية خفيفة بصوت نقي وميكروفون قابل للفصل. تدعم Nintendo Switch و PC و Android.",
     "features": [("لاسلكي USB-C", "اتصال لاسلكي عبر USB-C يعمل مع الموبايل والسويتش والكمبيوتر."), ("ميكروفون قابل للفصل", "افصل الميكروفون واستخدم السماعة للموسيقى في أي مكان."), ("متوافق مع Switch و PC", "الهيدسيت الوحيد اللاسلكي يعمل مع Nintendo Switch."), ("وزن خفيف جداً", "تصميم خفيف الوزن لا يثقل الرأس في الاستخدام الطويل."), ("بطارية 20 ساعة", "شحنة واحدة تكفي يوم كامل من الألعاب واللقاءات.")]},

    # شاشات
    {"name": "Samsung 27 inch IPS 165Hz شاشة جيمنج", "cat": "شاشات", "co": "Samsung", "q": "samsung gaming monitor 27 inch", "price": 4200, "disc": 10, "hot": True,
     "desc": "شاشة جيمنج 27 بوصة IPS بمعدل تحديث 165Hz واستجابة 1ms MPRT. تقنية AMD FreeSync Premium لصورة سلسة.",
     "features": [("165Hz refresh rate", "حركة سلسة تماماً بدون تمزق في الصورة أثناء الألعاب السريعة."), ("1ms MPRT response", "استجابة فائقة السرعة تلغي الضبابية في الحركات السريعة."), ("AMD FreeSync Premium", "مزامنة تلقائية مع كرت الشاشة لصورة خالية من التقطع."), ("HDR10 support", "ألوان حيوية وتباين عالي لتجربة بصرية غنية وواقعية."), ("Eye Saver Mode", "فلتر ضوء أزرق يحمي عينيك في جلسات الاستخدام الطويلة.")]},

    {"name": "LG 24 inch IPS FHD 75Hz شاشة مكتب", "cat": "شاشات", "co": "LG", "q": "lg office monitor 24 inch desktop", "price": 2800, "disc": 5, "hot": False,
     "desc": "شاشة مكتبية 24 بوصة IPS بألوان حقيقية 99% sRGB. مثالية للعمل والتصميم بميزة Reader Mode.",
     "features": [("لوحة IPS 99% sRGB", "ألوان دقيقة وحقيقية مثالية للتصميم الجرافيكي وتحرير الصور."), ("Reader Mode للعين", "يحول الشاشة لوضع ورق لتقليل إجهاد العين عند القراءة."), ("OnScreen Control", "تحكم في إعدادات الشاشة مباشرة من الكمبيوتر بدون أزرار."), ("HDMI و DisplayPort", "منافذ متعددة للاتصال بأي جهاز لابتوب أو كمبيوتر."), ("قابلة للتعديل في الارتفاع", "اضبط ارتفاع الشاشة لوضع مريح يناسب طول جلستك.")]},

    {"name": "Samsung 32 inch QHD 144Hz شاشة كيرفد", "cat": "شاشات", "co": "Samsung", "q": "samsung curved monitor 32 inch gaming", "price": 6500, "disc": 8, "hot": False,
     "desc": "شاشة منحنية 32 بوصة QHD 2560x1440 بمعدل 144Hz. تجربة غمر كاملة مع تقنية Samsung VA Panel.",
     "features": [("دقة QHD 2560x1440", "صورة أوضح وأكثر تفصيلاً من Full HD بنسبة 78%."), ("144Hz refresh rate", "ألعاب سلسة وسريعة مع معدل تحديث يفوق الشاشات العادية."), ("تصميم منحني 1000R", "انحناء يحاكي مجال رؤية العين البشرية لغمر حقيقي."), ("HDR10", "تباين ديناميكي يكشف تفاصيل الظل والضوء في نفس الوقت."), ("AMD FreeSync", "تزامن مع كروت الشاشة AMD لصورة خالية من التقطع.")]},

    {"name": "LG UltraWide 29 inch شاشة عريضة", "cat": "شاشات", "co": "LG", "q": "lg ultrawide monitor 29 inch", "price": 3900, "disc": 12, "hot": False,
     "desc": "شاشة عريضة 29 بوصة 21:9 IPS بدقة 2560x1080. مثالية للإنتاجية والألعاب مع HDR10.",
     "features": [("نسبة عرض 21:9", "مساحة عمل أوسع تعوض عن شاشتين جنباً إلى جنب."), ("دقة 2560x1080", "عرض تطبيقين بجودة كاملة في نفس الوقت بدون ضغط."), ("IPS بألوان دقيقة", "ألوان ثابتة من كل زوايا النظر مناسبة للتصميم والمونتاج."), ("HDR10", "ألوان حيوية وتباين عالٍ في المحتوى الداعم لتقنية HDR."), ("USB-C و HDMI", "توصيل بالابتوب بكابل واحد يشحن ويعرض الصورة معاً.")]},

    # كاميرات ويب
    {"name": "Logitech C920 HD Pro Webcam 1080p", "cat": "كاميرات ويب", "co": "Logitech", "q": "webcam 1080p hd video call", "price": 1600, "disc": 10, "hot": False,
     "desc": "كاميرا ويب احترافية 1080p 30fps مع ميكروفون ستيريو مدمج. مثالية للاجتماعات والستريم.",
     "features": [("دقة 1080p Full HD", "صورة واضحة وحادة في جميع ظروف الإضاءة."), ("ميكروفون ستيريو مدمج", "صوت ثلاثي الأبعاد يلتقط الصوت بوضوح من مسافة بعيدة."), ("تركيز تلقائي", "تركيز ذكي يتتبع وجهك ويحافظ على وضوح الصورة دائماً."), ("ضغط H.264", "ضغط ذكي يوفر جودة عالية مع استهلاك أقل لعرض الإنترنت."), ("متوافق مع Zoom و Teams", "يعمل فوراً بدون تثبيت درايفرات مع جميع تطبيقات الاجتماعات.")]},

    {"name": "Logitech StreamCam USB-C كاميرا ستريم", "cat": "كاميرات ويب", "co": "Logitech", "q": "streaming camera usb-c content creator", "price": 2400, "disc": 15, "hot": False,
     "desc": "كاميرا ستريم احترافية 1080p 60fps بمنفذ USB-C. AI Face Tracking لتتبع وجهك تلقائياً.",
     "features": [("1080p 60fps", "بث مباشر سلس بدقة كاملة ومعدل إطارات مضاعف."), ("AI Face Tracking", "الكاميرا تتبع وجهك تلقائياً وتبقيك دائماً في المنتصف."), ("منفذ USB-C", "توصيل سريع بأحدث الابتوبات بكابل USB-C واحد."), ("تركيز ذكي تلقائي", "خوارزمية ذكية تضمن وضوح وجهك في كل الأوضاع."), ("تثبيت أفقي وعمودي", "ضعها أفقياً للبث أو عمودياً لمحتوى السوشيال ميديا.")]},

    {"name": "Logitech Brio 4K Ultra HD Webcam", "cat": "كاميرات ويب", "co": "Logitech", "q": "4k webcam professional video", "price": 3800, "disc": 0, "hot": False,
     "desc": "كاميرا ويب 4K مع HDR وتقنية RightLight 3 للإضاءة التلقائية. الأفضل لمؤتمرات الفيديو الاحترافية.",
     "features": [("دقة 4K Ultra HD", "أوضح كاميرا ويب في السوق لاجتماعات تبدو كأنها وجهاً لوجه."), ("HDR و RightLight 3", "صورة مثالية حتى في الغرف ضعيفة الإضاءة أو أمام النوافذ."), ("زاوية رؤية 90 درجة", "تلتقط مساحة واسعة تسع أكثر من شخص في الإطار."), ("Windows Hello", "تسجيل دخول فوري لويندوز بالتعرف على الوجه بأمان تام."), ("تكبير رقمي 5x", "اقترب من أي تفصيلة دون فقدان جودة الصورة.")]},

    # هاردات وفلاشات
    {"name": "WD Blue SSD 1TB SATA هارد داخلي", "cat": "هاردات وفلاشات", "co": "Western Digital", "q": "ssd internal storage hard drive", "price": 1900, "disc": 10, "hot": False,
     "desc": "هارد SSD داخلي 1TB بسرعة قراءة 560 MB/s. يرفع أداء الكمبيوتر بشكل ملحوظ مع ضمان 5 سنوات.",
     "features": [("سرعة قراءة 560 MB/s", "تشغيل ويندوز في 10 ثواني وفتح التطبيقات فورياً."), ("سرعة كتابة 530 MB/s", "نقل الملفات الكبيرة بسرعة مذهلة تختصر وقت الانتظار."), ("ضمان 5 سنوات", "ضمان طويل الأمد يعكس ثقة WD في جودة منتجها."), ("واجهة SATA III", "متوافق مع جميع الأجهزة الحديثة والقديمة بدون تعديلات."), ("مناسب للابتوب والديسكتوب", "حجم 2.5 بوصة يناسب الابتوب والديسكتوب بمحول بسيط.")]},

    {"name": "Kingston 32GB USB 3.2 فلاشة سريعة", "cat": "هاردات وفلاشات", "co": "Kingston", "q": "usb flash drive storage", "price": 320, "disc": 0, "hot": False,
     "desc": "فلاشة USB 3.2 بسرعة نقل 200 MB/s بتصميم معدني متين ومدمج. ضمان مدى الحياة من كينجستون.",
     "features": [("USB 3.2 Gen 1", "أسرع 10 مرات من USB 2.0 لنقل الملفات في ثوانٍ."), ("سرعة قراءة 200 MB/s", "نقل فيلم كامل في أقل من دقيقتين بسرعة مذهلة."), ("تصميم معدني مدمج", "هيكل معدني صلب يتحمل السقوط والضغط بدون غطاء يضيع."), ("ضمان مدى الحياة", "Kingston تضمن منتجها للأبد وتستبدله مجاناً عند الحاجة."), ("متوافق مع Windows و Mac", "يعمل فوراً بدون تثبيت أي برامج على أي نظام تشغيل.")]},

    {"name": "WD My Passport 2TB هارد خارجي", "cat": "هاردات وفلاشات", "co": "Western Digital", "q": "external portable hard drive", "price": 2100, "disc": 5, "hot": False,
     "desc": "هارد خارجي محمول 2TB بتصميم أنيق وحماية بكلمة سر وتشفير AES 256-bit. USB 3.0 للنقل السريع.",
     "features": [("سعة 2TB", "سعة ضخمة تسع 500,000 صورة أو 200 ساعة فيديو 4K."), ("تشفير AES 256-bit", "حماية بياناتك بكلمة سر وتشفير عسكري لا يمكن كسره."), ("USB 3.0", "نقل بيانات بسرعة تصل 130 MB/s عبر كابل USB-C مرفق."), ("ضمان 3 سنوات", "ضمان WD الرسمي مع خدمة عملاء متاحة على مدار الساعة."), ("متوافق مع PC و Mac", "يعمل مع ويندوز وماك بدون تهيئة أو برامج إضافية.")]},

    {"name": "Kingston NV2 500GB NVMe SSD", "cat": "هاردات وفلاشات", "co": "Kingston", "q": "nvme m2 ssd fast storage", "price": 1200, "disc": 0, "hot": True,
     "desc": "هارد NVMe M.2 بسرعة قراءة 3500 MB/s. أسرع بـ 6 مرات من SSD العادي. مثالي للألعاب والإنتاج.",
     "features": [("سرعة قراءة 3500 MB/s", "تحميل الألعاب الكبيرة في ثوانٍ معدودة بدون انتظار."), ("واجهة PCIe 4.0 NVMe", "أحدث واجهة تخزين تستفيد من أقصى سرعة اللوحة الأم."), ("تصميم M.2 2280", "يركب مباشرة في اللوحة الأم بدون كابلات أو مساحة إضافية."), ("ضمان 3 سنوات", "ضمان Kingston الرسمي مع مؤشر TBW لضمان العمر الافتراضي."), ("استهلاك طاقة منخفض", "حرارة أقل وعمر بطارية أطول للابتوب مقارنة بالهاردات العادية.")]},

    # حوامل وكابلات
    {"name": "Anker 7-in-1 USB-C Hub هاب متعدد", "cat": "حوامل وكابلات", "co": "Anker", "q": "usb-c hub multiport adapter laptop", "price": 850, "disc": 15, "hot": False,
     "desc": "هاب USB-C 7 في 1 مع HDMI 4K و USB 3.0 و SD Card و شحن 100W. مثالي للابتوب.",
     "features": [("HDMI 4K@30Hz", "وصّل شاشة خارجية بدقة 4K كاملة لعرض احترافي."), ("3 منافذ USB 3.0", "وصّل ماوس وكيبورد وفلاشة في نفس الوقت بسرعة عالية."), ("SD و MicroSD Card", "اقرأ كروت الكاميرا مباشرة بدون محول إضافي."), ("شحن 100W PD", "اشحن ابتوبك بكامل طاقته عبر نفس منفذ الهاب بدون بطء."), ("توصيل فوري بدون درايفر", "وصّله واستخدمه فوراً على ويندوز وماك بدون تثبيت أي برامج.")]},

    {"name": "Anker كابل USB-C شحن سريع 2 متر", "cat": "حوامل وكابلات", "co": "Anker", "q": "usb-c charging cable braided", "price": 180, "disc": 0, "hot": False,
     "desc": "كابل USB-C بطول 2 متر يدعم شحن 60W وسرعة نقل بيانات 480 Mbps. مغلف بنايلون متين ضد الالتواء.",
     "features": [("دعم شحن 60W", "شحن سريع للموبايل والابتوب الصغير بأقصى سرعة مدعومة."), ("نقل بيانات 480 Mbps", "نقل ملفاتك بسرعة USB 2.0 الكاملة دون أي تدهور."), ("طول 2 متر", "طول مريح يعطيك حرية الحركة أثناء الشحن دون قيود."), ("غلاف نايلون متين", "مقاوم للالتواء والكسر أكثر 10 مرات من الكابلات العادية."), ("ضمان 18 شهراً", "ضمان Anker الشهير مع استبدال مجاني بدون أسئلة.")]},

    {"name": "Anker حامل لابتوب قابل للتعديل", "cat": "حوامل وكابلات", "co": "Anker", "q": "laptop stand adjustable aluminum desk", "price": 450, "disc": 10, "hot": False,
     "desc": "حامل لابتوب ألومنيوم قابل للتعديل في 6 زوايا. يحسن التهوية ويريح الرقبة أثناء العمل.",
     "features": [("6 زوايا قابلة للتعديل", "اختر الزاوية المثالية التي تريح رقبتك وعينيك."), ("هيكل ألومنيوم متين", "يتحمل ابتوب حتى 5 كيلو مع ثبات تام لا يهتز."), ("قواعد مطاطية مانعة للانزلاق", "ثابت على المكتب ولا يخدش الابتوب من الأسفل."), ("قابل للطي للحمل", "يطوى بشكل مسطح ويدخل في حقيبة الابتوب بسهولة."), ("يدعم لابتوب حتى 17 بوصة", "مناسب لجميع أحجام الابتوب من 10 إلى 17 بوصة.")]},

    # كروت شبكة وراوتر
    {"name": "TP-Link Archer AX21 راوتر WiFi 6", "cat": "كروت شبكة وراوتر", "co": "TP-Link", "q": "wifi router wireless network home", "price": 1650, "disc": 10, "hot": False,
     "desc": "راوتر WiFi 6 بسرعة 1800 Mbps مع 4 هوائيات خارجية. يدعم 80 جهاز في آن واحد بتقنية OFDMA.",
     "features": [("WiFi 6 AX1800", "أسرع جيل من الواي فاي يقلل التأخير ويزيد السرعة بشكل ملحوظ."), ("دعم 80 جهاز متصل", "موبايلات ولابتوبات وشاشات ذكية تتصل في نفس الوقت بدون بطء."), ("تقنية OFDMA", "توزيع ذكي لعرض النطاق يضمن سرعة عادلة لجميع الأجهزة."), ("4 هوائيات خارجية", "تغطية واسعة تصل لكل زوايا الشقة أو المنزل."), ("إعداد سهل عبر تطبيق", "إعداد الراوتر في دقيقتين عبر تطبيق Tether بدون خبرة تقنية.")]},

    {"name": "TP-Link USB WiFi Adapter كرت شبكة", "cat": "كروت شبكة وراوتر", "co": "TP-Link", "q": "usb wifi adapter network dongle", "price": 280, "disc": 0, "hot": False,
     "desc": "كرت شبكة WiFi USB بسرعة 300 Mbps. توصيل ولعب بدون إعداد. يعمل على Windows و Linux.",
     "features": [("سرعة 300 Mbps", "سرعة كافية للبث والألعاب الأونلاين بدون تقطع."), ("USB 2.0", "يعمل مع أي USB في الكمبيوتر بدون منفذ خاص."), ("Plug and Play", "ويندوز يتعرف عليه تلقائياً بدون تحميل درايفرات يدوياً."), ("هوائي قابل للطي", "هوائي يطوى للحمل ويفرد لتحسين الإشارة عند الاستخدام."), ("متوافق مع Windows 11/10/7", "يعمل مع جميع إصدارات ويندوز والتوزيعات الشائعة من لينكس.")]},

    {"name": "TP-Link TL-SG108 سويتش شبكة 8 منافذ", "cat": "كروت شبكة وراوتر", "co": "TP-Link", "q": "network switch ethernet 8 port", "price": 420, "disc": 5, "hot": False,
     "desc": "سويتش شبكة 8 منافذ Gigabit بسرعة 1000 Mbps لكل منفذ. مثالي لربط أجهزة المنزل والمكتب.",
     "features": [("8 منافذ Gigabit 1000Mbps", "سرعة قيقابت كاملة في كل منفذ للنقل السريع بين الأجهزة."), ("Plug and Play", "وصّله بالكهرباء وابدأ الاستخدام فوراً بدون أي إعداد."), ("هيكل معدني متين", "مصنوع من المعدن ليتحمل الاستخدام المستمر في المكاتب."), ("توفير الطاقة التلقائي", "يقلل استهلاك الكهرباء تلقائياً عند عدم استخدام منفذ."), ("بدون إعداد", "لا يحتاج ويب انترفيس أو برامج أو تهيئة من أي نوع.")]},

    # مراوح وتبريد
    {"name": "Cooler Master Hyper 212 مروحة معالج", "cat": "مراوح وتبريد", "co": "Cooler Master", "q": "cpu cooler fan tower heatsink", "price": 950, "disc": 15, "hot": False,
     "desc": "مروحة معالج Tower بـ 4 هيت بايب مباشرة وأداء تبريد ممتاز للمعالجات حتى 150W. تثبيت سهل.",
     "features": [("4 Heat Pipes مباشرة", "أنابيب حرارية تلمس المعالج مباشرة لنقل الحرارة بأقصى كفاءة."), ("قدرة تبريد 150W TDP", "يبرد معالجات Core i9 و Ryzen 9 بكفاءة عالية."), ("مروحة PWM 120mm", "سرعة المروحة تتعدل تلقائياً حسب درجة الحرارة للهدوء الأمثل."), ("متوافق Intel و AMD", "يركب على جميع مقابس Intel LGA1700 و AMD AM5 الحديثة."), ("تركيب بدون أدوات", "نظام تثبيت Push-Pin سهل لا يحتاج مفك أو أدوات خاصة.")]},

    {"name": "Cooler Master MasterBox Q300L كيس كمبيوتر", "cat": "مراوح وتبريد", "co": "Cooler Master", "q": "pc computer case gaming tower", "price": 1400, "disc": 10, "hot": False,
     "desc": "كيس كمبيوتر Micro-ATX بجانب شبكي لتدفق هواء ممتاز. يدعم 3 مراوح 120mm وراديتر 240mm.",
     "features": [("هيكل Micro-ATX", "حجم مدمج يوفر مساحة المكتب دون التضحية بالأداء."), ("جانب شبكي للتهوية", "تدفق هواء ممتاز من جميع الاتجاهات يبقي المكونات باردة."), ("يدعم 3 مراوح 120mm", "ركّب 3 مراوح للتبريد القوي مع إضاءة RGB ترضيك."), ("راديتر 240mm في الأمام", "ركّب تبريد مائي AIO 240mm في المقدمة بسهولة."), ("إدارة كابلات مرتبة", "مساحة خلفية لإخفاء الكابلات للحصول على مظهر نظيف.")]},

    {"name": "Cooler Master RGB مروحة كيس 120mm", "cat": "مراوح وتبريد", "co": "Cooler Master", "q": "rgb case fan 120mm cooling", "price": 320, "disc": 0, "hot": False,
     "desc": "مروحة كيس 120mm بإضاءة RGB قابلة للتحكم. هادئة في التشغيل مع أداء تهوية ممتاز.",
     "features": [("إضاءة RGB قابلة للتحكم", "تحكم في الألوان عبر اللوحة الأم أو كنترولر منفصل."), ("سرعة 650-1800 RPM", "نطاق سرعة واسع يوازن بين التبريد والهدوء حسب الحاجة."), ("ضوضاء منخفضة 8-27 dBA", "هادئة جداً في الأوضاع العادية لا تشتت التركيز."), ("تدفق هواء 38 CFM", "تدفق هواء كافٍ لتبريد الكيس بكفاءة عالية."), ("ضمان سنتين", "ضمان Cooler Master الرسمي مع دعم فني متاح.")]},

    {"name": "Cooler Master AIO تبريد مائي 240mm", "cat": "مراوح وتبريد", "co": "Cooler Master", "q": "aio liquid cpu cooler 240mm radiator", "price": 2200, "disc": 8, "hot": True,
     "desc": "تبريد مائي AIO بـ 240mm راديتر ومروحتين RGB. يبرد المعالجات حتى 250W بصمت تام.",
     "features": [("راديتر 240mm", "مساحة تبديد حرارة كبيرة لتبريد المعالجات الأقوى في السوق."), ("مروحتان 120mm RGB", "مروحتان متزامنتان مع إضاءة ARGB قابلة للتخصيص الكامل."), ("تبريد حتى 250W TDP", "يتعامل مع أقوى معالجات Intel و AMD دون عرق."), ("رأس تبريد نحاسي", "رأس نحاسي يلتصق بالمعالج بضغط مثالي لنقل الحرارة الأمثل."), ("متوافق Intel LGA1700 و AMD AM5", "يدعم جميع المنصات الحديثة بكيت تثبيت شامل في العلبة.")]},
]

REVIEWERS = [
    ("أحمد محمد",   5, "منتج ممتاز وصل بسرعة. الجودة أفضل من توقعاتي وشغّل من أول لحظة."),
    ("سارة علي",    4, "جيد جداً والسعر مناسب. التوصيل كان سريع. أنصح به بشدة."),
    ("محمود حسن",   5, "المنتج أصلي 100% وجودته عالية جداً. هشتري منكم تاني."),
    ("نورا خالد",   4, "الجودة ممتازة والتغليف كان رائع. هشتري تاني من نفس المتجر."),
    ("عمر إبراهيم", 5, "أفضل منتج في الفئة دي. يستاهل كل قرش. التوصيل في 3 أيام."),
    ("ريم أحمد",    3, "المنتج كويس بس التوصيل اتأخر شوية. الجودة مناسبة للسعر."),
    ("كريم سامي",   5, "اشتريته وأنا سعيد جداً. بيشتغل بكفاءة عالية ويستاهل السعر."),
    ("منى حسين",    4, "منتج جيد جداً. التغليف محترم والتوصيل كان في الوقت المحدد."),
]


def pexels_img(query, used_ids=None):
    if used_ids is None:
        used_ids = set()
    try:
        for page in [1, 2, 3]:
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
    try:
        from PIL import Image, ImageDraw, ImageFont
        clr = random.choice([(30, 30, 60), (20, 50, 80), (40, 20, 60), (10, 60, 50)])
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
        print("  [IMG OK] " + name[:30])
        return img, used_ids
    print("  [PLACEHOLDER] " + name[:30])
    return placeholder(name), used_ids


def make_slug(name):
    base = slugify(name) or uuid.uuid4().hex[:8]
    s, n = base, 1
    while Product.objects.filter(slug=s).exists():
        s = base + "-" + str(n)
        n += 1
    return s


class Command(BaseCommand):
    help = "Seed 30 products with full data, Pexels images, hot sale timers"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=== بدء رفع المنتجات ==="))

        hot_ids = list(Product.objects.filter(is_hot_sale=True).values_list("id", flat=True))
        self.stdout.write(f"Hot Sale محفوظة: {len(hot_ids)}")

        Product.objects.exclude(id__in=hot_ids).delete()
        Category.objects.all().delete()
        Company.objects.all().delete()
        self.stdout.write("تم مسح البيانات القديمة.")

        cats = {name: Category.objects.create(category=name) for name in CATS}
        self.stdout.write(f"تم إنشاء {len(cats)} فئة.")

        cos, seen = {}, set()
        for c in COS:
            key = c["name"] + "|" + c["cat"]
            if key in seen:
                continue
            seen.add(key)
            cat_obj = cats.get(c["cat"])
            if cat_obj:
                cos[c["name"]] = Company.objects.create(category=cat_obj, company=c["name"])
        self.stdout.write(f"تم إنشاء {len(cos)} شركة.")

        used_pexels_ids = set()
        success = 0

        for i, p in enumerate(PRODUCTS, 1):
            cat = cats.get(p["cat"])
            co = cos.get(p["co"])
            if not cat or not co:
                self.stdout.write(self.style.WARNING(f"SKIP: {p['name']}"))
                continue

            self.stdout.write(f"\n[{i}/{len(PRODUCTS)}] {p['name']}")
            slug = make_slug(p["name"])
            main_img, used_pexels_ids = get_img(p["name"], p["q"], used_pexels_ids)

            hot = p.get("hot", False)
            sale_end = timezone.now() + timedelta(hours=random.randint(24, 48)) if hot else None

            pr = Product(
                category=cat, company=co,
                product_name=p["name"],
                product_description=p["desc"],
                orignal_price=p["price"],
                discount_percentage=p["disc"],
                is_stock=True, is_active=True,
                is_hot_sale=hot, sale_end_time=sale_end,
                has_gift_wrap=random.random() < 0.2,
                slug=slug,
            )
            pr.save()
            pr.product_image.save(slug + ".jpg", main_img, save=True)

            # صور إضافية
            for eq in [p["q"] + " closeup", p["q"] + " detail", p["q"] + " product"]:
                fi, used_pexels_ids = get_img(p["name"] + " extra", eq, used_pexels_ids)
                fimg = FeatureProductImage(product=pr)
                fimg.image.save(uuid.uuid4().hex + ".jpg", fi, save=True)

            # مميزات مع وصف وصورة
            for feat_title, feat_desc in p.get("features", []):
                feat_img, used_pexels_ids = get_img(feat_title, p["q"], used_pexels_ids)
                pd_obj = ProductDescription(
                    product=pr,
                    feature=feat_title,
                    product_description=feat_desc,
                )
                pd_obj.save()
                pd_obj.product_image.save(uuid.uuid4().hex + ".jpg", feat_img, save=True)

            # تقييم
            rv = random.choice(REVIEWERS)
            Review.objects.create(product=pr, name=rv[0], rating=rv[1], review=rv[2])

            hot_label = " 🔥 HOT SALE" if hot else ""
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {p['name']} | {p['price']} EGP | خصم {p['disc']}%{hot_label}"
            ))
            success += 1

        self.stdout.write(self.style.SUCCESS(f"\n=== تم! {success} منتج من {len(PRODUCTS)} ==="))