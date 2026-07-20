/**
 * Audio Input Module
 * Handles audio recording via MediaRecorder API and uploads to /api/transcribe
 * for Whisper transcription and filler-word detection.
 */

(function() {
    'use strict';

    // ── State ──────────────────────────────────────────────────────────────
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    let audioStream = null;
    let recordingStartTime = 0;
    let recordingTimerInterval = null;

    // ── DOM Elements ──────────────────────────────────────────────────────
    const voiceBtn = document.getElementById('voice-btn');
    const voiceBtnIcon = document.getElementById('voice-btn-icon');
    const voiceBtnText = document.getElementById('voice-btn-text');
    const voiceTranscriptContainer = document.getElementById('voice-transcript-container');
    const voiceFinalText = document.getElementById('voice-final-text');
    const voiceInterimText = document.getElementById('voice-interim-text');
    const voiceStatus = document.getElementById('voice-status');
    const fillerWarning = document.getElementById('filler-warning');
    const fillerWarningText = document.getElementById('filler-warning-text');
    const audioUpload = document.getElementById('audio-upload');
    const audioUploadName = document.getElementById('audio-upload-name');
    const mainInput = document.getElementById('answer-input');
    const sendBtn = document.getElementById('send-btn');

    // ── Helper: Update UI for recording state ─────────────────────────────
    function setRecordingUI(recording) {
        isRecording = recording;
        if (voiceBtn) {
            if (recording) {
                voiceBtn.classList.add('recording');
                voiceBtn.classList.remove('idle');
                if (voiceBtnIcon) voiceBtnIcon.textContent = '⏹';
                if (voiceBtnText) voiceBtnText.textContent = 'Stop Recording';
            } else {
                voiceBtn.classList.remove('recording');
                voiceBtn.classList.add('idle');
                if (voiceBtnIcon) voiceBtnIcon.textContent = '🎙';
                if (voiceBtnText) voiceBtnText.textContent = 'Speak Your Answer';
            }
        }
    }

    function setTranscriptUI(show) {
        if (voiceTranscriptContainer) {
            voiceTranscriptContainer.style.display = show ? 'block' : 'none';
        }
    }

    function setFillerWarning(count, words) {
        if (!fillerWarning || !fillerWarningText) return;
        if (count > 0) {
            const wordList = Object.entries(words).map(([w, c]) => `${w} (${c})`).join(', ');
            fillerWarningText.textContent = `Detected ${count} filler word(s): ${wordList}`;
            fillerWarning.style.display = 'flex';
        } else {
            fillerWarning.style.display = 'none';
        }
    }

    function setVoiceStatus(msg) {
        if (voiceStatus) voiceStatus.textContent = msg;
    }

    function updateRecordingTimer() {
        if (!recordingStartTime || !voiceStatus) return;
        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
        const secs = (elapsed % 60).toString().padStart(2, '0');
        voiceStatus.textContent = `Recording... ${mins}:${secs}`;
    }

    // ── Start Recording ────────────────────────────────────────────────────
    async function startRecording() {
        if (isRecording) return;

        try {
            // Request microphone access
            audioStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 16000
                }
            });

            // Create MediaRecorder (prefer webm/opus for good compression)
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                ? 'audio/webm;codecs=opus'
                : MediaRecorder.isTypeSupported('audio/webm')
                    ? 'audio/webm'
                    : 'audio/mp4';

            mediaRecorder = new MediaRecorder(audioStream, { mimeType });
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                await processRecording();
            };

            mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                setVoiceStatus('Recording error: ' + event.error);
                stopRecording();
            };

            // Start recording
            mediaRecorder.start(100); // Collect data every 100ms
            recordingStartTime = Date.now();
            setRecordingUI(true);
            setTranscriptUI(false);
            setFillerWarning(0, {});
            setVoiceStatus('Recording... 00:00');

            // Start timer display
            recordingTimerInterval = setInterval(updateRecordingTimer, 1000);

        } catch (err) {
            console.error('Failed to start recording:', err);
            let msg = 'Microphone access denied';
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                msg = 'Microphone permission denied. Please allow microphone access in browser settings.';
            } else if (err.name === 'NotFoundError') {
                msg = 'No microphone found. Please connect a microphone.';
            } else if (err.name === 'NotReadableError') {
                msg = 'Microphone is in use by another application.';
            }
            setVoiceStatus(msg);
            alert(msg);
            setRecordingUI(false);
        }
    }

    // ── Stop Recording ─────────────────────────────────────────────────────
    function stopRecording() {
        if (!isRecording || !mediaRecorder) return;

        // Stop timer
        if (recordingTimerInterval) {
            clearInterval(recordingTimerInterval);
            recordingTimerInterval = null;
        }

        // Stop MediaRecorder (triggers ondataavailable then onstop)
        if (mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }

        // Stop audio tracks
        if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
            audioStream = null;
        }

        setRecordingUI(false);
        setVoiceStatus('Processing audio...');
    }

    // ── Process & Upload Recording ────────────────────────────────────────
    async function processRecording() {
        if (audioChunks.length === 0) {
            setVoiceStatus('No audio recorded');
            setTimeout(() => setVoiceStatus(''), 2000);
            return;
        }

        // Create blob from chunks
        const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
        audioChunks = [];

        // Prepare form data
        const formData = new FormData();
        // Use .webm extension since we record in webm
        const fileName = `recording_${Date.now()}.webm`;
        formData.append('audio', audioBlob, fileName);

        try {
            // Upload to transcription endpoint
            const response = await fetch('/api/transcribe', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Transcription failed');
            }

            // Display transcript
            const transcript = result.transcript || '';
            if (voiceFinalText) voiceFinalText.textContent = transcript;
            if (voiceInterimText) voiceInterimText.textContent = '';
            setTranscriptUI(true);
            setVoiceStatus('Transcription complete ✓');

            // Show filler warning if any
            const fillerCount = result.filler_count || 0;
            const fillerWords = result.filler_words || {};
            setFillerWarning(fillerCount, fillerWords);

            // Populate main textarea for review/edit
            if (mainInput && transcript) {
                mainInput.value = transcript;
                // Auto-resize
                mainInput.style.height = 'auto';
                mainInput.style.height = Math.min(mainInput.scrollHeight, 150) + 'px';
            }

            // Enable send button
            if (sendBtn) sendBtn.disabled = false;

            // Auto-hide transcript after delay and switch to type mode for review
            setTimeout(() => {
                if (voiceTranscriptContainer) voiceTranscriptContainer.style.display = 'none';
                // Show type section with transcript ready
                const voiceSection = document.getElementById('voice-section');
                const typeSection = document.getElementById('type-section');
                if (voiceSection) voiceSection.style.display = 'none';
                if (typeSection) {
                    typeSection.style.display = 'block';
                    if (mainInput) mainInput.focus();
                }
            }, 2000);

        } catch (err) {
            console.error('Transcription error:', err);
            setVoiceStatus('Transcription failed: ' + err.message);
            alert('Transcription failed: ' + err.message);
        }
    }

    // ── Handle Audio File Upload ──────────────────────────────────────────
    function handleAudioUpload(input) {
        const file = input.files[0];
        if (!file) return;

        // Show filename
        if (audioUploadName) {
            audioUploadName.textContent = file.name;
            audioUploadName.style.display = 'inline';
        }

        // Validate file type
        const validTypes = ['audio/webm', 'audio/mp4', 'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/x-wav'];
        const isValidType = validTypes.some(t => file.type.startsWith(t)) ||
                           /\.(webm|mp4|mp3|wav|ogg|m4a)$/i.test(file.name);

        if (!isValidType) {
            alert('Unsupported audio format. Please use WebM, MP4, MP3, WAV, OGG, or M4A.');
            if (audioUploadName) audioUploadName.style.display = 'none';
            input.value = '';
            return;
        }

        // Upload file
        const formData = new FormData();
        formData.append('audio', file);

        if (voiceStatus) voiceStatus.textContent = 'Uploading and transcribing...';

        fetch('/api/transcribe', {
            method: 'POST',
            body: formData
        })
        .then(resp => resp.json())
        .then(result => {
            if (result.error && !result.transcript) {
                throw new Error(result.error);
            }

            const transcript = result.transcript || '';
            if (voiceFinalText) voiceFinalText.textContent = transcript;
            if (voiceInterimText) voiceInterimText.textContent = '';
            setTranscriptUI(true);

            const fillerCount = result.filler_count || 0;
            const fillerWords = result.filler_words || {};
            setFillerWarning(fillerCount, fillerWords);

            if (mainInput && transcript) {
                mainInput.value = transcript;
                mainInput.style.height = 'auto';
                mainInput.style.height = Math.min(mainInput.scrollHeight, 150) + 'px';
            }

            if (sendBtn) sendBtn.disabled = false;
            setVoiceStatus('Transcription complete ✓');

            setTimeout(() => {
                if (voiceTranscriptContainer) voiceTranscriptContainer.style.display = 'none';
                const voiceSection = document.getElementById('voice-section');
                const typeSection = document.getElementById('type-section');
                if (voiceSection) voiceSection.style.display = 'none';
                if (typeSection) {
                    typeSection.style.display = 'block';
                    if (mainInput) mainInput.focus();
                }
            }, 2000);

        })
        .catch(err => {
            console.error('Upload transcription error:', err);
            setVoiceStatus('Transcription failed: ' + err.message);
            alert('Transcription failed: ' + err.message);
        });
    }

    // ── Toggle Voice Recording ────────────────────────────────────────────
    window.toggleVoiceRecording = function() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    // Expose handleAudioUpload globally for inline onchange
    window.handleAudioUpload = handleAudioUpload;

    // ── Initialize ────────────────────────────────────────────────────────
    function init() {
        // Check if voice elements exist (only on interview page)
        if (!voiceBtn) return;

        // Check browser support for MediaRecorder
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
            // Browser doesn't support recording - hide voice section, show type section
            const voiceSection = document.getElementById('voice-section');
            const typeSection = document.getElementById('type-section');
            const unsupported = document.getElementById('voice-unsupported');
            if (voiceSection) voiceSection.style.display = 'none';
            if (typeSection) typeSection.style.display = 'block';
            if (unsupported) unsupported.style.display = 'block';
            return;
        }

        // Initialize voice button with idle state
        voiceBtn.classList.add('idle');

        // Wire audio upload input
        if (audioUpload) {
            audioUpload.addEventListener('change', function() {
                handleAudioUpload(this);
            });
        }

        console.log('[AudioInput] Initialized - MediaRecorder supported');
    }

    // Run init on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();