(function () {
  var currentCall = null;
  var localStream = null;
  var pollInterval = null;
  var timerInterval = null;
  var seconds = 0;
  var donationId = null;
  var isInitiator = false;

  var callStatus = document.getElementById('call-status-text');
  var callTimer = document.getElementById('call-timer');
  var callStartBtn = document.getElementById('call-start-btn');
  var callEndBtn = document.getElementById('call-end-btn');

  var pathMatch = window.location.pathname.match(/\/chat\/(\d+)/);
  if (pathMatch) donationId = parseInt(pathMatch[1]);
  if (!donationId) return;

  var peer = new Peer(undefined, { debug: 2 });

  peer.on('open', function () {
    if (!donationId) return;
    pollInterval = setInterval(function () {
      fetch('/call/' + donationId + '/check')
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.active && data.peer_id && !isInitiator && !currentCall) {
            clearInterval(pollInterval);
            pollInterval = null;
            if (confirm('Incoming voice call. Accept?')) {
              joinCall(data.peer_id);
            }
          }
        })
        .catch(function () {});
    }, 3000);
  });

  peer.on('call', function (incomingCall) {
    if (currentCall) { incomingCall.close(); return; }
    if (isInitiator && incomingCall) {
      incomingCall.answer(localStream);
      setupCall(incomingCall);
      return;
    }
    if (confirm('Incoming voice call. Accept?')) {
      toggleCallModal();
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function (stream) {
          localStream = stream;
          incomingCall.answer(stream);
          setupCall(incomingCall);
        })
        .catch(function () { callStatus.textContent = 'Microphone denied'; });
    } else {
      incomingCall.close();
    }
  });

  peer.on('error', function () {});

  window.toggleCallModal = function () {
    var modal = new bootstrap.Modal(document.getElementById('callModal'));
    modal.show();
  };

  function joinCall(remotePeerId) {
    isInitiator = false;
    callStartBtn.disabled = true;
    callEndBtn.disabled = false;
    callStatus.textContent = 'Connecting...';
    toggleCallModal();

    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(function (stream) {
        localStream = stream;
        callStatus.textContent = 'Calling...';
        var call = peer.call(remotePeerId, stream);
        setupCall(call);
      })
      .catch(function () {
        callStatus.textContent = 'Microphone access denied';
        resetCallUI();
      });
  }

  window.startCall = function (did, uid) {
    donationId = did;
    isInitiator = true;
    callStartBtn.disabled = true;
    callEndBtn.disabled = false;
    callStatus.textContent = 'Requesting microphone...';
    if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }

    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(function (stream) {
        localStream = stream;
        callStatus.textContent = 'Waiting for other person...';

        if (!peer || !peer.id) {
          peer = new Peer(undefined, { debug: 2 });
          return new Promise(function (resolve) {
            peer.on('open', function () { resolve(); });
          });
        }
      })
      .then(function () {
        fetch('/call/' + donationId + '/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ peer_id: peer.id })
        });
        callStatus.textContent = 'Ringing...';
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
    if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }
    stopTimer();
    isInitiator = false;
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
    callStartBtn.disabled = false;
    callEndBtn.disabled = true;
    if (callTimer) callTimer.classList.add('d-none');
    setTimeout(function () {
      var modal = bootstrap.Modal.getInstance(document.getElementById('callModal'));
      if (modal) modal.hide();
    }, 2000);
  }
})();
