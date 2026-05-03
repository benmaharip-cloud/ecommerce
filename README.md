# ShopDjango — E-commerce complet avec Django

Plateforme e-commerce complète construite avec Django, adaptée au marché africain (FCFA, Mobile Money, etc.).

## Fonctionnalités incluses (16 modules)

### Modules de base
- Catalogue produits (catégories, variantes, images, filtres, recherche)
- Panier Redis (anonyme + connecté, coupons)
- Authentification JWT + OAuth Google
- Commandes & historique
- Paiement Stripe + Mobile Money + Cash

### Modules avancés
- Avis & notations (modération, achats vérifiés, signalement)
- Wishlist / Favoris (alertes prix, retour en stock)
- Coupons & codes promo (pourcentage, montant fixe, livraison gratuite)
- Livraison & tracking GPS (Google Maps, suivi temps réel)
- Chat support en direct (WebSocket Django Channels)
- Programme de fidélité & points (niveaux Bronze/Argent/Or/Platine)
- Multi-langue (FR, EN, AR, PT) + multi-devises (FCFA, USD, EUR)
- Tableau de bord vendeur (stats, commandes, stock)
- Notifications push (Firebase FCM, SMS Twilio, WebSocket)
- Recommandations IA (collaborative filtering, historique, tendances)

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Framework | Django 4.2 |
| API REST | Django REST Framework |
| Auth | JWT (SimpleJWT) |
| Base de données | PostgreSQL |
| Cache/Panier | Redis |
| Tâches async | Celery + Celery Beat |
| WebSocket | Django Channels |
| Paiement | Stripe |
| Notifications push | Firebase FCM |
| SMS | Twilio |
| i18n | Django i18n + Rosetta |
| Serveur | Gunicorn + WhiteNoise |

## Installation

### 1. Cloner et configurer l'environnement

```bash
git clone <votre-repo>
cd ecommerce

python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Variables d'environnement

```bash
cp .env.example .env
# Modifier .env avec vos vraies valeurs
```

### 3. Base de données

```bash
# Créer la base PostgreSQL
createdb ecommerce_db

# Migrations
python manage.py makemigrations
python manage.py migrate

# Superutilisateur admin
python manage.py createsuperuser

# Données de test (optionnel)
python manage.py loaddata fixtures/initial_data.json
```

### 4. Lancer les services

```bash
# Terminal 1 — Serveur Django
python manage.py runserver

# Terminal 2 — Celery worker
celery -A ecommerce worker -l info

# Terminal 3 — Celery Beat (tâches périodiques)
celery -A ecommerce beat -l info

# Terminal 4 — Redis (si pas installé comme service)
redis-server
```

### 5. Accéder au site

- Site : http://localhost:8000
- Admin : http://localhost:8000/fr/admin/
- Rosetta (traductions) : http://localhost:8000/rosetta/

## Structure du projet

```
ecommerce/
├── manage.py
├── requirements.txt
├── .env.example
├── ecommerce/              # Config principale
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── asgi.py
├── apps/
│   ├── users/              # Auth & profils
│   ├── products/           # Catalogue
│   ├── cart/               # Panier Redis
│   ├── orders/             # Commandes
│   ├── payments/           # Stripe & Mobile Money
│   ├── reviews/            # Avis & notations
│   ├── wishlist/           # Favoris
│   ├── coupons/            # Codes promo
│   ├── delivery/           # Livraison & tracking
│   ├── chat/               # Support WebSocket
│   ├── loyalty/            # Programme fidélité
│   ├── notifications/      # Push & SMS
│   ├── vendor/             # Dashboard vendeur
│   └── recommendations/    # Recommandations IA
├── templates/
├── static/
│   ├── css/main.css
│   └── js/main.js
└── locale/                 # Fichiers de traduction
```

## Intégrations tierces

### Stripe
1. Créer un compte sur stripe.com
2. Récupérer les clés API (test ou live)
3. Configurer le webhook : `stripe listen --forward-to localhost:8000/api/payments/webhook/`

### Firebase (Notifications push)
1. Créer un projet Firebase Console
2. Télécharger `firebase-credentials.json`
3. Placer à la racine du projet

### Twilio (SMS)
1. Créer un compte Twilio
2. Obtenir un numéro de téléphone
3. Renseigner les variables dans `.env`

### Google Maps (Tracking)
1. Activer Maps JavaScript API sur Google Cloud Console
2. Ajouter la clé dans les templates

## Déploiement production

```bash
# Variables d'environnement production
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com

# Collecte des fichiers statiques
python manage.py collectstatic

# Lancer avec Gunicorn
gunicorn ecommerce.asgi:application -k uvicorn.workers.UvicornWorker --workers 4
```

## Licence
MIT — Libre d'utilisation et de modification.
