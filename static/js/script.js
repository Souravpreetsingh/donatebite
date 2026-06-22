'use strict';

(function () {
  // ── Auto-dismiss flash messages after 6 seconds ──
  document.querySelectorAll('.alert-dismissible').forEach(function (el) {
    setTimeout(function () {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 6000);
  });

  // ── Confirm destructive actions ──
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.dataset.confirm || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });
})();
