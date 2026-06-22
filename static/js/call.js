(function () {
  var peer = null;
  var currentCall = null;
  var callInterval = null;
  var timerInterval = null;
  var seconds = 0;
  var donationId = null;
  var userId = null;
  var otherPeerId = null;

  var callStatus = document.getElementById('call-status-text');
  var callTimer = document.getElementById('call-timer');
  var callStartBtn = document.getElementById('call-start-btn');
  var callEndBtn = document.getElementById('call-end-btn');

  var pathMatch = window.location.pathname.match(/\/chat\/(\d+)/);
  if (pathMatch) {
    donationId = parseInt(pathMatch[1]);
  }

  window.toggleCallModal = function () {
    var modal = new bootstrap.Modal(document.getElementById('callModal'));
    modal.show();
  };

  window.startCall = function (did, uid) {
    donationId = did;
    userId = uid;
    callStartBtn.disabled = true;
    callEndBtn.disabled = false;
    callStatus.textContent = 'Connecting...';

    peer = new Peer('call-' + donationId + '-' + userId + '-' + Date.now());

    peer.on('open', function (id) {
      otherPeerId = id;
      callStatus.textContent = 'Ringing...';

      fetch('/call/' + donationId + '/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ peer_id: id })
      }).catch(function () {});

      callInterval = setInterval(function () {
        fetch('/call/' + donationId + '/check')
          .then(function (r) { return r.json(); })
          .then(function (data) {
            if (data.active && data.peer_id !== otherPeerId) {
              clearInterval(callInterval);
              callInterval = null;
              callStatus.textContent = 'Connecting...';
              var conn = peer.connect(data.peer_id);
              var call = peer.call(data.peer_id, null);
              setupCall(call);
            }
          })
          .catch(function () {});
      }, 2000);

      peer.on('call', function (incomingCall) {
        clearInterval(callInterval);
        callInterval = null;
        callStatus.textContent = 'Connecting...';
        incomingCall.answer(null);
        setupCall(incomingCall);
      });

      peer.on('connection', function (conn) {
        conn.on('open', function () {});
      });
    });

    peer.on('error', function (err) {
      callStatus.textContent = 'Call failed: ' + err.type;
      resetCallUI();
    });
  };

  function setupCall(call) {
    currentCall = call;
    callStatus.textContent = 'Connected';
    callTimer.classList.remove('d-none');
    seconds = 0;
    startTimer();

    call.on('stream', function (remoteStream) {
      var audio = new Audio();
      audio.srcObject = remoteStream;
      audio.play();
    });

    call.on('close', function () {
      endCall();
    });

    call.on('error', function () {
      callStatus.textContent = 'Call ended';
      resetCallUI();
    });
  }

  window.endCall = function () {
    if (currentCall) {
      currentCall.close();
      currentCall = null;
    }
    if (peer) {
      peer.destroy();
      peer = null;
    }
    stopTimer();
    if (callInterval) {
      clearInterval(callInterval);
      callInterval = null;
    }
    fetch('/call/' + donationId + '/end', { method: 'POST' }).catch(function () {});
    callStatus.textContent = 'Call ended';
    resetCallUI();
  };

  function startTimer() {
    timerInterval = setInterval(function () {
      seconds++;
      var min = String(Math.floor(seconds / 60)).padStart(2, '0');
      var sec = String(seconds % 60).padStart(2, '0');
      callTimer.textContent = min + ':' + sec;
    }, 1000);
  }

  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  function resetCallUI() {
    callStartBtn.disabled = false;
    callEndBtn.disabled = true;
    if (callTimer) callTimer.classList.add('d-none');
    setTimeout(function () {
      var modal = bootstrap.Modal.getInstance(document.getElementById('callModal'));
      if (modal) modal.hide();
    }, 2000);
  }
})();
