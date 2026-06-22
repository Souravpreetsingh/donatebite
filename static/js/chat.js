(function () {
  var messageForm = document.getElementById('message-form');
  var messageInput = document.getElementById('message-input');
  var chatMessages = document.getElementById('chat-messages');

  if (!messageForm || !messageInput || !chatMessages) return;

  var donationId = window.location.pathname.match(/\/chat\/(\d+)/);
  if (!donationId) return;

  var donationIdVal = donationId[1];
  var currentUserId = parseInt(chatMessages.dataset.userId || '0');

  window.sendMessage = function (e, did) {
    e.preventDefault();
    var msg = messageInput.value.trim();
    if (!msg) return;
    messageInput.disabled = true;

    var formData = new FormData();
    formData.append('message', msg);

    fetch('/chat/' + did + '/send', {
      method: 'POST',
      body: formData
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.success) {
        messageInput.value = '';
        scrollToBottom();
      }
    })
    .catch(function () {})
    .finally(function () {
      messageInput.disabled = false;
      messageInput.focus();
    });
  };

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function pollMessages() {
    fetch('/chat/' + donationIdVal + '/messages')
      .then(function (r) { return r.json(); })
      .then(function (messages) {
        var currentCount = chatMessages.querySelectorAll('.message-bubble').length;
        if (messages.length !== currentCount || currentCount === 0) {
          chatMessages.innerHTML = '';
          if (messages.length === 0) {
            chatMessages.innerHTML =
              '<div class="h-100 d-flex align-items-center justify-content-center">' +
              '<div class="text-center text-muted">' +
              '<i class="bi bi-chat-square-text fs-1 d-block mb-2"></i>' +
              '<small>No messages yet. Say hello!</small></div></div>';
          } else {
            messages.forEach(function (m) {
              var div = document.createElement('div');
              div.className = 'd-flex mb-3' + (m.sender_id === currentUserId ? ' justify-content-end' : '');
              div.innerHTML =
                '<div class="message-bubble ' +
                (m.sender_id === currentUserId ? 'message-sent' : 'message-received') +
                '"><div class="small">' + escapeHtml(m.message) +
                '</div><div class="small text-muted" style="font-size:0.65rem;">' +
                (m.created_at ? m.created_at.slice(0, 16) : '') + '</div></div>';
              chatMessages.appendChild(div);
            });
          }
          scrollToBottom();
        }
      })
      .catch(function () {});
  }

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }

  scrollToBottom();
  setInterval(pollMessages, 3000);
})();
