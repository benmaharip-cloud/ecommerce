import os

# ==================== REVIEWS ====================
os.makedirs('templates/reviews', exist_ok=True)
os.makedirs('templates/users', exist_ok=True)
os.makedirs('templates/products', exist_ok=True)
os.makedirs('templates/vendor', exist_ok=True)

# 1. Reviews URLs
open('apps/reviews/urls.py', 'w').write('''from django.urls import path
from . import views

app_name = "reviews"
urlpatterns = [
    path("ajouter/<int:product_id>/", views.add_review, name="add"),
    path("supprimer/<int:review_id>/", views.delete_review, name="delete"),
]
''')

# 2. Reviews views
open('apps/reviews/views.py', 'w').write('''from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.reviews.models import Review
from apps.products.models import Product


@login_required
@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    rating = int(request.POST.get("rating", 5))
    content = request.POST.get("content", "").strip()
    if not content:
        messages.error(request, "Le contenu de l\'avis est requis")
        return redirect(f"/produits/{product.slug}/")
    review, created = Review.objects.get_or_create(
        product=product, user=request.user,
        defaults={"rating": rating, "content": content, "is_approved": True}
    )
    if not created:
        review.rating = rating
        review.content = content
        review.is_approved = True
        review.save()
        messages.success(request, "Votre avis a ete mis a jour")
    else:
        messages.success(request, "Votre avis a ete ajoute avec succes")
    return redirect(f"/produits/{product.slug}/")


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()
    messages.success(request, "Avis supprime")
    return redirect(f"/produits/{product_slug}/")
''')

# 3. Product detail template with reviews
open('templates/products/detail.html', 'w').write(r'''{% extends "base/base.html" %}
{% load i18n %}
{% block title %}{{ product.name }} — ShopDjango{% endblock %}
{% block content %}
<div class="container">
  <nav aria-label="breadcrumb" class="mb-3">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><a href="/">Accueil</a></li>
      <li class="breadcrumb-item"><a href="/produits/">Catalogue</a></li>
      <li class="breadcrumb-item active">{{ product.name }}</li>
    </ol>
  </nav>
  <div class="row g-4 mb-5">
    <div class="col-md-5">
      {% if product.images.exists %}
      <img src="{{ product.images.first.image.url }}" alt="{{ product.name }}" class="img-fluid rounded-3 shadow-sm" style="width:100%;height:400px;object-fit:cover;">
      {% else %}
      <div class="bg-light rounded-3 d-flex align-items-center justify-content-center" style="height:400px;">
        <i class="bi bi-image text-muted" style="font-size:80px;"></i>
      </div>
      {% endif %}
    </div>
    <div class="col-md-7">
      <p class="text-muted mb-1">{{ product.category.name }}</p>
      <h2 class="fw-bold">{{ product.name }}</h2>
      <div class="d-flex align-items-center gap-2 mb-3">
        <div class="text-warning">
          {% for i in "12345" %}{% if forloop.counter <= product.average_rating %}<i class="bi bi-star-fill"></i>{% else %}<i class="bi bi-star"></i>{% endif %}{% endfor %}
        </div>
        <span class="text-muted small">({{ reviews|length }} avis)</span>
      </div>
      <div class="mb-3">
        {% if product.discount_price %}
        <span class="fs-2 fw-bold text-primary">{{ product.discount_price|floatformat:0 }} FCFA</span>
        <span class="text-muted text-decoration-line-through ms-2 fs-5">{{ product.price|floatformat:0 }}</span>
        <span class="badge bg-danger ms-2">-{{ product.discount_percent }}%</span>
        {% else %}
        <span class="fs-2 fw-bold text-primary">{{ product.price|floatformat:0 }} FCFA</span>
        {% endif %}
      </div>
      <p class="text-muted">{{ product.description }}</p>
      <div class="mb-3">
        {% if product.in_stock %}
        <span class="badge bg-success fs-6"><i class="bi bi-check-circle me-1"></i>En stock ({{ product.stock }} unites)</span>
        {% else %}
        <span class="badge bg-danger fs-6">Rupture de stock</span>
        {% endif %}
      </div>
      {% if product.in_stock %}
      <form action="/panier/ajouter/{{ product.id }}/" method="post" class="d-flex gap-3 align-items-center mb-3">
        {% csrf_token %}
        <input type="number" name="quantity" value="1" min="1" max="{{ product.stock }}" class="form-control" style="width:90px;">
        <button type="submit" class="btn btn-primary btn-lg flex-grow-1">
          <i class="bi bi-cart-plus me-2"></i>Ajouter au panier
        </button>
      </form>
      {% endif %}
      {% if user.is_authenticated %}
      <form action="/favoris/toggle/{{ product.id }}/" method="post" class="d-inline">
        {% csrf_token %}
        <button type="submit" class="btn btn-outline-danger">
          <i class="bi bi-heart{% if in_wishlist %}-fill{% endif %} me-1"></i>
          {% if in_wishlist %}Retirer des favoris{% else %}Ajouter aux favoris{% endif %}
        </button>
      </form>
      {% endif %}
    </div>
  </div>

  <div class="row g-4">
    <div class="col-md-8">
      <h4 class="fw-bold mb-3"><i class="bi bi-chat-left-text me-2"></i>Avis clients ({{ reviews|length }})</h4>
      {% if user.is_authenticated %}
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <h6 class="fw-semibold mb-3">Laisser un avis</h6>
          <form action="/avis/ajouter/{{ product.id }}/" method="post">
            {% csrf_token %}
            <div class="mb-3">
              <label class="form-label fw-semibold">Note</label>
              <div class="btn-group" role="group">
                {% for i in "12345" %}
                <input type="radio" class="btn-check" name="rating" id="star{{ forloop.counter }}" value="{{ forloop.counter }}" {% if forloop.counter == 5 %}checked{% endif %}>
                <label class="btn btn-outline-warning" for="star{{ forloop.counter }}">{{ forloop.counter }}★</label>
                {% endfor %}
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold">Votre avis</label>
              <textarea name="content" class="form-control" rows="3" placeholder="Partagez votre experience..." required></textarea>
            </div>
            <button type="submit" class="btn btn-primary">
              <i class="bi bi-send me-2"></i>Publier mon avis
            </button>
          </form>
        </div>
      </div>
      {% else %}
      <div class="alert alert-info">
        <a href="/compte/connexion/">Connectez-vous</a> pour laisser un avis.
      </div>
      {% endif %}

      {% for review in reviews %}
      <div class="card border-0 shadow-sm mb-3">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <div class="d-flex align-items-center gap-2">
              <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center fw-bold" style="width:36px;height:36px;font-size:14px;">
                {{ review.user.first_name.0 }}{{ review.user.last_name.0 }}
              </div>
              <div>
                <p class="mb-0 fw-semibold">{{ review.user.full_name }}</p>
                <div class="text-warning small">
                  {% for i in "12345" %}{% if forloop.counter <= review.rating %}<i class="bi bi-star-fill"></i>{% else %}<i class="bi bi-star"></i>{% endif %}{% endfor %}
                </div>
              </div>
            </div>
            <div class="d-flex align-items-center gap-2">
              <small class="text-muted">{{ review.created_at|date:"d/m/Y" }}</small>
              {% if review.is_verified_purchase %}<span class="badge bg-success small">Achat verifie</span>{% endif %}
              {% if user == review.user %}
              <form action="/avis/supprimer/{{ review.id }}/" method="post" class="d-inline">
                {% csrf_token %}
                <button type="submit" class="btn btn-sm btn-link text-danger p-0"><i class="bi bi-trash3"></i></button>
              </form>
              {% endif %}
            </div>
          </div>
          <p class="mb-0 text-muted">{{ review.content }}</p>
        </div>
      </div>
      {% empty %}
      <div class="text-center py-4 text-muted">
        <i class="bi bi-chat-left-dots" style="font-size:40px;"></i>
        <p class="mt-2">Aucun avis pour ce produit. Soyez le premier !</p>
      </div>
      {% endfor %}
    </div>

    <div class="col-md-4">
      <h5 class="fw-bold mb-3">Produits similaires</h5>
      {% for p in similar_products %}
      <div class="card border-0 shadow-sm mb-3">
        <div class="row g-0 align-items-center">
          <div class="col-4">
            {% if p.images.exists %}
            <img src="{{ p.images.first.image.url }}" class="img-fluid rounded-start" style="height:80px;object-fit:cover;" alt="{{ p.name }}">
            {% else %}
            <div class="bg-light d-flex align-items-center justify-content-center rounded-start" style="height:80px;"><i class="bi bi-image text-muted"></i></div>
            {% endif %}
          </div>
          <div class="col-8">
            <div class="card-body py-2 px-3">
              <p class="mb-0 small fw-semibold"><a href="/produits/{{ p.slug }}/" class="text-dark text-decoration-none">{{ p.name }}</a></p>
              <p class="mb-0 text-primary small fw-bold">{{ p.effective_price|floatformat:0 }} FCFA</p>
            </div>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
''')

# 4. Profile template
open('templates/users/profile.html', 'w').write(r'''{% extends "base/base.html" %}
{% block title %}Mon profil — ShopDjango{% endblock %}
{% block content %}
<div class="container" style="max-width:900px;">
  <h2 class="fw-bold mb-4"><i class="bi bi-person-circle me-2"></i>Mon profil</h2>
  {% if messages %}{% for message in messages %}
  <div class="alert alert-{{ message.tags }} alert-dismissible fade show">{{ message }}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
  {% endfor %}{% endif %}
  <div class="row g-4">
    <div class="col-md-4">
      <div class="card border-0 shadow-sm text-center p-4">
        {% if user.avatar %}
        <img src="{{ user.avatar.url }}" class="rounded-circle mx-auto mb-3" style="width:100px;height:100px;object-fit:cover;">
        {% else %}
        <div class="rounded-circle bg-primary text-white mx-auto mb-3 d-flex align-items-center justify-content-center fw-bold" style="width:100px;height:100px;font-size:36px;">{{ user.first_name.0 }}{{ user.last_name.0 }}</div>
        {% endif %}
        <h5 class="fw-bold mb-0">{{ user.full_name }}</h5>
        <p class="text-muted small">{{ user.email }}</p>
        {% if loyalty %}<span class="badge bg-warning text-dark px-3 py-2"><i class="bi bi-trophy me-1"></i>{{ loyalty.get_level_display }} — {{ loyalty.points }} pts</span>{% endif %}
        <hr>
        <div class="row text-center g-2">
          <div class="col-6"><div class="bg-light rounded p-2"><div class="fw-bold text-primary">{{ recent_orders|length }}</div><small class="text-muted">Commandes</small></div></div>
          <div class="col-6"><div class="bg-light rounded p-2"><div class="fw-bold text-danger">{% if user.wishlist %}{{ user.wishlist.items.count }}{% else %}0{% endif %}</div><small class="text-muted">Favoris</small></div></div>
        </div>
      </div>
    </div>
    <div class="col-md-8">
      <div class="card border-0 shadow-sm mb-3">
        <div class="card-body">
          <h5 class="fw-semibold mb-3"><i class="bi bi-pencil me-2"></i>Modifier mon profil</h5>
          <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            <div class="row g-3">
              <div class="col-6"><label class="form-label">Prenom</label><input type="text" name="first_name" class="form-control" value="{{ user.first_name }}" required></div>
              <div class="col-6"><label class="form-label">Nom</label><input type="text" name="last_name" class="form-control" value="{{ user.last_name }}" required></div>
              <div class="col-12"><label class="form-label">Telephone</label><input type="tel" name="phone" class="form-control" value="{{ user.phone }}"></div>
              <div class="col-12"><label class="form-label">Photo de profil</label><input type="file" name="avatar" class="form-control" accept="image/*"></div>
              <div class="col-12"><button type="submit" class="btn btn-primary"><i class="bi bi-save me-2"></i>Sauvegarder</button></div>
            </div>
          </form>
        </div>
      </div>
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <h5 class="fw-semibold mb-3"><i class="bi bi-box-seam me-2"></i>Commandes recentes</h5>
          {% for order in recent_orders %}
          <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
            <div><p class="mb-0 fw-semibold">{{ order.reference }}</p><small class="text-muted">{{ order.created_at|date:"d/m/Y" }}</small></div>
            <div class="text-end"><p class="mb-0 fw-bold text-primary">{{ order.total|floatformat:0 }} FCFA</p>
              {% if order.status == "delivered" %}<span class="badge bg-success">Livre</span>
              {% elif order.status == "confirmed" %}<span class="badge bg-primary">Confirme</span>
              {% else %}<span class="badge bg-warning text-dark">En attente</span>{% endif %}
            </div>
          </div>
          {% empty %}<p class="text-muted text-center py-3">Aucune commande</p>{% endfor %}
          <a href="/commandes/" class="btn btn-outline-primary w-100 mt-3">Voir toutes mes commandes</a>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
''')

# 5. Search/List template
open('templates/products/list.html', 'w').write(r'''{% extends "base/base.html" %}
{% block title %}Catalogue — ShopDjango{% endblock %}
{% block content %}
<div class="container">
  <div class="row g-4">
    <div class="col-md-3">
      <div class="card border-0 shadow-sm sticky-top" style="top:80px;">
        <div class="card-body">
          <h6 class="fw-bold mb-3"><i class="bi bi-funnel me-2"></i>Filtres</h6>
          <form method="get">
            <input type="hidden" name="q" value="{{ request.GET.q }}">
            <div class="mb-3">
              <label class="form-label fw-semibold small">Categorie</label>
              <select name="category" class="form-select form-select-sm" onchange="this.form.submit()">
                <option value="">Toutes</option>
                {% for cat in categories %}
                <option value="{{ cat.slug }}" {% if request.GET.category == cat.slug %}selected{% endif %}>{{ cat.name }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold small">Prix min (FCFA)</label>
              <input type="number" name="min_price" class="form-control form-control-sm" value="{{ request.GET.min_price }}" placeholder="0">
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold small">Prix max (FCFA)</label>
              <input type="number" name="max_price" class="form-control form-control-sm" value="{{ request.GET.max_price }}" placeholder="1000000">
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold small">Trier par</label>
              <select name="sort" class="form-select form-select-sm" onchange="this.form.submit()">
                <option value="-created_at">Plus recents</option>
                <option value="price_asc" {% if request.GET.sort == "price_asc" %}selected{% endif %}>Prix croissant</option>
                <option value="price_desc" {% if request.GET.sort == "price_desc" %}selected{% endif %}>Prix decroissant</option>
              </select>
            </div>
            <button type="submit" class="btn btn-primary w-100 btn-sm">Appliquer</button>
            <a href="/produits/" class="btn btn-outline-secondary w-100 btn-sm mt-2">Reinitialiser</a>
          </form>
        </div>
      </div>
    </div>
    <div class="col-md-9">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h4 class="fw-bold mb-0">{% if request.GET.q %}Resultats pour "{{ request.GET.q }}"{% else %}Catalogue produits{% endif %}</h4>
          <small class="text-muted">{{ paginator.count }} produit(s)</small>
        </div>
      </div>
      <div class="row g-3">
        {% for product in products %}
        <div class="col-6 col-md-4">
          <div class="card border-0 shadow-sm h-100 product-card">
            <div class="position-relative">
              {% if product.images.exists %}
              <img src="{{ product.images.first.image.url }}" class="card-img-top" alt="{{ product.name }}" style="height:180px;object-fit:cover;">
              {% else %}
              <div class="bg-light d-flex align-items-center justify-content-center" style="height:180px;"><i class="bi bi-image text-muted fs-1"></i></div>
              {% endif %}
              {% if product.discount_price %}<span class="badge bg-danger position-absolute top-0 start-0 m-2">-{{ product.discount_percent }}%</span>{% endif %}
              {% if not product.in_stock %}<span class="badge bg-secondary position-absolute top-0 end-0 m-2">Rupture</span>{% endif %}
            </div>
            <div class="card-body d-flex flex-column">
              <p class="text-muted small mb-1">{{ product.category.name }}</p>
              <h6 class="fw-semibold mb-1"><a href="/produits/{{ product.slug }}/" class="text-dark text-decoration-none stretched-link">{{ product.name }}</a></h6>
              <div class="text-warning small mb-2">
                {% for i in "12345" %}{% if forloop.counter <= product.average_rating %}<i class="bi bi-star-fill"></i>{% else %}<i class="bi bi-star"></i>{% endif %}{% endfor %}
                <span class="text-muted">({{ product.reviews.count }})</span>
              </div>
              <div class="mt-auto">
                {% if product.discount_price %}
                <span class="fw-bold text-primary">{{ product.discount_price|floatformat:0 }} FCFA</span>
                <span class="text-muted text-decoration-line-through small ms-1">{{ product.price|floatformat:0 }}</span>
                {% else %}
                <span class="fw-bold text-primary">{{ product.price|floatformat:0 }} FCFA</span>
                {% endif %}
              </div>
            </div>
          </div>
        </div>
        {% empty %}
        <div class="col-12 text-center py-5">
          <i class="bi bi-search text-muted" style="font-size:60px;"></i>
          <h4 class="mt-3 text-muted">Aucun produit trouve</h4>
          <a href="/produits/" class="btn btn-primary mt-2">Voir tout le catalogue</a>
        </div>
        {% endfor %}
      </div>
      {% if is_paginated %}
      <nav class="mt-4">
        <ul class="pagination justify-content-center">
          {% if page_obj.has_previous %}<li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}">&laquo;</a></li>{% endif %}
          {% for num in page_obj.paginator.page_range %}<li class="page-item {% if page_obj.number == num %}active{% endif %}"><a class="page-link" href="?page={{ num }}">{{ num }}</a></li>{% endfor %}
          {% if page_obj.has_next %}<li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}">&raquo;</a></li>{% endif %}
        </ul>
      </nav>
      {% endif %}
    </div>
  </div>
</div>
{% endblock %}
''')

# 6. Vendor dashboard template
open('templates/vendor/dashboard.html', 'w').write(r'''{% extends "base/base.html" %}
{% block title %}Dashboard Vendeur — ShopDjango{% endblock %}
{% block content %}
<div class="container-fluid px-4">
  <div class="d-flex justify-content-between align-items-center mb-4">
    <h2 class="fw-bold"><i class="bi bi-shop me-2 text-primary"></i>Dashboard Vendeur</h2>
    <a href="/fr/admin/products/product/add/" class="btn btn-primary btn-sm"><i class="bi bi-plus-circle me-1"></i>Ajouter un produit</a>
  </div>
  <div class="row g-3 mb-4">
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm border-start border-primary border-4">
        <div class="card-body"><p class="text-muted small mb-1">Commandes ce mois</p><h3 class="fw-bold text-primary mb-0">{{ stats.monthly_orders }}</h3><small class="text-muted">Total: {{ stats.total_orders }}</small></div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm border-start border-success border-4">
        <div class="card-body"><p class="text-muted small mb-1">Revenus ce mois</p><h3 class="fw-bold text-success mb-0">{{ stats.monthly_revenue|floatformat:0 }}</h3><small class="text-muted">FCFA</small></div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm border-start border-warning border-4">
        <div class="card-body"><p class="text-muted small mb-1">Produits actifs</p><h3 class="fw-bold text-warning mb-0">{{ stats.active_products }}</h3><small class="text-muted">sur {{ stats.total_products }}</small></div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm border-start border-info border-4">
        <div class="card-body"><p class="text-muted small mb-1">Note moyenne</p><h3 class="fw-bold text-info mb-0">{{ stats.avg_rating|floatformat:1 }}★</h3><small class="text-muted">{{ stats.total_reviews }} avis</small></div>
      </div>
    </div>
  </div>
  <div class="row g-4">
    <div class="col-lg-8">
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-0 d-flex justify-content-between">
          <h6 class="fw-bold mb-0">Commandes recentes</h6>
          <a href="/vendeur/commandes/" class="btn btn-sm btn-outline-primary">Voir tout</a>
        </div>
        <div class="card-body p-0">
          <table class="table table-hover mb-0">
            <thead class="table-light"><tr><th>Reference</th><th>Client</th><th>Statut</th><th class="text-end">Total</th><th>Date</th></tr></thead>
            <tbody>
              {% for order in recent_orders %}
              <tr>
                <td><strong>{{ order.reference }}</strong></td>
                <td>{{ order.user.full_name }}</td>
                <td>{% if order.status == "delivered" %}<span class="badge bg-success">Livre</span>{% elif order.status == "confirmed" %}<span class="badge bg-primary">Confirme</span>{% elif order.status == "cancelled" %}<span class="badge bg-danger">Annule</span>{% else %}<span class="badge bg-warning text-dark">En attente</span>{% endif %}</td>
                <td class="text-end fw-bold">{{ order.total|floatformat:0 }} FCFA</td>
                <td class="text-muted small">{{ order.created_at|date:"d/m/Y" }}</td>
              </tr>
              {% empty %}<tr><td colspan="5" class="text-center text-muted py-3">Aucune commande</td></tr>{% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div class="col-lg-4">
      <div class="card border-0 shadow-sm mb-3">
        <div class="card-header bg-white border-0"><h6 class="fw-bold mb-0 text-warning"><i class="bi bi-exclamation-triangle me-1"></i>Stock faible</h6></div>
        <div class="list-group list-group-flush">
          {% for product in low_stock_products %}
          <div class="list-group-item d-flex justify-content-between align-items-center">
            <div><p class="mb-0 small fw-semibold">{{ product.name }}</p><small class="text-muted">{{ product.sku }}</small></div>
            <span class="badge {% if product.stock == 0 %}bg-danger{% else %}bg-warning text-dark{% endif %}">{{ product.stock }}</span>
          </div>
          {% empty %}<div class="list-group-item text-center text-muted small py-3">Tous les stocks sont OK</div>{% endfor %}
        </div>
      </div>
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-0"><h6 class="fw-bold mb-0">Top produits</h6></div>
        <div class="card-body">
          {% for p in top_products %}
          <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="small text-truncate" style="max-width:150px;">{{ p.product__name }}</span>
            <span class="badge bg-primary">{{ p.total_sold }} ventes</span>
          </div>
          {% empty %}<p class="text-muted small text-center">Aucune vente encore</p>{% endfor %}
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
''')

# 7. Ajouter reviews URLs dans ecommerce/urls.py
content = open('ecommerce/urls.py').read()
if 'avis/' not in content:
    content = content.replace(
        'path("fr/admin/", admin.site.urls),',
        'path("fr/admin/", admin.site.urls),\n    path("avis/", include(("apps.reviews.urls", "reviews"), namespace="reviews")),'
    )
    open('ecommerce/urls.py', 'w').write(content)
    print('OK - avis URL ajoutee')

# 8. Corriger vendor web_urls
open('apps/vendor/web_urls.py', 'w').write('''from django.urls import path
from . import views

app_name = "vendor"
urlpatterns = [
    path("", views.VendorDashboardView.as_view(), name="dashboard"),
    path("produits/", views.VendorProductListView.as_view(), name="products"),
    path("commandes/", views.VendorOrderListView.as_view(), name="orders"),
]
''')

print('Tous les fichiers installes avec succes !')
