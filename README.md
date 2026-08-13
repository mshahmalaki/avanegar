# AvaNegar

**Persian voice, in Persian text.**

[English](#english) · [فارسی](#فارسی)

---

## English

AvaNegar is a local-first, privacy-focused application for transcribing Persian
(Farsi) audio into accurate, readable text. It provides a polished RTL web
interface, a clean API, Persian text normalization, timestamped segments,
confidence indicators, and TXT, JSON, SRT, and VTT exports.

### Features

- Upload MP3, WAV, M4A, OGG, WebM, MP4, MPEG, and FLAC files
- Record audio directly from the browser
- Transcribe Persian speech with `faster-whisper` and voice activity detection
- Normalize Arabic/Persian character variants, spacing, and zero-width non-joiners
- Return word and segment timestamps, confidence scores, and uncertainty markers
- Export transcripts as plain text, structured JSON, SRT, or WebVTT
- Delete temporary audio files immediately after processing
- Explore the interface in demo mode without downloading a speech model

> Multi-speaker diarization is not implemented in this MVP. When speaker labels
> are enabled, the output structure includes them, but every segment is assigned
> to “Speaker 1.”

### Quick start

Python 3.11 or newer is required. Install `ffmpeg` if you want to process formats
other than WAV.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

The base installation starts in demo mode. The application clearly identifies
demo transcripts because they are sample output and are not extracted from the
uploaded audio.

### Enable real transcription

```bash
pip install -e ".[whisper]"
cp .env.example .env
uvicorn app.main:app --reload
```

On its first run, `faster-whisper` downloads the configured model. The default
model is `small`. You can change the following values in `.env` for higher
accuracy or different hardware:

```dotenv
TRANSCRIBER_MODE=whisper
WHISPER_MODEL=medium
WHISPER_DEVICE=auto
WHISPER_COMPUTE_TYPE=default
```

- `TRANSCRIBER_MODE=auto` uses Whisper when available and falls back to demo mode
  if the engine cannot be initialized.
- `TRANSCRIBER_MODE=whisper` fails at startup if the engine or model is not
  available. This is the recommended mode for production.
- `TRANSCRIBER_MODE=demo` always generates clearly labeled sample output.

### Docker

```bash
docker compose up --build
```

The application will be available on port `8000`. Hugging Face model files are
kept in a dedicated Docker volume; user audio files are not stored there.

### API

Interactive API documentation is available at `/docs`. The primary workflow is:

1. Send `multipart/form-data` to `POST /api/transcriptions`.
2. Poll `GET /api/transcriptions/{id}` for status and results.
3. Download an export from
   `GET /api/transcriptions/{id}/export/{txt|json|srt|vtt}`.
4. Optionally delete a result early with `DELETE /api/transcriptions/{id}`.

Results are stored only in memory and expire after `JOB_TTL_MINUTES`. The
in-memory job store is suitable for a single-server deployment. Multi-process or
distributed deployments should replace it with a shared store such as Redis.

### Tests

```bash
pip install -e ".[dev]"
pytest
```

### Disclaimer

Machine-generated transcripts are not guaranteed to be legally, medically, or
forensically verbatim. Human review is required for high-stakes use cases.

---

<div dir="rtl">

## فارسی

**صدای فارسی، به خط فارسی.**

آوانگار یک برنامهٔ محلی و حریم‌خصوصی‌محور برای تبدیل صدای فارسی به متن دقیق و
خوانا است. این پروژه رابط وب راست‌به‌چپ، API تمیز، نرمال‌سازی نگارش فارسی،
زمان‌بندی بخش‌ها، نمایش میزان اطمینان و خروجی‌های TXT، JSON، SRT و VTT ارائه
می‌دهد.

### قابلیت‌ها

- بارگذاری فایل‌های MP3، WAV، M4A، OGG، WebM، MP4، MPEG و FLAC
- ضبط مستقیم صدا از میکروفون مرورگر
- تشخیص گفتار فارسی با `faster-whisper` و تشخیص بخش‌های دارای صدا
- یکسان‌سازی حروف عربی و فارسی، فاصله‌گذاری و نیم‌فاصله
- زمان‌بندی کلمه و بخش، امتیاز اطمینان و علامت‌گذاری بخش‌های نامطمئن
- خروجی متن ساده، JSON ساختاریافته، SRT و WebVTT
- حذف فایل صوتی موقت بلافاصله پس از پردازش
- حالت نمایشی برای بررسی رابط بدون دریافت مدل تشخیص گفتار

> تفکیک واقعی چند گوینده هنوز در این MVP پیاده‌سازی نشده است. اگر گزینهٔ برچسب
> گوینده روشن باشد، ساختار خروجی آماده می‌شود، اما همهٔ بخش‌ها «گوینده ۱» خواهند
> بود.

### اجرای سریع

به Python 3.11 یا جدیدتر نیاز دارید. برای پردازش فرمت‌های غیر WAV نیز باید
`ffmpeg` نصب باشد.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

سپس آدرس `http://127.0.0.1:8000` را باز کنید.

در نصب پایه، برنامه در حالت نمایشی اجرا می‌شود و به‌روشنی اعلام می‌کند که متن
نمونه از محتوای فایل صوتی استخراج نشده است.

### فعال‌کردن رونویسی واقعی

```bash
pip install -e ".[whisper]"
cp .env.example .env
uvicorn app.main:app --reload
```

در نخستین اجرا، `faster-whisper` مدل تنظیم‌شده را دریافت می‌کند. مدل پیش‌فرض
`small` است. برای دقت بیشتر یا سخت‌افزار متفاوت، مقادیر زیر را در `.env` تغییر
دهید:

```dotenv
TRANSCRIBER_MODE=whisper
WHISPER_MODEL=medium
WHISPER_DEVICE=auto
WHISPER_COMPUTE_TYPE=default
```

- `TRANSCRIBER_MODE=auto` در صورت وجود Whisper از آن استفاده می‌کند و در صورت
  خطای راه‌اندازی به حالت نمایشی برمی‌گردد.
- `TRANSCRIBER_MODE=whisper` اگر موتور یا مدل آماده نباشد، راه‌اندازی را با خطا
  متوقف می‌کند. این حالت برای محیط تولید پیشنهاد می‌شود.
- `TRANSCRIBER_MODE=demo` همیشه خروجی نمونه و مشخص‌شده تولید می‌کند.

### Docker

```bash
docker compose up --build
```

برنامه در پورت `8000` در دسترس خواهد بود. فایل‌های مدل Hugging Face در یک
volume جداگانه نگهداری می‌شوند و فایل‌های صوتی کاربران در آن ذخیره نمی‌شوند.

### API

مستندات تعاملی API در `/docs` قرار دارد. روند اصلی:

1. ارسال `multipart/form-data` به `POST /api/transcriptions`
2. دریافت وضعیت و نتیجه از `GET /api/transcriptions/{id}`
3. دریافت خروجی از
   `GET /api/transcriptions/{id}/export/{txt|json|srt|vtt}`
4. حذف زودهنگام نتیجه با `DELETE /api/transcriptions/{id}`

نتیجه‌ها فقط در حافظه نگهداری می‌شوند و پس از مدت `JOB_TTL_MINUTES` منقضی
خواهند شد. این حافظهٔ موقت برای استقرار تک‌سرور مناسب است. در استقرار چندپردازه‌ای
یا توزیع‌شده باید آن را با یک مخزن مشترک مانند Redis جایگزین کرد.

### تست

```bash
pip install -e ".[dev]"
pytest
```

### محدودیت مسئولیت

رونویسی ماشینی برای کاربردهای حقوقی، پزشکی یا قضایی تضمین واژه‌به‌واژه نیست.
در کاربردهای حساس، بازبینی انسانی ضروری است.

</div>
