// ShopDjango — Main JS

// Wishlist toggle AJAX
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.wishlist-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const productId = this.dataset.productId;
      const icon = this.querySelector('i');

      fetch(`/api/wishlist/toggle/${productId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest',
        },
      })
        .then(r => r.json())
        .then(data => {
          if (data.in_wishlist) {
            icon.className = 'bi bi-heart-fill text-danger';
          } else {
            icon.className = 'bi bi-heart';
          }
          showToast(data.message, 'success');
        });
    });
  });

  // Add to cart AJAX
  document.querySelectorAll('.add-to-cart-form').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            updateCartBadge(data.cart_count);
            showToast('Produit ajouté au panier !', 'success');
          }
        });
    });
  });

  // Quantity inputs
  document.querySelectorAll('.qty-input').forEach(input => {
    input.addEventListener('change', function () {
      if (this.value < 1) this.value = 1;
    });
  });

  // Initialize tooltips
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach(el => new bootstrap.Tooltip(el));
});

// Mettre à jour le badge du panier
function updateCartBadge(count) {
  const badge = document.querySelector('.cart-badge');
  if (badge) {
    badge.textContent = count;
    badge.style.display = count > 0 ? 'inline-flex' : 'none';
  }
}

// Afficher un toast Bootstrap
function showToast(message, type = 'success') {
  const toastContainer = document.getElementById('toast-container') || createToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-white bg-${type} border-0`;
  toast.setAttribute('role', 'alert');
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>`;
  toastContainer.appendChild(toast);
  new bootstrap.Toast(toast, { delay: 3000 }).show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function createToastContainer() {
  const div = document.createElement('div');
  div.id = 'toast-container';
  div.className = 'position-fixed top-0 end-0 p-3';
  div.style.zIndex = '9999';
  document.body.appendChild(div);
  return div;
}

// Lire cookie CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
      c = c.trim();
      if (c.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(c.slice(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Google Maps tracking
function initDeliveryMap(lat, lng, destLat, destLng) {
  if (typeof google === 'undefined') return;
  const map = new google.maps.Map(document.getElementById('delivery-map'), {
    center: { lat, lng },
    zoom: 13,
  });
  new google.maps.Marker({ position: { lat, lng }, map, label: '🛵', title: 'Livreur' });
  new google.maps.Marker({ position: { lat: destLat, lng: destLng }, map, label: '🏠', title: 'Destination' });
}

// Multi-devise conversion
const exchangeRates = { XAF: 1, USD: 0.00164, EUR: 0.00152 };
function convertPrice(amountXAF, targetCurrency) {
  return (amountXAF * (exchangeRates[targetCurrency] || 1)).toFixed(2);
}
