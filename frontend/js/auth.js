// Geonova Authentication & User Profile Manager

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    async init() {
        if (api.token) {
            try {
                this.currentUser = await api.getProfile();
                this.renderAuthState();
            } catch (e) {
                console.warn('Session expired or invalid. Clearing token.');
                api.setToken(null);
                this.currentUser = null;
                this.renderAuthState();
            }
        } else {
            this.renderAuthState();
        }

        window.addEventListener('auth:expired', () => {
            this.currentUser = null;
            this.renderAuthState();
            if (window.showToast) window.showToast('Session expired. Please log in again.', 'warning');
        });
    }

    renderAuthState() {
        const userNavContainer = document.getElementById('user-nav-actions');
        if (!userNavContainer) return;

        if (this.currentUser) {
            const roleBadgeClass = this.currentUser.role === 'admin' ? 'badge-crimson' : 
                                  this.currentUser.role === 'provider' ? 'badge-amber' : 
                                  this.currentUser.role === 'authority' ? 'badge-blue' : 'badge-emerald';

            const aadhaarBadge = this.currentUser.is_aadhaar_verified ? `
                <span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); font-size: 0.68rem; padding: 0.18rem 0.5rem; display: inline-flex; align-items: center; gap: 0.25rem;">
                    <span>🇮🇳</span> Aadhaar Verified
                </span>
            ` : '';

            userNavContainer.innerHTML = `
                <div class="user-dropdown-container" style="display: flex; align-items: center; gap: 0.75rem;">
                    <button class="btn btn-outline btn-sm" onclick="app.navigate('dashboard')" style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="width: 28px; height: 28px; border-radius: 50%; background: var(--grad-primary); display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 700;">
                            ${this.currentUser.full_name.charAt(0)}
                        </span>
                        <span>${this.currentUser.full_name.split(' ')[0]}</span>
                        <span class="badge ${roleBadgeClass}" style="font-size: 0.65rem; padding: 0.15rem 0.45rem;">${this.currentUser.role}</span>
                        ${aadhaarBadge}
                    </button>
                    ${this.currentUser.role === 'admin' ? `
                        <button class="btn btn-sm btn-emerald" onclick="app.navigate('admin')">
                            Admin Console
                        </button>
                    ` : ''}
                    <button class="btn btn-outline btn-sm" onclick="auth.logout()" title="Logout" style="padding: 0.45rem 0.65rem;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                    </button>
                </div>
            `;
        } else {
            userNavContainer.innerHTML = `
                <button class="btn btn-outline btn-sm btn-login" onclick="app.navigate('login')">Login</button>
                <button class="btn btn-primary btn-sm" onclick="auth.openRegisterModal()">Register</button>
            `;
        }
    }

    openLoginModal() {
        const modal = document.getElementById('auth-modal');
        const modalBody = document.getElementById('auth-modal-body');
        const modalTitle = document.getElementById('auth-modal-title');

        modalTitle.textContent = 'Welcome Back to Geonova';
        modalBody.innerHTML = `
            <form id="login-form" onsubmit="auth.handleLogin(event)">
                <div class="form-group">
                    <label class="form-label">Email Address</label>
                    <input type="email" id="login-email" class="form-input" placeholder="tourist@geonova.in" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" id="login-password" class="form-input" placeholder="••••••••" required />
                </div>
                <button type="submit" class="btn btn-primary btn-block" style="margin-top: 1rem;">Sign In</button>
            </form>

            <div style="margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid var(--navy-border);">
                <div style="font-size: 0.8rem; color: var(--text-muted); text-align: center; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">
                    Demo Quick Access Logins
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                    <button class="btn btn-outline btn-sm" onclick="auth.quickFill('tourist@geonova.in', 'Tourist@123')">Tourist Demo</button>
                    <button class="btn btn-outline btn-sm" onclick="auth.quickFill('admin@geonova.in', 'Admin@123')">Admin Demo</button>
                    <button class="btn btn-outline btn-sm" onclick="auth.quickFill('provider@geonova.in', 'Provider@123')">Provider Demo</button>
                    <button class="btn btn-outline btn-sm" onclick="auth.quickFill('police@geonova.in', 'Police@123')">Authority Demo</button>
                </div>
            </div>

            <div style="margin-top: 1.25rem; text-align: center; font-size: 0.85rem; color: var(--text-muted);">
                Don't have an account yet? <a href="#" onclick="auth.openRegisterModal(); return false;" style="color: var(--safe-emerald-light); font-weight: 600;">Register here</a>
            </div>
        `;

        modal.classList.add('open');
    }

    openRegisterModal() {
        const modal = document.getElementById('auth-modal');
        const modalBody = document.getElementById('auth-modal-body');
        const modalTitle = document.getElementById('auth-modal-title');

        modalTitle.textContent = 'Create Your Geonova Account';
        modalBody.innerHTML = `
            <form id="register-form" onsubmit="auth.handleRegister(event)">
                <div class="form-group">
                    <label class="form-label">Full Name</label>
                    <input type="text" id="reg-name" class="form-input" placeholder="e.g. John Doe / Priya Sharma" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Email Address</label>
                    <input type="email" id="reg-email" class="form-input" placeholder="name@example.com" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Phone Number (with country code)</label>
                    <input type="tel" id="reg-phone" class="form-input" placeholder="+91 9876543210" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Account Role</label>
                    <select id="reg-role" class="form-select">
                        <option value="tourist">Tourist (Domestic / International)</option>
                        <option value="provider">Tourism Provider / Tour Operator</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" id="reg-password" class="form-input" placeholder="At least 6 characters" minlength="6" required />
                </div>
                <button type="submit" class="btn btn-emerald btn-block" style="margin-top: 1rem;">Create Safe Account</button>
            </form>

            <div style="margin-top: 1.25rem; text-align: center; font-size: 0.85rem; color: var(--text-muted);">
                Already registered? <a href="#" onclick="auth.openLoginModal(); return false;" style="color: #60a5fa; font-weight: 600;">Sign In</a>
            </div>
        `;

        modal.classList.add('open');
    }

    quickFill(email, password) {
        const emailInput = document.getElementById('login-email');
        const passInput = document.getElementById('login-password');
        if (emailInput && passInput) {
            emailInput.value = email;
            passInput.value = password;
        }
    }

    onLoginSuccess(user, message) {
        this.currentUser = user;
        this.renderAuthState();
        this.closeModal();
        if (window.showToast) window.showToast(message || `Welcome back, ${user.full_name}!`, 'success');
        
        // Reload relevant dashboard data
        if (window.dashboard) window.dashboard.loadData();
        if (window.admin && user.role === 'admin') window.admin.loadStats();

        // Redirect to Home page after successful login!
        if (window.app) {
            window.app.navigate('home');
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            const data = await api.login({ email, password });
            api.setToken(data.access_token);
            this.onLoginSuccess(data.user, `Welcome back, ${data.user.full_name}!`);
        } catch (error) {
            window.showToast(error.message, 'danger');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const full_name = document.getElementById('reg-name').value;
        const email = document.getElementById('reg-email').value;
        const phone_number = document.getElementById('reg-phone').value;
        const role = document.getElementById('reg-role').value;
        const password = document.getElementById('reg-password').value;

        try {
            const data = await api.register({ full_name, email, phone_number, role, password });
            api.setToken(data.access_token);
            this.onLoginSuccess(data.user, 'Account created successfully! Your Geonova pass is active.');
        } catch (error) {
            window.showToast(error.message, 'danger');
        }
    }

    // --- Multi-Channel Login Page Methods ---

    switchLoginTab(method) {
        document.querySelectorAll('.auth-tab-trigger').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.auth-panel').forEach(panel => panel.classList.remove('active'));

        const tabBtn = document.getElementById(`tab-btn-${method}`);
        const tabPane = document.getElementById(`panel-auth-${method}`);
        if (tabBtn) tabBtn.classList.add('active');
        if (tabPane) tabPane.classList.add('active');
    }

    async handleGoogleLogin(e, emailOverride, nameOverride) {
        if (e) e.preventDefault();
        const email = emailOverride || (document.getElementById('login-google-email') ? document.getElementById('login-google-email').value : 'aarav.mehta.travel@gmail.com');
        const name = nameOverride || (email ? email.split('@')[0].replace('.', ' ').replace(/\b\w/g, c => c.toUpperCase()) : 'Google Traveler');

        try {
            const data = await api.loginWithGoogle({ email, full_name: name });
            api.setToken(data.access_token);
            this.onLoginSuccess(data.user, `Signed in with Google (${email})!`);
        } catch (error) {
            window.showToast(error.message || 'Google sign-in failed', 'danger');
        }
    }

    async handleSendPhoneOtp(e) {
        if (e) e.preventDefault();
        const prefix = document.getElementById('phone-prefix') ? document.getElementById('phone-prefix').value : '+91';
        const num = document.getElementById('phone-number-input') ? document.getElementById('phone-number-input').value.trim() : '';

        if (!num || num.length < 7) {
            window.showToast('Please enter a valid mobile number.', 'warning');
            return;
        }

        const fullPhone = `${prefix} ${num}`.trim();
        try {
            const res = await api.sendPhoneOtp({ phone_number: fullPhone });
            const stepBox = document.getElementById('phone-otp-step');
            if (stepBox) {
                stepBox.style.display = 'block';
                const chip = document.getElementById('phone-demo-otp-chip');
                if (chip) chip.textContent = `Demo SMS OTP: ${res.demo_otp}`;
                const otpInput = document.getElementById('phone-otp-input');
                if (otpInput) otpInput.value = res.demo_otp;
            }
            window.showToast(res.message, 'info');
        } catch (error) {
            window.showToast(error.message, 'danger');
        }
    }

    async handleVerifyPhoneOtp(e) {
        if (e) e.preventDefault();
        const prefix = document.getElementById('phone-prefix') ? document.getElementById('phone-prefix').value : '+91';
        const num = document.getElementById('phone-number-input') ? document.getElementById('phone-number-input').value.trim() : '';
        const otp = document.getElementById('phone-otp-input') ? document.getElementById('phone-otp-input').value.trim() : '';

        if (!otp) {
            window.showToast('Please enter the 6-digit verification code.', 'warning');
            return;
        }

        const fullPhone = `${prefix} ${num}`.trim();
        try {
            const data = await api.verifyPhoneOtp({ phone_number: fullPhone, otp });
            api.setToken(data.access_token);
            this.onLoginSuccess(data.user, `Verified mobile ${fullPhone}. Welcome to Geonova!`);
        } catch (error) {
            window.showToast(error.message, 'danger');
        }
    }

    formatAadhaarInput(el) {
        if (!el) return;
        let val = el.value.replace(/\D/g, '').substring(0, 12);
        let parts = [];
        for (let i = 0; i < val.length; i += 4) {
            parts.push(val.substring(i, i + 4));
        }
        el.value = parts.join(' ');
    }

    async handleSendAadhaarOtp(e) {
        if (e) e.preventDefault();
        const aadhEl = document.getElementById('aadhaar-number-input');
        const aadhVal = aadhEl ? aadhEl.value.trim() : '';
        const consent = document.getElementById('aadhaar-consent-checkbox') ? document.getElementById('aadhaar-consent-checkbox').checked : false;

        const digits = aadhVal.replace(/\D/g, '');
        if (digits.length !== 12) {
            window.showToast('Please enter a valid 12-digit Aadhaar number.', 'warning');
            return;
        }

        if (!consent) {
            window.showToast('Please accept the voluntary UIDAI e-KYC consent checkbox.', 'warning');
            return;
        }

        try {
            const res = await api.sendAadhaarOtp({ aadhaar_number: aadhVal, consent: true });
            const stepBox = document.getElementById('aadhaar-otp-step');
            if (stepBox) {
                stepBox.style.display = 'block';
                const targetText = document.getElementById('aadhaar-masked-target');
                if (targetText) targetText.textContent = res.masked_target;
                const chip = document.getElementById('aadhaar-demo-otp-chip');
                if (chip) chip.textContent = `UIDAI Demo OTP: ${res.demo_otp}`;
                const otpInput = document.getElementById('aadhaar-otp-input');
                if (otpInput) otpInput.value = res.demo_otp;
            }
            window.showToast(res.message, 'info');
        } catch (error) {
            window.showToast(error.message, 'danger');
        }
    }

    async handleVerifyAadhaarOtp(e) {
        if (e) e.preventDefault();
        const aadhEl = document.getElementById('aadhaar-number-input');
        const aadhVal = aadhEl ? aadhEl.value.trim() : '';
        const otp = document.getElementById('aadhaar-otp-input') ? document.getElementById('aadhaar-otp-input').value.trim() : '';

        if (!otp) {
            window.showToast('Please enter the 6-digit UIDAI OTP.', 'warning');
            return;
        }

        try {
            const data = await api.verifyAadhaarOtp({ aadhaar_number: aadhVal, otp });
            api.setToken(data.access_token);
            this.onLoginSuccess(data.user, `🇮🇳 Official UIDAI Verification Verified! Welcome, ${data.user.full_name}.`);
        } catch (error) {
            window.showToast(error.message, 'danger');
        }
    }

    quickFillMethod(method, val1, val2) {
        this.switchLoginTab(method);
        if (method === 'google') {
            const emailInput = document.getElementById('login-google-email');
            if (emailInput) emailInput.value = val1;
            this.handleGoogleLogin(null, val1, val2);
        } else if (method === 'phone') {
            const phoneInput = document.getElementById('phone-number-input');
            if (phoneInput) phoneInput.value = val1;
            this.handleSendPhoneOtp(null);
        } else if (method === 'aadhaar') {
            const aadhInput = document.getElementById('aadhaar-number-input');
            const consentCheckbox = document.getElementById('aadhaar-consent-checkbox');
            if (aadhInput) {
                aadhInput.value = val1;
                this.formatAadhaarInput(aadhInput);
            }
            if (consentCheckbox) consentCheckbox.checked = true;
            this.handleSendAadhaarOtp(null);
        }
    }

    logout() {
        api.setToken(null);
        this.currentUser = null;
        this.renderAuthState();
        window.showToast('Logged out safely.', 'info');
        app.navigate('home');
    }

    closeModal() {
        const modal = document.getElementById('auth-modal');
        if (modal) modal.classList.remove('open');
    }
}

const auth = new AuthManager();
window.auth = auth;
