

## 🇮🇷 فارسی

**کنترل صدای ویندوز با حرکت دست (Hand Gesture Volume Control)**

این پروژه یک ابزار کنترل صدای سیستم‌عامل ویندوز با استفاده از حرکات دست و تشخیص تصویر زنده از وب‌کم است. با استفاده از کتابخانه‌ی MediaPipe، مختصات نقاط کلیدی دست (لندمارک‌ها) از تصویر دوربین استخراج می‌شود و فاصله‌ی بین نوک انگشت شست و انگشت اشاره اندازه‌گیری می‌شود. این فاصله با استفاده از کتابخانه‌ی OpenCV به صورت زنده روی تصویر نمایش داده می‌شود و سپس با کمک کتابخانه‌ی pycaw (که به رابط‌های Core Audio ویندوز متصل می‌شود) به میزان صدای سیستم تبدیل و اعمال می‌گردد. هرچه فاصله‌ی دو انگشت بیشتر باشد، صدا بلندتر و هرچه نزدیک‌تر باشند، صدا کم‌تر می‌شود.

در طول توسعه‌ی این پروژه چند مشکل فنی رفع شد: ناسازگاری تابع `Activate` در نسخه‌های جدید pycaw (که با استفاده از پراپرتی `EndpointVolume` حل شد)، و خطای `COMError` ناشی از استفاده‌ی بازه‌ی دسی‌بل ثابت به‌جای بازه‌ی واقعی سیستم (که با فراخوانی `GetVolumeRange()` و تبدیل صریح مقادیر به نوع float پایتون برطرف شد).

علاوه بر نسخه‌ی ساده‌ی خط‌فرمانی، یک نسخه‌ی گرافیکی کامل با استفاده از کتابخانه‌ی CustomTkinter نیز ساخته شد که شامل موارد زیر است: پیش‌نمایش زنده‌ی تصویر دوربین در پنجره، دکمه‌ی شروع و توقف دوربین، امکان انتخاب شماره‌ی دوربین، نوار و درصد نمایش زنده‌ی صدا، اسلایدرهای تنظیم بازه‌ی فاصله‌ی تشخیص (کالیبراسیون دستی)، قابلیت هموارسازی (Smoothing) برای جلوگیری از پرش ناگهانی صدا، و ویژگی «قفل با مشت» که با بستن دست از تغییر ناخواسته‌ی صدا هنگام حرکات غیرارادی جلوگیری می‌کند. همچنین شمارنده‌ی FPS برای پایش عملکرد بلادرنگ به رابط گرافیکی اضافه شده است.

**تکنولوژی‌های استفاده‌شده:** Python, OpenCV, MediaPipe, pycaw, comtypes, NumPy, CustomTkinter, Pillow

---

## 🔤 فینگلیش (Finglish)

**Hand Gesture Volume Control**

In pooroje ye abzare control sedaye system e Windows hast ke ba estefade az harekate dast va tashkhise tasvire zende az webcam kar mikone. Ba estefade az ketabkhone ye MediaPipe, mokhtasate noghate kelidiye dast (landmark ha) az tasvire dorbin estekhraj mishe va fasele ye beyne noke angoshte shast va angoshte eshare andaze giri mishe. In fasele ba komake OpenCV be soorate zende roo tasvir neshoon dade mishe, va bad ba komake ketabkhone ye pycaw (ke be rabet haye Core Audio ye Windows vasl mishe) be mizane sedaye system tabdil va e'mal mishe. Har che fasele ye do angosht bishtar bashe, seda bolandtar va har che nazdiktar bashan, seda kamtar mishe.

Toole tosee ye in pooroje chand moshkele fanni raf shod: nasazegariye tabe'e `Activate` too nasakheye jadid pycaw (ke ba estefade az property `EndpointVolume` hal shod), va khataye `COMError` be dalile estefade az baze ye decibel sabet be jaye baze ye vagheiye system (ke ba faraKhaniye `GetVolumeRange()` va tabdile sarih e meghdarha be noe float e python bartaraf shod).

Elave bar noskheye sadeye khat farmani, ye noskheye graphici kamel ham ba estefade az ketabkhoneye CustomTkinter sakhte shod ke shamele in mavared hast: pishnemayeshe zendeye tasvire dorbin too panjere, dokmeye shoro' va tavaghofe dorbin, emkane entekhabe shomareye dorbin, navar va darsade neshane zendeye seda, sliderhaye tanzime bazeye fasele ye tashkhis (calibration e dasti), ghabeliyate hamvarsazi (smoothing) baraye jelogiri az paresh e nagahaniye seda, va vizhegiye "ghofl ba moshte" ke ba baste shodane dast az taghyire nakhastehyeye seda hengame harekat haye gheyre eradi jelogiri mikone. Hamchenin shomarande ye FPS baraye payeshe amalkarde belafasel be rabete graphici ezafe shode.

**Technology haye estefade shode:** Python, OpenCV, MediaPipe, pycaw, comtypes, NumPy, CustomTkinter, Pillow

---

## 🇬🇧 English

**Hand Gesture Volume Control**

This project is a Windows system volume controller that uses real-time hand gesture recognition from a webcam feed. Using the MediaPipe library, hand landmark coordinates are extracted from the camera image, and the distance between the tip of the thumb and the index finger is measured. This distance is visualized live on-screen using OpenCV, then mapped and applied to the system's master volume via the pycaw library, which interfaces with Windows Core Audio APIs. The farther apart the two fingers are, the louder the volume; the closer together, the quieter.

During development, several technical issues were resolved: an `Activate` method incompatibility in newer versions of pycaw (fixed by using the `EndpointVolume` property instead), and a `COMError` caused by using a hardcoded decibel range instead of the system's actual range (fixed by calling `GetVolumeRange()` and explicitly casting values to native Python floats).

In addition to the simple command-line version, a full graphical version was built using CustomTkinter, featuring: a live camera preview window, start/stop camera controls, camera index selection, a live volume bar and percentage display, sliders for calibrating the detection distance range, a smoothing feature to prevent sudden volume jumps, and a "fist-lock" feature that prevents accidental volume changes by locking the volume when the hand is closed into a fist. An FPS counter was also added to the GUI for real-time performance monitoring.

**Tech stack:** Python, OpenCV, MediaPipe, pycaw, comtypes, NumPy, CustomTkinter, Pillow
