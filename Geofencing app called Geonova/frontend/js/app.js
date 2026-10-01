// Geonova Core Application Coordinator & Router

class App {
    constructor() {
        this.currentRoute = 'home';
        this.protocols = [];
    }

    async init() {
        if (window.i18n) window.i18n.init();
        this.setupRouting();
        this.setupToasts();

        // Initialize sub-systems
        await tourism.init();
        await packageManager.init();
        await paymentManager.init();
        await this.loadSafetyProtocols();

        // Handle initial URL hash
        const hash = window.location.hash.replace('#', '') || 'home';
        this.navigate(hash);
    }

    setupRouting() {
        window.addEventListener('hashchange', () => {
            const route = window.location.hash.replace('#', '') || 'home';
            this.navigate(route);
        });
    }

    navigate(route) {
        this.currentRoute = route;
        if (window.location.hash.replace('#', '') !== route) {
            history.pushState(null, '', `#${route}`);
        }

        // Hide all views
        document.querySelectorAll('.app-view').forEach(view => {
            view.style.display = 'none';
        });

        // Show target view
        const target = document.getElementById(`view-${route}`);
        if (target) {
            target.style.display = 'block';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            const homeView = document.getElementById('view-home');
            if (homeView) homeView.style.display = 'block';
        }

        // Update active nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('href') === `#${route}`) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        // Update mobile bottom nav links
        document.querySelectorAll('.bottom-nav-item').forEach(item => {
            if (item.dataset.route === route) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Route-specific triggers
        if (route === 'map') {
            setTimeout(() => {
                if (window.mapManager) {
                    window.mapManager.init();
                    if (window.mapManager.map) window.mapManager.map.invalidateSize();
                }
            }, 100);
        } else if (route === 'dashboard') {
            if (window.dashboard) window.dashboard.loadData();
        } else if (route === 'admin') {
            if (window.admin) window.admin.loadStats();
        } else if (route === 'vault') {
            if (window.vaultManager) window.vaultManager.init();
        }

        if (window.i18n) window.i18n.applyTranslations();
    }

    setupToasts() {
        window.showToast = (message, type = 'info') => {
            const container = document.getElementById('toast-container');
            if (!container) return;

            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            const icon = type === 'success' ? '✓' : type === 'danger' ? '✕' : type === 'warning' ? '⚠' : 'ℹ';

            toast.innerHTML = `
                <div style="font-weight: 700; font-size: 1.1rem;">${icon}</div>
                <div style="font-size: 0.9rem;">${message}</div>
            `;

            container.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                toast.style.transition = 'all 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }, 4000);
        };
    }

    async loadSafetyProtocols() {
        try {
            this.protocols = await api.getProtocols();
            this.renderSafetyProtocols(this.protocols);
        } catch (e) {
            console.error('Failed to load safety protocols:', e);
        }
    }

    renderSafetyProtocols(protocols) {
        const container = document.getElementById('protocols-cards-container');
        if (!container) return;

        container.innerHTML = protocols.map((p, idx) => `
            <div class="glass-card" style="margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                    <div>
                        <span class="badge badge-blue" style="font-size: 0.72rem; margin-bottom: 0.35rem;">${p.category}</span>
                        <h3 style="color: #ffffff; font-size: 1.3rem;">${p.title}</h3>
                    </div>
                    <span class="badge badge-emerald">Verified Protocol</span>
                </div>
                
                <p style="color: #cbd5e1; font-size: 0.92rem; margin-bottom: 1.25rem; line-height: 1.6;">${p.summary}</p>

                <!-- Warnings Banner -->
                <div style="background: rgba(220, 38, 38, 0.1); border-left: 3px solid #ef4444; padding: 0.75rem 1rem; border-radius: 0 var(--radius-md) var(--radius-md) 0; margin-bottom: 1rem; font-size: 0.88rem; color: #fca5a5;">
                    <strong>Warning Indicators:</strong> ${p.warning_signs}
                </div>

                <!-- Do's and Don'ts Split -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: var(--radius-md); padding: 1rem;">
                        <h5 style="color: var(--safe-emerald-light); font-size: 0.85rem; text-transform: uppercase; margin-bottom: 0.4rem;">
                            ✓ Recommended Do's
                        </h5>
                        <p style="color: #ffffff; font-size: 0.85rem; line-height: 1.5;">${p.dos}</p>
                    </div>

                    <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: var(--radius-md); padding: 1rem;">
                        <h5 style="color: #f87171; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 0.4rem;">
                            ✕ Dangerous Don'ts
                        </h5>
                        <p style="color: #ffffff; font-size: 0.85rem; line-height: 1.5;">${p.donts}</p>
                    </div>
                </div>

                <!-- Emergency Action Guidance -->
                <div style="background: rgba(30, 41, 59, 0.6); border-radius: var(--radius-md); padding: 0.75rem 1rem; font-size: 0.82rem; color: var(--text-muted); display: flex; align-items: center; justify-content: space-between;">
                    <span>Emergency Procedure: <strong style="color: #ffffff;">${p.emergency_guidance}</strong></span>
                    <a href="tel:112" class="btn btn-sos btn-sm" style="padding: 0.25rem 0.6rem; font-size: 0.75rem;">112 Emergency</a>
                </div>
            </div>
        `).join('');
    }

    searchProtocols(query) {
        const q = query.trim().toLowerCase();
        if (!q) {
            this.renderSafetyProtocols(this.protocols);
            return;
        }

        const filtered = this.protocols.filter(p => 
            p.category.toLowerCase().includes(q) ||
            p.title.toLowerCase().includes(q) ||
            p.summary.toLowerCase().includes(q) ||
            p.dos.toLowerCase().includes(q)
        );
        this.renderSafetyProtocols(filtered);
    }
}

const app = new App();
window.app = app;

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
