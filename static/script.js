/**
 * AI Interview Intelligence System - Frontend Logic
 * Handles registration, interview chat, dashboard, camera, round progress, and report interactions.
 */

// ── Helper Utilities ─────────────────────────────────────────────────────────

function $(selector) {
    return document.querySelector(selector);
}

function $$(selector) {
    return document.querySelectorAll(selector);
}

function showElement(el) {
    if (typeof el === 'string') el = $(el);
    if (el) el.classList.remove('hidden');
}

function hideElement(el) {
    if (typeof el === 'string') el = $(el);
    if (el) el.classList.add('hidden');
}

function showError(msg, target) {
    const el = typeof target === 'string' ? $(target) : target;
    if (el) {
        el.innerHTML = '<div class="alert alert-error">' + escapeHtml(msg) + '</div>';
        el.classList.remove('hidden');
    }
}

function showSuccess(msg, target) {
    const el = typeof target === 'string' ? $(target) : target;
    if (el) {
        el.innerHTML = '<div class="alert alert-success">' + escapeHtml(msg) + '</div>';
        el.classList.remove('hidden');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getScoreClass(score) {
    if (score >= 8) return 'score-excellent';
    if (score >= 6) return 'score-good';
    return 'score-average';
}

function getDifficultyClass(difficulty) {
    return 'difficulty-badge ' + (difficulty || 'medium').toLowerCase();
}


// ── Registration Page ────────────────────────────────────────────────────────

function initRegistrationForm() {
    const form = $('#registration-form');
    if (!form) return;

    const fileInput = $('#resume-file');
    const fileNameDisplay = $('#file-name');
    const skillsContainer = $('#skills-display');
    const submitBtn = $('#submit-btn');
    const errorContainer = $('#error-msg');
    const modeOptions = $$('.mode-option');

    // Mode selection
    let selectedMode = 'technical';
    modeOptions.forEach(opt => {
        opt.addEventListener('click', function() {
            modeOptions.forEach(o => o.classList.remove('selected'));
            this.classList.add('selected');
            selectedMode = this.dataset.mode || 'technical';
        });
    });

    // File upload display
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileNameDisplay.textContent = this.files[0].name;
                fileNameDisplay.classList.remove('hidden');
            } else {
                fileNameDisplay.classList.add('hidden');
            }
        });
    }

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        hideElement(errorContainer);
        submitBtn.disabled = true;
        submitBtn.textContent = 'Registering...';

        const formData = new FormData(form);
        formData.append('mode', selectedMode);

        try {
            const resp = await fetch('/register', {
                method: 'POST',
                body: formData,
            });

            const data = await resp.json();

            if (!resp.ok) {
                showError(data.error || 'Registration failed', errorContainer);
                submitBtn.disabled = false;
                submitBtn.textContent = 'Start Interview';
                return;
            }

            // Show success with skills
            showSuccess(
                data.message || 'Registration successful!',
                errorContainer
            );

            // Display identified skills
            if (skillsContainer && data.skills && data.skills.length > 0) {
                skillsContainer.innerHTML = data.skills.map(s =>
                    '<span class="skill-tag">' + escapeHtml(s) + '</span>'
                ).join('');
            }

            // Redirect to interview after brief delay
            setTimeout(() => {
                window.location.href = '/interview?mode=' + selectedMode;
            }, 1500);

        } catch (err) {
            showError('Network error: ' + err.message, errorContainer);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Start Interview';
        }
    });

    // Ollama status check
    checkOllamaStatus();
}

async function checkOllamaStatus() {
    const statusEl = $('#ollama-status');
    if (!statusEl) return;

    try {
        const resp = await fetch('/api/ollama_status');
        const data = await resp.json();

        if (data.status === 'connected' && data.model_available) {
            statusEl.innerHTML = '<span style="color:var(--accent-emerald);">&#x25CF;</span> ' +
                escapeHtml(data.model_name) + ' ready';
        } else if (data.status === 'connected') {
            statusEl.innerHTML = '<span style="color:var(--accent-amber);">&#x25CF;</span> ' +
                'Model not found. Run: ollama pull llama3.2:latest';
        } else {
            statusEl.innerHTML = '<span style="color:var(--accent-rose);">&#x25CF;</span> ' +
                'Ollama not connected. Ensure ollama serve is running.';
        }
    } catch {
        statusEl.innerHTML = '<span style="color:var(--accent-rose);">&#x25CF;</span> ' +
            'Cannot reach server';
    }
}


// ── Camera Module ────────────────────────────────────────────────────────────

let cameraStream = null;
let cameraActive = false;

function toggleCamera() {
    const video = $('#camera-feed');
    const overlay = $('#camera-overlay');
    const toggleBtn = $('#camera-toggle-btn');

    console.log('[Camera] toggleCamera() called. cameraActive =', cameraActive);

    if (!video) {
        console.error('[Camera] Video element #camera-feed not found in DOM');
        alert('Camera error: video element not found in the page. Has the page loaded correctly?');
        return;
    }

    if (cameraActive) {
        // Turn camera OFF
        console.log('[Camera] Stopping camera stream...');
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => {
                console.log('[Camera] Stopping track:', track.kind, track.label);
                track.stop();
            });
            cameraStream = null;
        }
        video.srcObject = null;
        cameraActive = false;
        if (overlay) overlay.classList.remove('hidden');
        if (toggleBtn) toggleBtn.innerHTML = '&#x1f4f7; Turn Camera On';
        console.log('[Camera] Camera turned OFF');
        return;
    }

    // Turn camera ON
    console.log('[Camera] Requesting camera access (getUserMedia)...');

    // Check if video element has required attributes
    if (!video.hasAttribute('playsinline')) {
        console.warn('[Camera] video element missing playsinline attribute');
        video.setAttribute('playsinline', '');
    }
    if (!video.hasAttribute('autoplay')) {
        console.warn('[Camera] video element missing autoplay attribute');
        video.setAttribute('autoplay', '');
    }

    const constraints = {
        video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user'
        },
        audio: false
    };

    console.log('[Camera] Constraints:', JSON.stringify(constraints));

    navigator.mediaDevices.getUserMedia(constraints)
        .then(function(stream) {
            console.log('[Camera] getUserMedia succeeded. Stream tracks:', stream.getTracks().length);
            console.log('[Camera] Video track:', stream.getVideoTracks()[0]?.label || 'none');

            cameraStream = stream;
            video.srcObject = stream;

            console.log('[Camera] Waiting for video to start playing...');

            video.onplaying = function() {
                console.log('[Camera] Video element is NOW PLAYING. ReadyState:', video.readyState);
                cameraActive = true;
                if (overlay) overlay.classList.add('hidden');
                if (toggleBtn) toggleBtn.innerHTML = '&#x1f6ab; Turn Camera Off';
            };

            video.onerror = function(e) {
                console.error('[Camera] Video element error:', e);
                alert('Camera error: video element encountered an error during playback.');
            };

            video.play().then(function() {
                console.log('[Camera] video.play() resolved successfully');
            }).catch(function(err) {
                console.error('[Camera] video.play() failed:', err.name, err.message);
                alert('Camera error: video playback failed - ' + err.name + ': ' + err.message);
            });
        })
        .catch(function(err) {
            console.error('[Camera] getUserMedia FAILED');
            console.error('[Camera] Error name:', err.name);
            console.error('[Camera] Error message:', err.message);
            console.error('[Camera] Full error:', JSON.stringify(err, Object.getOwnPropertyNames(err)));

            let errorMsg = err.name + ': ' + err.message;
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                errorMsg += ' (Camera permission denied. Check browser settings and ensure no other app is using the camera.)';
            } else if (err.name === 'NotFoundError') {
                errorMsg += ' (No camera found on this device.)';
            } else if (err.name === 'NotReadableError') {
                errorMsg += ' (Camera is busy. Close other apps/tabs using the camera.)';
            } else if (err.name === 'OverconstrainedError') {
                errorMsg += ' (Camera does not meet required constraints.)';
            } else if (err.name === 'TypeError') {
                errorMsg += ' (Invalid constraints. Check getUserMedia parameters.)';
            }

            alert('Camera error: ' + errorMsg);
        });
}

// Initialize camera on page load for interview pages
function initCamera() {
    const video = $('#camera-feed');
    if (!video) {
        console.log('[Camera] No camera video element found on this page - skipping camera init');
        return;
    }

    console.log('[Camera] Camera element found. Checking browser compatibility...');

    // Check getUserMedia availability
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('[Camera] getUserMedia not supported in this browser');
        alert('Camera error: Your browser does not support camera access (getUserMedia not available). Try Chrome, Firefox, or Edge.');
        return;
    }

    console.log('[Camera] getUserMedia is available. Camera ready for toggle.');

    // Ensure video element has correct attributes
    if (!video.hasAttribute('playsinline')) {
        video.setAttribute('playsinline', '');
    }
    if (!video.hasAttribute('autoplay')) {
        video.setAttribute('autoplay', '');
    }
    video.muted = true;

    // Wire toggleCamera to button if it exists
    const toggleBtn = $('#camera-toggle-btn');
    if (toggleBtn) {
        console.log('[Camera] Camera toggle button found, onclick should call toggleCamera()');
        // Remove old onclick and re-attach to avoid duplicates
        toggleBtn.onclick = function(e) {
            e.preventDefault();
            toggleCamera();
        };
    }
}


// ── Interview Page ───────────────────────────────────────────────────────────

function initInterview() {
    const messagesContainer = $('#messages');
    const inputField = $('#answer-input');
    const sendBtn = $('#send-btn');
    const progressFill = $('#progress-fill');
    const progressText = $('#progress-text');
    const roundText = $('#round-text');
    const currentDifficultyEl = $('#current-difficulty');
    const sidebarScores = $('#sidebar-scores');
    const roundStepper = $('#round-stepper');
    const roundFocusBanner = $('#round-focus-banner');
    const roundFocusText = $('#round-focus-text');
    const currentRoundBadge = $('#current-round-badge');

    if (!messagesContainer) return;

    let sessionId = null;
    let isProcessing = false;
    let interviewComplete = false;
    let totalScores = { overall: 0, technical: 0, communication: 0, confidence: 0 };
    let answerCount = 0;
    let evaluatedAnswersCount = 0;

    // Company state (for context badges)
    let currentCompany = '';
    let currentCompanyLabel = '';

    // Round state
    let roundsData = [];
    let currentRoundIndex = 0;
    let totalRounds = 0;
    let isResumePhase = true;

    // Aptitude state
    let isAptitudeRound = false;
    let aptitudeSelectedOption = -1;
    let aptitudeTimerInterval = null;
    let aptitudeTimeLeft = 45;
    let aptitudeCorrect = 0;
    let aptitudeTotal = 0;
    let aptitudeCurrentOptions = [];

    // Voice/Speech state
    let voiceRecognition = null;
    let voiceIsRecording = false;
    let voiceFinalText = '';
    let voiceSilenceTimer = null;
    let voiceModeActive = true;  // Start in voice mode if supported

    // Initialize camera (if available)
    initCamera();

    // Initialize voice (if available) — wire voice button
    const voiceBtn = document.getElementById('voice-btn');
    if (voiceBtn) {
        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            // Supported — keep voice section visible, hide fallback
            const unsupported = document.getElementById('voice-unsupported');
            if (unsupported) unsupported.style.display = 'none';
            const voiceSection = document.getElementById('voice-section');
            if (voiceSection) voiceSection.style.display = 'block';
            const typeSection = document.getElementById('type-section');
            if (typeSection) typeSection.style.display = 'none';
            voiceModeActive = true;
        } else {
            // Not supported — show typing mode with note
            const voiceSection = document.getElementById('voice-section');
            if (voiceSection) voiceSection.style.display = 'none';
            const typeSection = document.getElementById('type-section');
            if (typeSection) typeSection.style.display = 'block';
            const unsupported = document.getElementById('voice-unsupported');
            if (unsupported) unsupported.style.display = 'block';
            voiceModeActive = false;
        }
    }

    // Start the interview
    startInterviewSession();

    async function startInterviewSession() {
        addAIMessage('Hello! I\'m your AI interviewer today. Let\'s begin...', '');

        try {
            const resp = await fetch('/api/start_interview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: window.INTERVIEW_MODE || 'technical',
                }),
            });

            const data = await resp.json();

            if (data.error) {
                addAIMessage('I apologize, but there was an error starting the interview: ' + data.error, '');
                return;
            }

            sessionId = data.session_id;

            // Store company info for context badges
            currentCompany = data.company || '';
            if (currentCompany && currentCompany !== 'General') {
                currentCompanyLabel = currentCompany;
            }

            // Store round data
            roundsData = data.rounds || [];
            currentRoundIndex = data.current_round_index || 0;
            totalRounds = data.total_rounds || 1;
            isResumePhase = data.is_resume_phase || false;

            // Render round stepper
            renderRoundStepper(roundsData, currentRoundIndex);

            // Show round focus banner
            if (data.current_round) {
                showRoundFocus(data.current_round, data.is_resume_phase);
            }

            // Update round badge
            updateRoundBadge(currentRoundIndex, totalRounds, data.current_round);

            // Display the first question
            setTimeout(() => {
                if (data.is_aptitude) {
                    // Aptitude round: show question + MCQ mode
                    isAptitudeRound = true;
                    aptitudeTotal = data.aptitude_total || 10;
                    aptitudeCorrect = 0;
                    aptitudeSelectedOption = -1;
                    addAIMessage(data.question, 'medium');
                    updateProgress(1, data.total_questions);
                    updateRoundProgress(0, 0, data.current_round);
                    switchToAptitudeMode(data.question);
                } else {
                    addAIMessage(data.question, data.difficulty || 'medium');
                    updateProgress(1, data.total_questions);
                    setDifficulty(data.difficulty || 'medium');
                    updateRoundProgress(0, 0, data.current_round);
                    enableInput(true);
                }
            }, 500);

        } catch (err) {
            addAIMessage('Connection error. Please check that the server is running.', '');
        }
    }

    // Send answer
    function submitAnswer() {
        if (isProcessing || interviewComplete) return;

        const answer = inputField.value.trim();
        if (!answer) return;

        // Disable input
        isProcessing = true;
        enableInput(false);

        // Display user message
        addUserMessage(answer);
        inputField.value = '';
        autoResizeInput();

        // Show typing indicator
        showTypingIndicator();

        // Send to server
        fetch('/api/submit_answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answer: answer }),
        })
        .then(resp => resp.json())
        .then(data => {
            removeTypingIndicator();

            if (data.error) {
                addAIMessage('Error: ' + data.error, '');
                isProcessing = false;
                enableInput(true);
                return;
            }

            // Show evaluation
            addEvaluationCard(data.evaluation);
            updateSidebarScores(data.evaluation);
            answerCount++;

            if (data.is_complete) {
                interviewComplete = true;
                updateProgress(data.progress.total, data.progress.total);

                setTimeout(() => {
                    addAIMessage(
                        data.completion.message ||
                        'Interview complete! Redirecting to your report...',
                        ''
                    );

                    // Mark all rounds complete in stepper
                    updateStepperOnCompletion();

                    setTimeout(() => {
                        window.location.href = data.completion.report_url ||
                            '/report/' + sessionId;
                    }, 2000);
                }, 1000);
                return;
            }

            // Handle round transition
            if (data.round_transition) {
                // Round is complete — show transition banner
                currentRoundIndex = data.current_round ?
                    (roundsData.findIndex(r => r.name === data.current_round.name) || currentRoundIndex + 1) :
                    currentRoundIndex + 1;

                // Render stepper with updated index
                renderRoundStepper(roundsData, currentRoundIndex);

                // Show transition message
                const trans = data.round_transition;
                addTransitionBanner(trans.message || 'Starting next round...');

                // Update round badge and focus
                if (data.current_round) {
                    showRoundFocus(data.current_round, false);
                    updateRoundBadge(currentRoundIndex, totalRounds, data.current_round);
                }

                // Update progress
                updateProgress(data.progress.current, data.progress.total);
                updateRoundProgress(0, data.round_progress.round_question_limit || 0, data.current_round);

                // ═══ Check if transitioning TO an aptitude round ═══
                const nextRoundIsAptitude = data.is_aptitude === true ||
                    (data.current_round && data.current_round.type === 'aptitude');
                if (nextRoundIsAptitude) {
                    isAptitudeRound = true;
                    aptitudeTotal = data.aptitude_total || 10;
                    // Show next question as MCQ after delay
                    setTimeout(() => {
                        if (data.next_question) {
                            addAIMessage(data.next_question, 'medium');
                            switchToAptitudeMode(data.next_question);
                        }
                        isProcessing = false;
                    }, 800);
                    return; // <-- return to prevent the default flow below
                }
            } else {
                // Same round continues
                updateProgress(data.progress.current, data.progress.total);

                if (data.round_progress) {
                    updateRoundProgress(
                        data.round_progress.round_question_count || 0,
                        data.round_progress.round_question_limit || 0,
                        data.current_round
                    );
                }
            }

            setDifficulty(data.difficulty || 'medium');

            // Show next question after a brief pause
            setTimeout(() => {
                if (data.next_question) {
                    addAIMessage(data.next_question, data.difficulty || 'medium');
                }
                isProcessing = false;
                enableInput(true);
                inputField.focus();
            }, 800);

        })
        .catch(err => {
            removeTypingIndicator();
            addAIMessage('Network error. Please check your connection.', '');
            isProcessing = false;
            enableInput(true);
        });
    }

    // Event listeners
    if (sendBtn) {
        sendBtn.addEventListener('click', submitAnswer);
    }

    // Wire fallback send button (when voice unsupported)
    const sendBtnFallback = document.getElementById('send-btn-fallback');
    if (sendBtnFallback) {
        sendBtnFallback.addEventListener('click', function() {
            const inputFallback = document.getElementById('answer-input-fallback');
            if (inputFallback) {
                inputField = inputFallback; // Point main inputField at fallback for submitAnswer
                submitAnswer();
            }
        });
    }
    const inputFallback = document.getElementById('answer-input-fallback');
    if (inputFallback) {
        inputFallback.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (sendBtnFallback && !sendBtnFallback.disabled) {
                    inputField = inputFallback;
                    submitAnswer();
                }
            }
        });
        inputFallback.addEventListener('input', autoResizeInput);
    }

    if (inputField) {
        inputField.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitAnswer();
            }
        });

        inputField.addEventListener('input', autoResizeInput);
    }

    // ── Round Progress UI Functions ──

    function getRoundIcon(roundName, roundType) {
        var name = (roundName || '').toLowerCase();
        var type = (roundType || '').toLowerCase();
        if (name.includes('resume') || name.includes('hr')) return '&#x1f4cb;';
        if (name.includes('aptitude') || type === 'aptitude') return '&#x1f4ca;';
        if (name.includes('technical') || type === 'technical') return '&#x1f4bb;';
        if (name.includes('coding') || type === 'coding') return '&#x2328;&#xfe0f;';
        if (name.includes('hr') || name.includes('behavioral')) return '&#x1f91d;';
        if (name.includes('system design')) return '&#x1f4e1;';
        return '&#x1f4ac;';
    }

    function renderRoundStepper(rounds, currentIdx) {
        if (!roundStepper || !rounds || rounds.length === 0) return;

        roundStepper.innerHTML = '';

        rounds.forEach(function(round, idx) {
            const item = document.createElement('div');
            item.className = 'stepper-item';
            if (idx < currentIdx) item.classList.add('completed');
            if (idx === currentIdx) item.classList.add('active');

            let statusClass = '';
            let statusIcon = '';

            if (idx < currentIdx) {
                statusClass = 'stepper-completed';
                statusIcon = '&#x2713;';
            } else if (idx === currentIdx) {
                statusClass = 'stepper-active';
                statusIcon = (idx + 1).toString();
            } else {
                statusClass = 'stepper-upcoming';
                statusIcon = (idx + 1).toString();
            }

            var roundName = round.name || 'Round ' + (idx + 1);
            var roundType = round.type || '';
            var isResume = round.is_resume_phase ? ' (Resume)' : '';
            var icon = getRoundIcon(roundName, roundType);

            var focusClass = '';
            var focusColor = 'var(--text-muted)';
            if (idx < currentIdx) { focusClass = 'completed-focus'; focusColor = 'var(--accent-emerald)'; }
            else if (idx === currentIdx) { focusClass = 'active-focus'; focusColor = 'var(--accent-indigo)'; }

            item.innerHTML =
                '<div class="stepper-indicator ' + statusClass + '">' +
                    statusIcon +
                '</div>' +
                '<div class="stepper-content">' +
                    '<div class="stepper-name">' +
                        '<span class="stepper-icon">' + icon + '</span>' +
                        '<span>' + escapeHtml(roundName) + escapeHtml(isResume) + '</span>' +
                    '</div>' +
                    '<div class="stepper-focus ' + focusClass + '">' +
                        escapeHtml(round.focus?.substring(0, 35) || '') +
                    '</div>' +
                '</div>';

            roundStepper.appendChild(item);
        });
    }

    function showRoundFocus(roundData, isResume) {
        if (!roundFocusBanner || !roundFocusText) return;

        if (roundData && roundData.focus) {
            var prefix = isResume ? '&#x1f4cb; Resume Discussion' : '&#x1f3af; ' + roundData.name;
            roundFocusText.innerHTML = prefix + ' &mdash; ' + escapeHtml(roundData.focus);
            roundFocusBanner.style.display = 'flex';
        } else {
            roundFocusBanner.style.display = 'none';
        }
    }

    function updateRoundBadge(roundIdx, totalR, roundData) {
        if (!currentRoundBadge) return;
        if (roundData && roundData.name) {
            currentRoundBadge.textContent = 'Round ' + (roundIdx + 1) + ': ' + roundData.name;
            currentRoundBadge.style.display = 'inline-flex';
        } else {
            currentRoundBadge.style.display = 'none';
        }
    }

    function updateRoundProgress(count, limit, roundData) {
        if (!roundText) return;
        let name = roundData?.name || 'Round ' + (currentRoundIndex + 1);
        roundText.textContent = name + ' (' + count + '/' + limit + ' questions)';
    }

    function updateStepperOnCompletion() {
        if (!roundStepper) return;
        $$('.stepper-item').forEach(function(item, idx) {
            item.classList.add('completed');
            item.classList.remove('active');
            var indicator = item.querySelector('.stepper-indicator');
            if (indicator) {
                indicator.className = 'stepper-indicator stepper-completed';
                indicator.innerHTML = '\u2713';
            }
        });
    }

    function addTransitionBanner(message) {
        if (!messagesContainer) return;
        const div = document.createElement('div');
        div.className = 'round-transition-banner';
        div.innerHTML = escapeHtml(message);
        messagesContainer.appendChild(div);
        scrollToBottom();
    }

    // ── Helper: Add AI message ──
    function addAIMessage(text, difficulty, companyContext) {
        const div = document.createElement('div');
        div.className = 'message ai';

        let metaHtml = '';
        if (difficulty) {
            metaHtml = '<span class="' + getDifficultyClass(difficulty) + '">' +
                       escapeHtml(difficulty) + '</span>';
        }

        // Extract Aptitude category header if embedded (e.g. **[Aptitude - Logical Reasoning]**)
        let aptCategoryBadge = '';
        const aptCatMatch = text.match(/[\*\_]*\[Aptitude\s*-\s*([^\]]+)\][\*\_]*/i);
        if (aptCatMatch) {
            aptCategoryBadge = '<div class="company-context-badge" style="background:rgba(99,102,241,0.15);border-color:rgba(99,102,241,0.3);color:var(--accent-indigo);">' +
                'Aptitude &bull; ' + escapeHtml(aptCatMatch[1]) +
                '</div>';
            text = text.replace(/[\*\_]*\[Aptitude\s*-\s*[^\]]+\][\*\_]*/gi, '');
        }

        // Company context badge
        let companyBadgeHtml = '';
        var contextMatch = text.match(/\*\[Context:\s*([^\]]+)\]/i);
        if (contextMatch) {
            companyBadgeHtml = '<div class="company-context-badge">' +
                escapeHtml(contextMatch[1]) +
                '</div>';
            text = text.replace(/\n?\*\[Context:[^\]]*\]/gi, '');
        } else if (companyContext) {
            companyBadgeHtml = '<div class="company-context-badge">' +
                escapeHtml(companyContext) +
                '</div>';
        } else if (currentCompanyLabel && currentCompanyLabel !== 'General') {
            companyBadgeHtml = '<div class="company-context-badge">' +
                escapeHtml(currentCompanyLabel) +
                '</div>';
        }

        // Strip remaining raw markdown bolding asterisks
        text = text.replace(/\*\*/g, '').trim();

        div.innerHTML =
            '<div class="message-avatar">&#x1f916;</div>' +
            '<div class="message-content">' +
                aptCategoryBadge +
                companyBadgeHtml +
                '<div class="message-bubble">' +
                escapeHtml(text) +
                '</div>' +
                '<div class="message-meta">AI Interviewer' +
                (metaHtml ? ' &#x00B7; ' + metaHtml : '') +
                '</div>' +
            '</div>';

        messagesContainer.appendChild(div);
        scrollToBottom();
    }

    // ── Helper: Add user message ──
    function addUserMessage(text) {
        if (!messagesContainer) return;
        const div = document.createElement('div');
        div.className = 'message user';
        div.innerHTML =
            '<div class="message-avatar">&#x1f464;</div>' +
            '<div class="message-content">' +
                '<div class="message-bubble">' +
                escapeHtml(text) +
                '</div>' +
                '<div class="message-meta">You</div>' +
            '</div>';

        messagesContainer.appendChild(div);
        scrollToBottom();
    }

    // ── Global Rewrite Editor ──────────────────────────────────────────
    window.openRewriteEditor = function(answerIndex, currentScore) {
        // Find the last user message for this answer index
        const userMsgs = document.querySelectorAll('.message.user');
        const targetMsg = userMsgs[userMsgs.length - 1]; // Last user message
        if (!targetMsg) return;

        // Create rewrite editor
        const editor = document.createElement('div');
        editor.className = 'rewrite-editor';
        editor.innerHTML =
            '<div class="rewrite-header">' +
                '<span class="rewrite-icon">\u270f\ufe0f</span>' +
                '<span class="rewrite-title">Rewrite Answer #' + (answerCount + 1) + '</span>' +
            '</div>' +
            '<div class="rewrite-original">' +
                '<strong>Original:</strong> Your answer above' +
            '</div>' +
            '<textarea class="form-textarea rewrite-textarea" placeholder="Write your improved answer here..." rows="3"></textarea>' +
            '<div class="rewrite-actions">' +
                '<button class="btn btn-primary btn-sm" onclick="submitRewrite(' + answerIndex + ', this)">' +
                'Submit Rewrite</button>' +
                '<button class="btn btn-secondary btn-sm" onclick="closeRewriteEditor(this)">Cancel</button>' +
            '</div>';

        messagesContainer.appendChild(editor);
        scrollToBottom();
        editor.querySelector('.rewrite-textarea').focus();
    };

    window.submitRewrite = function(answerIndex, btnEl) {
        const editor = btnEl.closest('.rewrite-editor');
        const textarea = editor.querySelector('.rewrite-textarea');
        const rewritten = textarea.value.trim();
        if (!rewritten) return;

        // Show loading
        btnEl.disabled = true;
        btnEl.textContent = 'Submitting...';

        fetch('/api/rewrite_answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answer_index: answerIndex, rewritten_answer: rewritten }),
        })
        .then(resp => resp.json())
        .then(data => {
            if (data.error) {
                alert('Rewrite error: ' + data.error);
                btnEl.disabled = false;
                btnEl.textContent = 'Submit Rewrite';
                return;
            }

            // Remove editor
            editor.remove();

            // Show rewrite result
            const resultDiv = document.createElement('div');
            resultDiv.className = 'rewrite-result';

            const imp = data.improvement || {};
            let deltaHtml = '<div class="rewrite-deltas">';
            for (const [key, val] of Object.entries(imp)) {
                const cls = val > 0 ? 'delta-up' : (val < 0 ? 'delta-down' : 'delta-neutral');
                const arrow = val > 0 ? '\u2191' : (val < 0 ? '\u2193' : '\u2192');
                deltaHtml += '<div class="' + cls + '">' +
                    key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) + ': ' +
                    '<span class="delta-value">' + (originalScores[key] || 0) + ' \u2192 ' + (rewriteScores[key] || 0) + ' (' + (val > 0 ? '+' : '') + val + ')</span>' +
                    '</div>';
            }
            deltaHtml += '</div>';

            resultDiv.innerHTML = '<div class="rewrite-success">' +
                deltaHtml +
                '<div class="rewrite-evaluation">' +
                    '<strong>New Evaluation:</strong><br>' +
                    (data.rewrite_evaluation ? (data.rewrite_evaluation.feedback || '') : '') +
                '</div>' +
            '</div>';

            messagesContainer.insertBefore(resultDiv, messagesContainer.lastChild);
            scrollToBottom();
        })
        .catch(err => {
            alert('Rewrite failed: ' + err.message);
            btnEl.disabled = false;
            btnEl.textContent = 'Submit Rewrite';
        });
    };

    window.closeRewriteEditor = function(btnEl) {
        const editor = btnEl.closest('.rewrite-editor');
        if (editor) editor.remove();
    };

    // ── Helper: Add evaluation card after answer ──
    function addEvaluationCard(evaluation) {
        if (!evaluation || !messagesContainer) return;

        const card = document.createElement('div');
        card.className = 'evaluation-card';

        const scores = [
            { label: 'Overall', key: 'overall_score', cls: 'value-indigo' },
            { label: 'Technical', key: 'technical_score', cls: 'value-emerald' },
            { label: 'Communication', key: 'communication_score', cls: 'value-amber' },
            { label: 'Confidence', key: 'confidence_score', cls: 'value-violet' },
            { label: 'Problem Solving', key: 'problem_solving_score', cls: 'value-indigo' },
            { label: 'Time Management', key: 'time_management_score', cls: 'value-emerald' },
            { label: 'Conceptual Clarity', key: 'conceptual_clarity_score', cls: 'value-amber' },
        ];

        let html = '<div class="eval-header"><span class="eval-title">Evaluation</span></div>';

        html += '<div class="score-bars">';
        scores.forEach(function(s) {
            var val = evaluation[s.key] || 0;
            var label = s.label;
            var colorClass = val >= 7 ? 'bg-emerald' : (val >= 5 ? 'bg-amber' : 'bg-violet');
            html += '<div class="bar-group">' +
                '<div class="bar-info"><span class="bar-label">' + label + '</span> <span class="bar-value ' + s.cls + '">' + val + '/10</span></div>' +
                '<div class="bar"><div class="bar-fill ' + colorClass + '" style="width:' + (val * 10) + '%;"></div></div>' +
            '</div>';
        });
        html += '</div>';

        if (evaluation.feedback) {
            html += '<div class="feedback-summary-box">' + escapeHtml(evaluation.feedback) + '</div>';
        }

        if (evaluation.improvement_tip) {
            html += '<div class="actionable-tip-box"><span class="tip-tag">Tip:</span> <p>' + escapeHtml(evaluation.improvement_tip) + '</p></div>';
        }

        var strengths = evaluation.strengths || [];
        var weaknesses = evaluation.weaknesses || [];
        if (strengths.length > 0 || weaknesses.length > 0) {
            html += '<div class="qa-critique-grid">';
            if (strengths.length > 0) {
                html += '<div class="critique-column strengths-col"><div class="critique-header">Strengths</div><ul class="critique-list">';
                strengths.forEach(function(s) { html += '<li>' + escapeHtml(s) + '</li>'; });
                html += '</ul></div>';
            }
            if (weaknesses.length > 0) {
                html += '<div class="critique-column weaknesses-col"><div class="critique-header">Areas to Improve</div><ul class="critique-list">';
                weaknesses.forEach(function(w) { html += '<li>' + escapeHtml(w) + '</li>'; });
                html += '</ul></div>';
            }
            html += '</div>';
        }

        var keywordsUsed = evaluation.keywords_used || [];
        var keywordsMissed = evaluation.keywords_missed || [];
        if (keywordsUsed.length > 0 || keywordsMissed.length > 0) {
            html += '<div class="keywords-analysis-block">';
            if (keywordsUsed.length > 0) {
                html += '<div class="keywords-list">';
                keywordsUsed.forEach(function(k) { html += '<span class="keyword-pill keyword-used">' + escapeHtml(k) + '</span>'; });
                html += '</div>';
            }
            if (keywordsMissed.length > 0) {
                html += '<div class="keywords-list" style="margin-top: 0.3rem;">';
                keywordsMissed.forEach(function(k) { html += '<span class="keyword-pill keyword-missed">' + escapeHtml(k) + '</span>'; });
                html += '</div>';
            }
            html += '</div>';
        }

        if (evaluation.ideal_answer) {
            html += '<div class="ideal-answer-box"><div class="ideal-answer-header">Ideal Answer</div><p>' + escapeHtml(evaluation.ideal_answer) + '</p></div>';
        }

        if (evaluation.filler_word_count > 0) {
            html += '<div class="filler-badge" style="display:inline-flex;">Filler words: ' + evaluation.filler_word_count + '</div>';
        }

        card.innerHTML = html;
        messagesContainer.appendChild(card);
        scrollToBottom();
    }

    // ── Helper: Add filler-word to sidebar after eval ──
    function addFillerWordToSidebar(evaluation) {
        if (!sidebarScores || !evaluation) return;
        const fillerCount = evaluation.filler_word_count || 0;
        if (fillerCount > 0) {
            const existingBadge = document.querySelector('.filler-badge');
            if (existingBadge) {
                existingBadge.textContent = '\u26a0\ufe0f ' + fillerCount + ' fillers';
            } else {
                const badge = document.createElement('div');
                badge.className = 'filler-badge';
                badge.innerHTML = '\u26a0\ufe0f ' + fillerCount + ' filler words';
                if (sidebarScores.parentNode) {
                    sidebarScores.parentNode.appendChild(badge);
                }
            }
        }
    }

    // ── Helper: Typing indicator ──
    function showTypingIndicator() {
        removeTypingIndicator();
        const div = document.createElement('div');
        div.className = 'typing-indicator';
        div.id = 'typing-indicator';
        div.innerHTML = '<div class="typing-dot"></div>' +
                        '<div class="typing-dot"></div>' +
                        '<div class="typing-dot"></div>';
        messagesContainer.appendChild(div);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const el = $('#typing-indicator');
        if (el) el.remove();
    }

    // ── Helper: Progress ──
    function updateProgress(current, total) {
        if (progressFill) {
            const pct = Math.min(100, (current / total) * 100);
            progressFill.style.width = pct + '%';
        }
        if (progressText) {
            progressText.textContent = 'Question ' + current + ' of ' + total;
        }
    }

    // ── Helper: Difficulty ──
    function setDifficulty(diff) {
        if (currentDifficultyEl) {
            currentDifficultyEl.textContent = diff ? diff.charAt(0).toUpperCase() + diff.slice(1) : 'Medium';
            currentDifficultyEl.className = getDifficultyClass(diff);
        }
    }

    // ── Helper: Sidebar scores ──
    function updateSidebarScores(eval) {
        if (!eval || !sidebarScores) return;

        totalScores.overall += (typeof eval.overall_score === 'number' ? eval.overall_score : 0);
        totalScores.technical += (typeof eval.technical_score === 'number' ? eval.technical_score : 0);
        totalScores.communication += (typeof eval.communication_score === 'number' ? eval.communication_score : 0);
        totalScores.confidence += (typeof eval.confidence_score === 'number' ? eval.confidence_score : 0);

        evaluatedAnswersCount++;

        const count = evaluatedAnswersCount;
        if (count <= 0) return;

        const avgOverall = (totalScores.overall / count).toFixed(1);
        const avgTech = (totalScores.technical / count).toFixed(1);
        const avgComm = (totalScores.communication / count).toFixed(1);
        const avgConf = (totalScores.confidence / count).toFixed(1);

        const overallColor = parseFloat(avgOverall) >= 7.0 ? 'var(--accent-emerald)' : (parseFloat(avgOverall) >= 5.0 ? 'var(--accent-amber)' : 'var(--accent-rose)');

        sidebarScores.innerHTML =
            '<div class="score-item"><span class="score-label">Overall</span>' +
            '<span class="score-value" style="color:' + overallColor + '">' + avgOverall + '</span></div>' +
            '<div class="score-item"><span class="score-label">Technical</span>' +
            '<span class="score-value">' + avgTech + '</span></div>' +
            '<div class="score-item"><span class="score-label">Communication</span>' +
            '<span class="score-value">' + avgComm + '</span></div>' +
            '<div class="score-item"><span class="score-label">Confidence</span>' +
            '<span class="score-value">' + avgConf + '</span></div>';
    }

    // ── Helper: Input ──
    function enableInput(enabled) {
        // Textarea in type mode
        if (inputField) inputField.disabled = !enabled;
        if (sendBtn) {
            sendBtn.disabled = !enabled;
            sendBtn.textContent = enabled ? 'Send' : '...';
        }
        // Fallback textarea (voice unsupported)
        const inputFallback = document.getElementById('answer-input-fallback');
        const sendFallback = document.getElementById('send-btn-fallback');
        if (inputFallback) inputFallback.disabled = !enabled;
        if (sendFallback) {
            sendFallback.disabled = !enabled;
            sendFallback.textContent = enabled ? 'Send' : '...';
        }
        // Voice send button
        const voiceSendBtn = document.getElementById('voice-send-btn');
        if (voiceSendBtn) voiceSendBtn.disabled = !enabled;
        // Voice mode toggle buttons
        const voiceModeSwitch = document.getElementById('voice-mode-switch');
        const typeModeSwitch = document.getElementById('type-mode-switch');
        if (voiceModeSwitch) voiceModeSwitch.disabled = !enabled;
        if (typeModeSwitch) typeModeSwitch.disabled = !enabled;
    }

    function autoResizeInput() {
        if (inputField) {
            inputField.style.height = 'auto';
            inputField.style.height = Math.min(inputField.scrollHeight, 150) + 'px';
        }
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}


// ═══════════════════════════════════════════════════════════════════════
// ── Aptitude Round Functions ─────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════════

function parseAptitudeQuestion(text) {
    if (!text) return { questionText: '', options: [] };

    // Clean out markdown bolding, context headers, and pattern tags
    let cleanedText = text
        .replace(/\*\[Context:\s*[^\]]+\]/gi, '')
        .replace(/[\*\_]*\[Aptitude\s*-\s*[^\]]+\][\*\_]*/gi, '')
        .replace(/^\s*\*\*|\*\*\s*$/g, '');

    const lines = cleanedText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    let questionParts = [];
    const options = [];

    for (const line of lines) {
        if (/^[Aa]\.\s*/.test(line)) {
            options.push(line.replace(/^[Aa]\.\s*/, '').replace(/\*\*/g, '').trim());
        } else if (/^[Bb]\.\s*/.test(line)) {
            options.push(line.replace(/^[Bb]\.\s*/, '').replace(/\*\*/g, '').trim());
        } else if (/^[Cc]\.\s*/.test(line)) {
            options.push(line.replace(/^[Cc]\.\s*/, '').replace(/\*\*/g, '').trim());
        } else if (/^[Dd]\.\s*/.test(line)) {
            options.push(line.replace(/^[Dd]\.\s*/, '').replace(/\*\*/g, '').trim());
        } else if (options.length === 0) {
            questionParts.push(line.replace(/\*\*/g, '').trim());
        }
    }

    const questionText = questionParts.join(' ').trim();
    return { questionText, options };
}


function switchToAptitudeMode(questionText) {
    isAptitudeRound = true;

    // Hide normal chat messages window so MCQ area displays cleanly
    const msgsContainer = document.getElementById('messages');
    if (msgsContainer) msgsContainer.style.display = 'none';

    // Hide normal input area
    const inputArea = document.getElementById('input-area');
    if (inputArea) inputArea.style.display = 'none';

    // Show aptitude area
    const aptArea = document.getElementById('aptitude-area');
    if (aptArea) aptArea.style.display = 'flex';

    // Show aptitude score section in sidebar
    const aptScoreSection = document.getElementById('aptitude-score-section');
    if (aptScoreSection) aptScoreSection.style.display = 'flex';

    // Show camera note
    const cameraNote = document.getElementById('camera-aptitude-note');
    if (cameraNote) cameraNote.style.display = 'block';

    // Disable camera toggle
    const camToggle = document.getElementById('camera-toggle-btn');
    if (camToggle) camToggle.disabled = true;

    // Reset selection
    aptitudeSelectedOption = -1;
    const submitBtn = document.getElementById('aptitude-submit-btn');
    if (submitBtn) submitBtn.disabled = true;

    // Remove any existing option selections
    document.querySelectorAll('.aptitude-option').forEach(el => {
        el.classList.remove('selected', 'correct', 'incorrect', 'disabled');
        el.style.pointerEvents = 'auto';
    });

    // Hide previous feedback
    const feedbackEl = document.getElementById('aptitude-feedback');
    if (feedbackEl) feedbackEl.style.display = 'none';

    // Parse question and populate
    const parsed = parseAptitudeQuestion(questionText);
    const questionEl = document.getElementById('aptitude-question-text');
    if (questionEl) questionEl.textContent = parsed.questionText || questionText.replace(/\*\*/g, '');

    aptitudeCurrentOptions = parsed.options;

    // Populate options
    for (let i = 0; i < 4; i++) {
        const optEl = document.getElementById('apt-opt-' + i);
        if (optEl) {
            optEl.textContent = parsed.options[i] || 'Option ' + (i + 1);
        }
    }

    // Update score display
    updateAptitudeScore();

    // Start timer
    startAptitudeTimer();
}


function switchToNormalMode() {
    isAptitudeRound = false;

    // Restore normal chat messages window
    const msgsContainer = document.getElementById('messages');
    if (msgsContainer) msgsContainer.style.display = 'flex';

    // Show normal input area
    const inputArea = document.getElementById('input-area');
    if (inputArea) inputArea.style.display = 'flex';

    // Hide aptitude area
    const aptArea = document.getElementById('aptitude-area');
    if (aptArea) aptArea.style.display = 'none';

    // Hide aptitude score section
    const aptScoreSection = document.getElementById('aptitude-score-section');
    if (aptScoreSection) aptScoreSection.style.display = 'none';

    // Hide camera note
    const cameraNote = document.getElementById('camera-aptitude-note');
    if (cameraNote) cameraNote.style.display = 'none';

    // Enable camera toggle
    const camToggle = document.getElementById('camera-toggle-btn');
    if (camToggle) camToggle.disabled = false;

    // Reset timer
    pauseAptitudeTimer();
}


function selectAptitudeOption(element, index) {
    if (!element) return;

    // Deselect all
    document.querySelectorAll('.aptitude-option').forEach(el => {
        el.classList.remove('selected');
    });

    // Select this one
    element.classList.add('selected');
    aptitudeSelectedOption = index;

    // Enable submit button
    const submitBtn = document.getElementById('aptitude-submit-btn');
    if (submitBtn) submitBtn.disabled = false;
}


function submitAptitudeAnswer() {
    if (aptitudeSelectedOption < 0) return;

    // Pause timer while server processes
    pauseAptitudeTimer();

    const submitBtn = document.getElementById('aptitude-submit-btn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Checking...';
    }

    // Disable all options during submission
    document.querySelectorAll('.aptitude-option').forEach(el => {
        el.style.pointerEvents = 'none';
    });

    // Show typing indicator / loading
    const aptArea = document.getElementById('aptitude-area');
    if (aptArea) aptArea.classList.add('aptitude-loading');

    fetch('/api/submit_aptitude_answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selected_option_index: aptitudeSelectedOption }),
    })
    .then(resp => resp.json())
    .then(data => {
        if (aptArea) aptArea.classList.remove('aptitude-loading');

        if (data.error) {
            console.error('Aptitude error:', data.error);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Answer \u2191';
            }
            document.querySelectorAll('.aptitude-option').forEach(el => {
                el.style.pointerEvents = 'auto';
            });
            return;
        }

        // Show feedback
        const isCorrect = data.evaluation && data.evaluation.is_correct;
        const explanation = data.evaluation && data.evaluation.explanation;
        const correctAnswer = data.evaluation && data.evaluation.correct_answer;

        // Highlight correct/incorrect on options
        document.querySelectorAll('.aptitude-option').forEach((el, idx) => {
            el.style.pointerEvents = 'none';
            el.classList.remove('selected');

            // Show which was the correct answer
            if (data.evaluation && idx === data.evaluation.correct_answer_index) {
                el.classList.add('correct');
            }
            // Show which option was selected (if wrong)
            if (!isCorrect && idx === aptitudeSelectedOption) {
                el.classList.add('incorrect');
            }
            // If correct, the selected one is also correct
            if (isCorrect && idx === aptitudeSelectedOption) {
                el.classList.add('correct');
            }
        });

        // Update score
        if (data.aptitude_progress) {
            aptitudeCorrect = data.aptitude_progress.correct;
            aptitudeTotal = data.aptitude_progress.total;
            updateAptitudeScore();
        }

        // Show flash feedback
        showAptitudeFeedback(isCorrect, explanation, correctAnswer);

        // Update progress
        if (data.progress) {
            const progressFill = document.getElementById('progress-fill');
            const progressText = document.getElementById('progress-text');
            if (progressFill) {
                const pct = Math.min(100, (data.progress.current / data.progress.total) * 100);
                progressFill.style.width = pct + '%';
            }
            if (progressText) {
                progressText.textContent = 'Question ' + data.progress.current + ' of ' + data.progress.total;
            }
        }

        if (submitBtn) {
            submitBtn.textContent = 'Submit Answer \u2191';
        }

        // Handle round transition or completion
        if (data.is_complete) {
            // Interview complete
            setTimeout(() => {
                const aptArea = document.getElementById('aptitude-area');
                if (aptArea) aptArea.style.display = 'none';
                const inputArea = document.getElementById('input-area');
                if (inputArea) inputArea.style.display = 'none';

                const messagesContainer = document.getElementById('messages');
                if (messagesContainer && data.completion) {
                    const div = document.createElement('div');
                    div.className = 'message ai';
                    div.innerHTML =
                        '<div class="message-avatar">&#x1f916;</div>' +
                        '<div class="message-content">' +
                            '<div class="message-bubble">' +
                            escapeHtml(data.completion.message || 'Interview complete!') +
                            '</div><div class="message-meta">AI Interviewer</div>' +
                        '</div>';
                    messagesContainer.appendChild(div);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }

                // Update stepper
                const stepperItems = document.querySelectorAll('.stepper-item');
                stepperItems.forEach(function(item) {
                    item.classList.add('completed');
                    item.classList.remove('active');
                    const indicator = item.querySelector('.stepper-indicator');
                    if (indicator) {
                        indicator.className = 'stepper-indicator stepper-completed';
                        indicator.innerHTML = '\u2713';
                    }
                });

                setTimeout(() => {
                    if (data.completion && data.completion.report_url) {
                        window.location.href = data.completion.report_url;
                    }
                }, 2000);
            }, 2500);
            return;
        }

        if (data.round_transition) {
            // Round transition — show transition banner then load next
            setTimeout(() => {
                const messagesContainer = document.getElementById('messages');
                if (messagesContainer && data.round_transition.message) {
                    const div = document.createElement('div');
                    div.className = 'round-transition-banner';
                    div.textContent = data.round_transition.message;
                    messagesContainer.appendChild(div);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }

                // Update stepper
                const stepperItems = document.querySelectorAll('.stepper-item');
                if (stepperItems.length > 0) {
                    const currentIdx = roundsData.findIndex(r =>
                        r.name === (data.current_round ? data.current_round.name : '')
                    );
                    renderRoundStepper(roundsData, currentIdx >= 0 ? currentIdx : currentRoundIndex + 1);
                }

                // Update round info
                if (data.current_round) {
                    if (typeof showRoundFocus === 'function') {
                        showRoundFocus(data.current_round, false);
                    }
                    if (typeof updateRoundBadge === 'function') {
                        updateRoundBadge(currentRoundIndex + 1, totalRounds, data.current_round);
                    }
                }

                // If next round is not aptitude, switch to normal mode
                if (data.current_round && data.current_round.type !== 'aptitude') {
                    switchToNormalMode();
                    const inputField = document.getElementById('answer-input');
                    const sendBtn = document.getElementById('send-btn');
                    if (inputField) inputField.disabled = false;
                    if (sendBtn) sendBtn.disabled = false;
                }

                // Show next question
                if (data.next_question) {
                    const messagesContainer = document.getElementById('messages');
                    if (messagesContainer) {
                        const div = document.createElement('div');
                        div.className = 'message ai';
                        div.innerHTML =
                            '<div class="message-avatar">&#x1f916;</div>' +
                            '<div class="message-content">' +
                                '<div class="message-bubble">' +
                                escapeHtml(data.next_question) +
                                '</div><div class="message-meta">AI Interviewer</div>' +
                            '</div>';
                        messagesContainer.appendChild(div);
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    }

                    // If next round is again aptitude, switch back to aptitude mode
                    if (data.current_round && data.current_round.type === 'aptitude') {
                        isAptitudeRound = true;
                        switchToAptitudeMode(data.next_question);
                    }
                }
            }, 2000);
            return;
        }

        // Same round continues — load next question after delay
        setTimeout(function() {
            // Show next question in chat
            if (data.next_question) {
                const messagesContainer = document.getElementById('messages');
                if (messagesContainer) {
                    const div = document.createElement('div');
                    div.className = 'message ai';
                    div.innerHTML =
                        '<div class="message-avatar">&#x1f916;</div>' +
                        '<div class="message-content">' +
                            '<div class="message-bubble">' +
                            escapeHtml(data.next_question) +
                            '</div><div class="message-meta">AI Interviewer</div>' +
                        '</div>';
                    messagesContainer.appendChild(div);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }

                // Switch to aptitude mode with new question
                switchToAptitudeMode(data.next_question);

                // Update round progress
                if (data.round_progress) {
                    const roundText = document.getElementById('round-text');
                    if (roundText) {
                        const name = data.current_round ? data.current_round.name : 'Aptitude Test';
                        roundText.textContent = name + ' (' +
                            data.round_progress.round_question_count + '/' +
                            data.round_progress.round_question_limit + ' questions)';
                    }
                }
            }
        }, 2500); // 2.5s delay between questions

    })
    .catch(err => {
        console.error('Aptitude submit error:', err);
        const aptArea = document.getElementById('aptitude-area');
        if (aptArea) aptArea.classList.remove('aptitude-loading');
        const submitBtn = document.getElementById('aptitude-submit-btn');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Answer \u2191';
        }
        document.querySelectorAll('.aptitude-option').forEach(el => {
            el.style.pointerEvents = 'auto';
        });
    });
}


function showAptitudeFeedback(isCorrect, explanation, correctAnswer) {
    const feedbackEl = document.getElementById('aptitude-feedback');
    const textEl = document.getElementById('aptitude-feedback-text');
    const explEl = document.getElementById('aptitude-feedback-explanation');

    if (!feedbackEl || !textEl) return;

    feedbackEl.style.display = 'block';
    feedbackEl.className = 'aptitude-feedback ' + (isCorrect ? 'feedback-correct' : 'feedback-incorrect');

    if (isCorrect) {
        textEl.innerHTML = '\u2705 <strong>Correct!</strong>';
    } else {
        textEl.innerHTML = '\u274c <strong>Incorrect.</strong> The correct answer was: ' +
            escapeHtml(correctAnswer || '');
    }

    if (explanation && explEl) {
        explEl.textContent = explanation;
        explEl.style.display = 'block';
    } else if (explEl) {
        explEl.style.display = 'none';
    }

    // Auto-hide after 2.5s (managed by callers)
}


function updateAptitudeScore() {
    const displayEl = document.getElementById('aptitude-score-display');
    if (displayEl) {
        const valueEl = displayEl.querySelector('.aptitude-score-value');
        if (valueEl) {
            valueEl.textContent = aptitudeCorrect + '/' + aptitudeTotal;
        }
    }
}


function startAptitudeTimer() {
    pauseAptitudeTimer(); // Clear any existing timer

    const timerEl = document.getElementById('aptitude-timer');
    if (!timerEl) return;

    aptitudeTimeLeft = 45;
    updateTimerDisplay();

    aptitudeTimerInterval = setInterval(function() {
        aptitudeTimeLeft--;
        updateTimerDisplay();

        if (aptitudeTimeLeft <= 0) {
            pauseAptitudeTimer();
            // Auto-submit (with whatever is selected, or -1)
            if (aptitudeSelectedOption >= 0) {
                submitAptitudeAnswer();
            } else {
                // No option selected — submit with -1 (counts as wrong)
                aptitudeSelectedOption = -1;
                submitAptitudeAnswer();
            }
        }
    }, 1000);
}


function pauseAptitudeTimer() {
    if (aptitudeTimerInterval) {
        clearInterval(aptitudeTimerInterval);
        aptitudeTimerInterval = null;
    }
}


function resetAptitudeTimer() {
    pauseAptitudeTimer();
    aptitudeTimeLeft = 45;
    updateTimerDisplay();
}


function updateTimerDisplay() {
    const timerEl = document.getElementById('aptitude-timer');
    if (!timerEl) return;

    const mins = Math.floor(aptitudeTimeLeft / 60);
    const secs = aptitudeTimeLeft % 60;
    timerEl.textContent = String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');

    // Color coding
    timerEl.className = 'aptitude-timer';
    if (aptitudeTimeLeft <= 10) {
        timerEl.classList.add('timer-critical');
    } else if (aptitudeTimeLeft <= 20) {
        timerEl.classList.add('timer-warning');
    }
}


// ═══════════════════════════════════════════════════════════════════════
// ── Voice/Speech Input Functions ─────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════════

let globalVoiceRecognition = null;
let globalVoiceIsRecording = false;
let globalVoiceFinalText = '';
let globalVoiceSilenceTimer = null;

function getSpeechRecognition() {
    return window.SpeechRecognition || window.webkitSpeechRecognition;
}

function toggleVoiceRecording() {
    if (globalVoiceIsRecording) {
        stopVoiceRecording();
    } else {
        startVoiceRecording();
    }
}

function startVoiceRecording() {
    const SpeechRecognition = getSpeechRecognition();
    if (!SpeechRecognition) {
        switchToTypeMode();
        return;
    }

    // Reset state
    globalVoiceFinalText = '';
    const finalEl = document.getElementById('voice-final-text');
    const interimEl = document.getElementById('voice-interim-text');
    if (finalEl) finalEl.textContent = '';
    if (interimEl) interimEl.textContent = '';

    // Update button UI
    const btn = document.getElementById('voice-btn');
    const icon = document.getElementById('voice-btn-icon');
    const text = document.getElementById('voice-btn-text');
    if (icon) icon.innerHTML = '\u23f9'; // ⏹
    if (text) text.textContent = 'Stop Recording';
    if (btn) {
        btn.classList.add('recording');
        btn.classList.remove('idle');
    }

    // Show transcript area
    const transcriptContainer = document.getElementById('voice-transcript-container');
    if (transcriptContainer) transcriptContainer.style.display = 'block';

    const statusEl = document.getElementById('voice-status');
    if (statusEl) statusEl.textContent = 'Listening...';

    globalVoiceIsRecording = true;

    // Create recognition instance
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = function(event) {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            if (result.isFinal) {
                finalTranscript += result[0].transcript;
                // Track word count for metrics
                if (window.__answerWordCount === undefined) window.__answerWordCount = 0;
                window.__answerWordCount += result[0].transcript.split(/\s+/).filter(w => w).length;
            } else {
                interimTranscript += result[0].transcript;
            }
        }

        if (finalTranscript) {
            globalVoiceFinalText += (globalVoiceFinalText ? ' ' : '') + finalTranscript.trim();
            const finalEl = document.getElementById('voice-final-text');
            if (finalEl) finalEl.textContent = globalVoiceFinalText;
        }

        const interimEl = document.getElementById('voice-interim-text');
        if (interimEl) interimEl.textContent = interimTranscript;

        // Reset silence timer on each speech
        clearTimeout(globalVoiceSilenceTimer);
        globalVoiceSilenceTimer = setTimeout(function() {
            // 3 seconds of silence → auto-stop
            if (globalVoiceIsRecording) {
                stopVoiceRecording();
            }
        }, 3000);
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        const statusEl = document.getElementById('voice-status');
        if (statusEl) statusEl.textContent = 'Error: ' + event.error;

        // Only stop for fatal errors
        if (event.error !== 'no-speech' && event.error !== 'aborted') {
            stopVoiceRecording();
        }
    };

    recognition.onend = function() {
        // If still flagged as recording, restart (handles continuous)
        if (globalVoiceIsRecording) {
            try {
                recognition.start();
            } catch (e) {
                console.log('Could not restart speech recognition:', e);
                stopVoiceRecording();
            }
        }
    };

    // Start recognition
    try {
        recognition.start();
    } catch (e) {
        console.error('Could not start speech recognition:', e);
        stopVoiceRecording();
        return;
    }

    globalVoiceRecognition = recognition;
}

function stopVoiceRecording() {
    clearTimeout(globalVoiceSilenceTimer);
    globalVoiceSilenceTimer = null;

    if (globalVoiceRecognition) {
        try {
            globalVoiceRecognition.stop();
        } catch (e) {
            // Ignore errors on stop
        }
        globalVoiceRecognition = null;
    }

    globalVoiceIsRecording = false;

    // Update button UI
    const btn = document.getElementById('voice-btn');
    const icon = document.getElementById('voice-btn-icon');
    const text = document.getElementById('voice-btn-text');
    if (icon) icon.innerHTML = '\uD83C\uDF99'; // 🎙
    if (text) text.textContent = 'Speak Your Answer';
    if (btn) {
        btn.classList.remove('recording');
        btn.classList.add('idle');
    }

    const statusEl = document.getElementById('voice-status');
    if (statusEl) {
        if (globalVoiceFinalText.trim()) {
            statusEl.textContent = 'Done \u2705  (review and send below)';
        } else {
            statusEl.textContent = 'No speech detected';
        }
    }

    // Move finalized transcript into the type-mode textarea for review
    if (globalVoiceFinalText.trim()) {
        const mainInput = document.getElementById('answer-input');
        if (mainInput) {
            mainInput.value = globalVoiceFinalText.trim();
            // Auto-resize
            mainInput.style.height = 'auto';
            mainInput.style.height = Math.min(mainInput.scrollHeight, 150) + 'px';
        }
        // Show type section with transcript ready for editing
        const voiceSection = document.getElementById('voice-section');
        if (voiceSection) voiceSection.style.display = 'none';
        const typeSection = document.getElementById('type-section');
        if (typeSection) typeSection.style.display = 'block';

        // Auto-submit after brief delay (so user sees transcript)
        setTimeout(() => {
            if (mainInput && mainInput.value.trim()) {
                // Find submitAnswer in the current scope
                if (typeof submitAnswer === 'function') {
                    submitAnswer();
                }
            }
        }, 1200);
    }

    // Hide transcript container after delay
    setTimeout(() => {
        const transcriptContainer = document.getElementById('voice-transcript-container');
        if (transcriptContainer) transcriptContainer.style.display = 'none';
    }, 2000);
}

function switchToTypeMode() {
    // Stop any active recording
    if (globalVoiceIsRecording) {
        stopVoiceRecording();
    }

    const voiceSection = document.getElementById('voice-section');
    const typeSection = document.getElementById('type-section');
    const unsupported = document.getElementById('voice-unsupported');

    if (voiceSection) voiceSection.style.display = 'none';
    if (typeSection) typeSection.style.display = 'block';
    if (unsupported) unsupported.style.display = 'none';

    // If there was transcribed text, carry it over
    if (globalVoiceFinalText.trim()) {
        const mainInput = document.getElementById('answer-input');
        if (mainInput) {
            mainInput.value = globalVoiceFinalText.trim();
            mainInput.style.height = 'auto';
            mainInput.style.height = Math.min(mainInput.scrollHeight, 150) + 'px';
        }
    }

    const mainInput = document.getElementById('answer-input');
    if (mainInput) {
        mainInput.focus();
        mainInput.disabled = false;
    }
}

function switchToVoiceMode() {
    const voiceSection = document.getElementById('voice-section');
    const typeSection = document.getElementById('type-section');
    const unsupported = document.getElementById('voice-unsupported');

    if (typeSection) typeSection.style.display = 'none';
    if (unsupported) unsupported.style.display = 'none';
    if (voiceSection) {
        voiceSection.style.display = 'block';
        // Add idle animation
        const btn = document.getElementById('voice-btn');
        if (btn) btn.classList.add('idle');
    }
}


// ── Wire aptitude submit button globally ──
document.addEventListener('DOMContentLoaded', function() {
    const aptSubmitBtn = document.getElementById('aptitude-submit-btn');
    if (aptSubmitBtn) {
        aptSubmitBtn.addEventListener('click', function() {
            if (!this.disabled) {
                submitAptitudeAnswer();
            }
        });
    }
});


// ── Dashboard Page ───────────────────────────────────────────────────────────

function initDashboard() {
    // Staggered entrance for stat cards
    const statCards = $$('.stat-card');
    statCards.forEach(function(card, i) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(12px)';
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        setTimeout(function() {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + i * 100);
    });

    // Animate bar fills
    const barFills = $$('.bar-fill');
    setTimeout(() => {
        barFills.forEach(bar => {
            const target = bar.dataset.height || 0;
            bar.style.height = target + '%';
        });
    }, 200);

    // Load Chart.js from CDN and initialize progress chart
    initProgressChart();
}

async function initProgressChart() {
    const canvas = $('#progress-chart');
    if (!canvas) return;

    try {
        const resp = await fetch('/api/progress/' + (window.CANDIDATE_ID || 0));
        if (!resp.ok) return;
        const data = await resp.json();
        if (!data.labels || data.labels.length < 1) return;

        // Dynamically load Chart.js
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js';
        script.onload = function() {
            const ctx = canvas.getContext('2d');

            // Prepare datasets
            const chartDatasets = [
                { label: 'Overall', data: data.datasets.overall, borderColor: '#6366f1', backgroundColor: 'rgba(99,102,241,0.1)', fill: true, tension: 0.3 },
                { label: 'Technical', data: data.datasets.technical, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.05)', tension: 0.3 },
                { label: 'Communication', data: data.datasets.communication, borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,0.05)', tension: 0.3 },
                { label: 'Confidence', data: data.datasets.confidence, borderColor: '#8b5cf6', backgroundColor: 'rgba(139,92,246,0.05)', tension: 0.3 },
            ];

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: chartDatasets,
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { intersect: false, mode: 'index' },
                    plugins: {
                        legend: {
                            labels: { color: '#8b949e', font: { size: 11 } }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#6e7681' },
                            grid: { color: '#30363d' }
                        },
                        y: {
                            min: 0, max: 10,
                            ticks: { color: '#6e7681', stepSize: 2 },
                            grid: { color: '#30363d' }
                        }
                    }
                }
            });
        };
        document.head.appendChild(script);
    } catch (e) {
        // Chart.js failed to load, silently skip
    }
}


// ── Report Page ──────────────────────────────────────────────────────────────

function initReport() {
    // Staggered fade-in for cards
    const cards = $$('.card');
    cards.forEach(function(card, i) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(15px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        setTimeout(function() {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + i * 80);
    });

    // Animate distribution bars
    const distFills = $$('.dist-fill');
    setTimeout(() => {
        distFills.forEach(fill => {
            const target = fill.dataset.width || 0;
            fill.style.width = target + '%';
        });
    }, 300);

    // Animate SVG circular progress ring
    animateScoreRing();

    // Animate readability bar
    const readinessFill = $('.readiness-fill');
    if (readinessFill) {
        setTimeout(() => {
            readinessFill.style.width = readinessFill.dataset.width || '0%';
        }, 500);
    }

    // Animate score detail bars
    setTimeout(() => {
        $$('.score-detail-bar .bar-fill').forEach(bar => {
            bar.style.width = bar.dataset.width || '0%';
        });
    }, 400);

    // Copy report link button
    const copyBtn = $('#copy-report-link');
    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            navigator.clipboard.writeText(window.location.href).then(() => {
                const orig = this.innerHTML;
                this.innerHTML = '&#x2705; Copied!';
                this.classList.add('btn-primary');
                setTimeout(() => { this.innerHTML = orig; this.classList.remove('btn-primary'); }, 2000);
            });
        });
    }
}

function animateScoreRing() {
    const ring = $('.ring-progress');
    if (!ring) return;
    const score = parseFloat(ring.dataset.score || 0);
    const circumference = 2 * Math.PI * 70; // r=70
    const offset = circumference * (1 - score / 10);
    ring.style.strokeDasharray = circumference;
    ring.style.strokeDashoffset = circumference; // Start hidden
    // Trigger animation after render
    setTimeout(() => {
        ring.style.strokeDashoffset = offset;
    }, 200);
}


// ── Initialize on Page Load ──────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function() {
    // Detect page type from body class
    const body = document.body;

    if (body.classList.contains('page-register')) {
        initRegistrationForm();
    } else if (body.classList.contains('page-interview')) {
        initInterview();
    } else if (body.classList.contains('page-dashboard')) {
        initDashboard();
    } else if (body.classList.contains('page-report')) {
        initReport();
    }
});
