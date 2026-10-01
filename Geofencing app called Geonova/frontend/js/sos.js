// Geonova Emergency SOS System

class SOSManager {
    constructor() {
        this.countdownTimer = null;
        this.countdownSeconds = 3;
        this.selectedCategory = 'Medical emergency';
        this.isSirenPlaying = false;
        this.audioCtx = null;
        this.sirenOsc = null;
        this.sirenGain = null;
        this.sirenInterval = null;
    }

    openSOSModal() {
        const modal = document.getElementById('sos-modal');
        if (!modal) return;

        // Render Step 1: Confirmation with Countdown
        this.renderCountdownStep();
        modal.classList.add('open');
    }

    renderCountdownStep() {
        const container = document.getElementById('sos-modal-content');
        this.countdownSeconds = 3;
        const t = (k, fb) => (window.i18n ? window.i18n.getText(k) : fb);

        container.innerHTML = `
            <div style="text-align: center; padding: 1.5rem 1rem;">
                <div style="width: 84px; height: 84px; border-radius: 50%; background: var(--grad-sos); display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; box-shadow: 0 0 30px var(--sos-crimson-glow); animation: pulse-border 1.5s infinite;">
                    <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                </div>

                <h2 style="font-size: 1.85rem; color: #ffffff; margin-bottom: 0.5rem;">${t('sos_countdown_title', 'Emergency SOS Trigger')}</h2>
                <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1.5rem;">
                    ${t('sos_countdown_subtitle', 'Accidental activation check. Dispatching emergency mode in...')}
                </p>

                <div id="sos-countdown-display" style="font-size: 4rem; font-weight: 800; font-family: 'Outfit', sans-serif; color: #ef4444; margin-bottom: 1.5rem;">
                    3
                </div>

                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <button class="btn btn-outline btn-lg" onclick="sosManager.cancelSOS()">
                        ${t('sos_btn_cancel', 'Cancel Activation')}
                    </button>
                    <button class="btn btn-sos btn-lg" onclick="sosManager.proceedImmediately()">
                        ${t('sos_btn_activate', 'Activate Now')}
                    </button>
                </div>
            </div>
        `;

        this.countdownTimer = setInterval(() => {
            this.countdownSeconds--;
            const display = document.getElementById('sos-countdown-display');
            if (display) display.textContent = this.countdownSeconds;

            if (this.countdownSeconds <= 0) {
                clearInterval(this.countdownTimer);
                this.renderActiveSOSView();
            }
        }, 1000);
    }

    cancelSOS() {
        if (this.countdownTimer) clearInterval(this.countdownTimer);
        this.stopSiren();
        const modal = document.getElementById('sos-modal');
        if (modal) modal.classList.remove('open');
        window.showToast('Emergency SOS activation aborted.', 'info');
    }

    proceedImmediately() {
        if (this.countdownTimer) clearInterval(this.countdownTimer);
        this.renderActiveSOSView();
    }

    renderActiveSOSView() {
        const container = document.getElementById('sos-modal-content');
        const lat = (window.mapManager && window.mapManager.currentCoords) ? window.mapManager.currentCoords.lat : 28.6139;
        const lng = (window.mapManager && window.mapManager.currentCoords) ? window.mapManager.currentCoords.lng : 77.2090;
        const t = (k, fb) => (window.i18n ? window.i18n.getText(k) : fb);

        container.innerHTML = `
            <div style="padding: 1rem 0;">
                <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--navy-border); padding-bottom: 1rem; margin-bottom: 1.5rem;">
                    <div>
                        <span class="badge badge-crimson" style="font-size: 0.8rem; padding: 0.3rem 0.8rem;">${t('sos_active_badge', '● Emergency Mode Active')}</span>
                        <h3 style="font-size: 1.5rem; color: #ffffff; margin-top: 0.4rem;">${t('sos_choose_type', 'Select Emergency Assistance Type')}</h3>
                    </div>
                    <button class="btn btn-outline btn-sm" onclick="sosManager.toggleSiren()" id="siren-toggle-btn">
                        ${this.isSirenPlaying ? t('btn_siren_stop', '🔇 Stop Siren Alarm') : t('btn_siren', '🔊 Sound Siren Alarm')}
                    </button>
                </div>

                <!-- Emergency Type Buttons Grid -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; margin-bottom: 1.5rem;">
                    <button class="btn btn-outline category-btn active" onclick="sosManager.selectCategory('Medical emergency', this)">
                        ${t('sos_med', '🩺 Medical Emergency')}
                    </button>
                    <button class="btn btn-outline category-btn" onclick="sosManager.selectCategory('Accident', this)">
                        ${t('sos_accident', '🚗 Vehicle Accident')}
                    </button>
                    <button class="btn btn-outline category-btn" onclick="sosManager.selectCategory('Harassment or threat', this)">
                        ${t('sos_threat', '🛡️ Threat / Harassment')}
                    </button>
                    <button class="btn btn-outline category-btn" onclick="sosManager.selectCategory('Lost tourist', this)">
                        ${t('sos_lost', '🧭 Lost / Stranded')}
                    </button>
                    <button class="btn btn-outline category-btn" onclick="sosManager.selectCategory('Natural disaster', this)">
                        ${t('sos_disaster', '🌊 Natural Disaster')}
                    </button>
                    <button class="btn btn-outline category-btn" onclick="sosManager.selectCategory('Other emergency', this)">
                        ${t('sos_other', '⚠️ Other Urgent')}
                    </button>
                </div>

                <!-- Current Location Verified -->
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid var(--navy-border); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="font-size: 0.8rem; color: var(--safe-emerald-light); font-weight: 700; text-transform: uppercase;">
                            📍 GPS Location Captured
                        </div>
                        <div style="font-size: 0.95rem; color: #ffffff; font-weight: 600;">
                            Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}
                        </div>
                    </div>
                    <button class="btn btn-sm btn-emerald" onclick="sosManager.dispatchIncidentReport(${lat}, ${lng})">
                        ${t('sos_save_incident', 'Save Incident Report')}
                    </button>
                </div>

                <!-- Direct Dialing Hotlines -->
                <h4 style="font-size: 1.05rem; color: #ffffff; margin-bottom: 0.75rem;">
                    ${t('sos_helplines_title', 'Official Direct Emergency Helplines (One-Tap Dial)')}
                </h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem; margin-bottom: 1.5rem;">
                    <a href="tel:112" class="btn btn-sos" style="display: flex; flex-direction: column; padding: 0.75rem;">
                        <span style="font-size: 1.25rem; font-weight: 800;">📞 112</span>
                        <span style="font-size: 0.75rem; font-weight: 500; opacity: 0.9;">National All-in-One Emergency</span>
                    </a>
                    <a href="tel:100" class="btn btn-outline" style="display: flex; flex-direction: column; padding: 0.75rem;">
                        <span style="font-size: 1.25rem; font-weight: 800; color: #60a5fa;">👮 100</span>
                        <span style="font-size: 0.75rem; color: var(--text-muted);">Police Control Room</span>
                    </a>
                    <a href="tel:102" class="btn btn-outline" style="display: flex; flex-direction: column; padding: 0.75rem;">
                        <span style="font-size: 1.25rem; font-weight: 800; color: #f87171;">🚑 102 / 108</span>
                        <span style="font-size: 0.75rem; color: var(--text-muted);">Ambulance & Trauma</span>
                    </a>
                    <a href="tel:1090" class="btn btn-outline" style="display: flex; flex-direction: column; padding: 0.75rem;">
                        <span style="font-size: 1.25rem; font-weight: 800; color: #f472b6;">👩 1090 / 181</span>
                        <span style="font-size: 0.75rem; color: var(--text-muted);">Women Safety Helpline</span>
                    </a>
                    <a href="tel:1363" class="btn btn-outline" style="display: flex; flex-direction: column; padding: 0.75rem;">
                        <span style="font-size: 1.25rem; font-weight: 800; color: #34d399;">🧳 1363</span>
                        <span style="font-size: 0.75rem; color: var(--text-muted);">24/7 Tourist Assistance</span>
                    </a>
                </div>

                <!-- Legal Emergency Disclaimer -->
                <div style="background: rgba(220, 38, 38, 0.08); border: 1px solid rgba(220, 38, 38, 0.25); border-radius: var(--radius-md); padding: 0.85rem 1.15rem; font-size: 0.82rem; color: #fca5a5; line-height: 1.5;">
                    <strong>Important Safety Notice:</strong> Geonova records your incident coordinates and dispatches simulated alerts to your verified emergency contacts. This platform does not replace direct emergency service dispatch; in critical or life-threatening situations, always dial <strong>112</strong> immediately.
                </div>

                <div style="margin-top: 1.5rem; text-align: right;">
                    <button class="btn btn-outline" onclick="sosManager.cancelSOS()">Close SOS Screen</button>
                </div>
            </div>
        `;
    }

    selectCategory(cat, elem) {
        this.selectedCategory = cat;
        document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active', 'btn-primary'));
        elem.classList.add('active', 'btn-primary');
    }

    async dispatchIncidentReport(lat, lng) {
        try {
            const userPhone = (window.auth && window.auth.currentUser) ? window.auth.currentUser.phone_number : "Direct SOS";
            const incident = await api.triggerSOS({
                emergency_type: this.selectedCategory,
                latitude: lat,
                longitude: lng,
                location_name: "Active Traveler Coordinates",
                description: `Emergency alert triggered by user: ${this.selectedCategory}`,
                contact_phone: userPhone
            });

            window.showToast(`Incident #${incident.id} logged securely. Emergency contacts notified!`, 'success');
            
            // Reload tourist dashboard incidents
            if (window.dashboard) window.dashboard.loadData();
        } catch (e) {
            window.showToast('Failed to log incident: ' + e.message, 'danger');
        }
    }

    toggleSiren() {
        if (this.isSirenPlaying) {
            this.stopSiren();
        } else {
            this.startSiren();
        }
    }

    startSiren() {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            this.audioCtx = new AudioContext();
            this.sirenOsc = this.audioCtx.createOscillator();
            this.sirenGain = this.audioCtx.createGain();

            this.sirenOsc.type = 'sawtooth';
            this.sirenOsc.frequency.setValueAtTime(600, this.audioCtx.currentTime);
            this.sirenGain.gain.setValueAtTime(0.2, this.audioCtx.currentTime);

            this.sirenOsc.connect(this.sirenGain);
            this.sirenGain.connect(this.audioCtx.destination);
            this.sirenOsc.start();

            let high = false;
            this.sirenInterval = setInterval(() => {
                if (!this.audioCtx) return;
                const freq = high ? 600 : 900;
                this.sirenOsc.frequency.exponentialRampToValueAtTime(freq, this.audioCtx.currentTime + 0.25);
                high = !high;
            }, 300);

            this.isSirenPlaying = true;
            const btn = document.getElementById('siren-toggle-btn');
            if (btn) btn.innerHTML = '🔇 Stop Siren Alarm';
            window.showToast('Audible distress siren sounding!', 'warning');
        } catch (e) {
            console.error('Audio siren error:', e);
        }
    }

    stopSiren() {
        if (this.sirenInterval) clearInterval(this.sirenInterval);
        if (this.sirenOsc) {
            try { this.sirenOsc.stop(); } catch (e) {}
        }
        if (this.audioCtx) {
            try { this.audioCtx.close(); } catch (e) {}
        }
        this.isSirenPlaying = false;
        const btn = document.getElementById('siren-toggle-btn');
        if (btn) btn.innerHTML = '🔊 Sound Siren Alarm';
    }
}

const sosManager = new SOSManager();
window.sosManager = sosManager;
