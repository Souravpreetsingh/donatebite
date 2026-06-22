(function () {
  var currentCall = null;
  var localStream = null;
  var pollInterval = null;
  var timerInterval = null;
  var seconds = 0;
  var donationId = null;

  var callStatus = document.getElementById('call-status-text');
  var callTimer = document.getElementById('call-timer');
  var callStartBtn = document.getElementById('call-start-btn');
  var callEndBtn = document.getElementById('call-end-btn');

  var pathMatch = window.location.pathname.match(/\/chat\/(\d+)/);
  if (pathMatch) donationId = parseInt(pathMatch[1]);
  if (!donationId) return;

  var peer = new Peer(undefined, { debug: 0 });

  peer.on('open', function () {
    watchForCalls();
  });

  peer.on('call', function (incomingCall) {
    if (currentCall) { incomingCall.close(); return; }
    stopWatching();
    toggleCallModal();
    callStatus.textContent = 'Incoming call...';
    callStartBtn.disabled = true;
    callEndBtn.disabled = false;
    incomingCall.answer(localStream || null);
    if (!localStream) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function (s) {
          localStream = s;
          incomingCall.answer(s);
        })
        .catch(function () { callStatus.textContent = 'Mic blocked'; });
    }
    setupCall(incomingCall);
  });

  peer.on('error', function () {});

  function watchForCalls() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(function () {
      fetch('/call/' + donationId + '/check')
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.active && data.peer_id && !currentCall) {
            stopWatching();
            toggleCallModal();
            callStatus.textContent = 'Incoming call...';
            callStartBtn.disabled = true;
            callEndBtn.disabled = false;
            navigator.mediaDevices.getUserMedia({ audio: true })
              .then(function (stream) {
                localStream = stream;
                callStatus.textContent = 'Connecting...';
                var call = peer.call(data.peer_id, stream);
                setupCall(call);
              })
              .catch(function () { callStatus.textContent = 'Mic blocked'; });
          }
        })
        .catch(function () {});
    }, 2000);
  }

  function stopWatching() {
    if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }
  }

  window.toggleCallModal = function () {
    var m = new bootstrap.Modal(document.getElementById('callModal'));
    m.show();
  };

  function getMyPeerId() {
    if (peer && peer.id) return Promise.resolve(peer.id);
    return new Promise(function (resolve) {
      peer.on('open', function (id) { resolve(id); });
    });
  }

  window.startCall = function (did) {
    donationId = did;
    stopWatching();
    callStartBtn.disabled = true;
    callEndBtn.disabled = false;
    callStatus.textContent = 'Requesting microphone...';

    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(function (stream) {
        localStream = stream;
        callStatus.textContent = 'Connecting...';
        return getMyPeerId();
      })
      .then(function (myId) {
        callStatus.textContent = 'Ringing...';
        fetch('/call/' + donationId + '/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ peer_id: myId })
        });
      })
      .catch(function () {
        callStatus.textContent = 'Microphone access denied';
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
      var audio = document.createElement('audio');
      audio.srcObject = remoteStream;
      audio.autoplay = true;
    });

    call.on('close', function () { endCall(); });
    call.on('error', function () { endCall(); });
  }

  window.endCall = function () {
    if (currentCall) { currentCall.close(); currentCall = null; }
    if (localStream) { localStream.getTracks().forEach(function (t) { t.stop(); }); localStream = null; }
    stopTimer();
    stopWatching();
    fetch('/call/' + donationId + '/end', { method: 'POST' }).catch(function () {});
    callStatus.textContent = 'Call ended';
    resetCallUI();
  };

  function startTimer() {
    timerInterval = setInterval(function () {
      seconds++;
      var m = String(Math.floor(seconds / 60)).padStart(2, '0');
      var s = String(seconds % 60).padStart(2, '0');
      callTimer.textContent = m + ':' + s;
    }, 1000);
  }

  function stopTimer() {
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
  }

  function resetCallUI() {
    watchForCalls();
    callStartBtn.disabled = false;
    callEndBtn.disabled = true;
    if (callTimer) callTimer.classList.add('d-none');
    setTimeout(function () {
      var modal = bootstrap.Modal.getInstance(document.getElementById('callModal'));
      if (modal) modal.hide();
    }, 2000);
  }
})();
