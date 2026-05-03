content = """SECRET_KEY=shopdjango-secret-key-ibni-abakar-2024-tchad
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=ecommerce_db
DB_USER=shop_user
DB_PASSWORD=Shop2024
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@shopdjango.com
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
"""
open('.env', 'w').write(content)
print('OK - .env cree avec succes')
