// Geonova Administrator Console & Safety Command Center

class AdminManager {
    constructor() {
        this.activeTab = 'incidents';
    }

    async init() {
        if (!auth.currentUser || auth.currentUser.role !== 'admin') return;
        this.loadStats();
    }

    async loadStats() {
        try {
            const [stats, incidents, geofences, users, auditLogs] = await Promise.all([
                api.getAdminStats(),
                api.getAdminIncidents(),
                api.getGeofences(),
                api.getAdminUsers(),
                api.getAuditLogs()
            ]);

            this.renderAdminConsole(stats, incidents, geofences, users, auditLogs);
        } catch (e) {
            console.error('Failed to load admin console data:', e);
        }
    }

    renderAdminConsole(stats, incidents, geofences, users, auditLogs) {
        const container = document.getElementById('admin-view');
        if (!container) return;

        if (!auth.currentUser || auth.currentUser.role !== 'admin') {
            container.innerHTML = `
                <div style="text-align: center; padding: 4rem; background: var(--bg-glass-card); border-radius: var(--radius-xl); border: 1px solid var(--navy-border);">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🛡️</div>
                    <h2 style="color: #ffffff; margin-bottom: 0.5rem;">Administrator Access Restricted</h2>
                    <p style="color: var(--text-muted); margin-bottom: 1.5rem;">You need administrative privileges to view incident reports, moderate geofences, and review audit logs.</p>
                    <button class="btn btn-crimson" onclick="auth.openLoginModal()">Login as Admin</button>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                    <div>
                        <span class="badge badge-crimson" style="margin-bottom: 0.4rem;">Geonova Safety Operations Center</span>
                        <h2 style="font-size: 2.2rem; color: #ffffff; margin: 0;">Central Operations Command</h2>
                    </div>
                    <div style="display: flex; gap: 0.75rem;">
                        <button class="btn btn-outline btn-sm" onclick="admin.loadStats()">🔄 Refresh Live Telemetry</button>
                        <button class="btn btn-emerald btn-sm" onclick="admin.openNewGeofenceModal()">+ Add New Geofence</button>
                    </div>
                </div>

                <!-- Admin KPI Cards -->
                <div class="stats-cards-grid" style="margin-bottom: 2.5rem;">
                    <div class="stat-card">
                        <div class="stat-card-info">
                            <h5>Registered Tourists</h5>
                            <div class="stat-card-value">${stats.total_users}</div>
                        </div>
                        <div class="stat-card-icon stat-icon-blue">👥</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-card-info">
                            <h5>Active Geofences</h5>
                            <div class="stat-card-value">${stats.active_geofences}</div>
                        </div>
                        <div class="stat-card-icon stat-icon-emerald">🌐</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-card-info">
                            <h5>Open SOS Tickets</h5>
                            <div class="stat-card-value" style="color: #f87171;">${stats.open_sos_incidents}</div>
                        </div>
                        <div class="stat-card-icon stat-icon-crimson">🚨</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-card-info">
                            <h5>Total Marketplace Revenue</h5>
                            <div class="stat-card-value" style="color: #34d399;">₹${stats.total_revenue_inr.toLocaleString()}</div>
                        </div>
                        <div class="stat-card-icon stat-icon-amber">💰</div>
                    </div>
                </div>

                <!-- Admin Navigation Tabs -->
                <div class="filter-tabs" style="margin-bottom: 1.5rem;">
                    <button class="tab-btn active" onclick="admin.switchAdminTab('incidents', this)">
                        🚨 SOS Incident Triage (${incidents.length})
                    </button>
                    <button class="tab-btn" onclick="admin.switchAdminTab('geofences', this)">
                        🛡️ Geofence Boundaries (${geofences.length})
                    </button>
                    <button class="tab-btn" onclick="admin.switchAdminTab('users', this)">
                        👤 User Accounts (${users.length})
                    </button>
                    <button class="tab-btn" onclick="admin.switchAdminTab('audit', this)">
                        📜 Security & Audit Logs (${auditLogs.length})
                    </button>
                </div>

                <!-- Tab Pane: Incidents -->
                <div id="admin-tab-incidents" class="admin-pane">
                    <div class="data-table-container">
                        <div class="data-table-header">
                            <h3 style="color: #ffffff; font-size: 1.15rem;">Real-Time Emergency Incident Log</h3>
                        </div>
                        ${incidents.length === 0 ? `
                            <div style="padding: 3rem; text-align: center; color: var(--text-muted);">No emergency incidents on record. All tourists safe!</div>
                        ` : `
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Emergency Type</th>
                                        <th>Location Coordinates</th>
                                        <th>Phone Contact</th>
                                        <th>Status</th>
                                        <th>Reported At</th>
                                        <th>Resolution Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${incidents.map(inc => {
                                        const badgeClass = inc.status === 'resolved' ? 'badge-emerald' : 
                                                           inc.status === 'investigating' ? 'badge-amber' : 'badge-crimson';
                                        return `
                                            <tr>
                                                <td>#${inc.id}</td>
                                                <td><strong style="color: #ffffff;">${inc.emergency_type}</strong></td>
                                                <td>Lat: ${inc.latitude.toFixed(4)}, Lng: ${inc.longitude.toFixed(4)}</td>
                                                <td><a href="tel:${inc.contact_phone}" style="color: #60a5fa;">${inc.contact_phone || 'N/A'}</a></td>
                                                <td><span class="badge ${badgeClass}">${inc.status}</span></td>
                                                <td style="color: var(--text-muted); font-size: 0.8rem;">${new Date(inc.reported_at).toLocaleString()}</td>
                                                <td>
                                                    ${inc.status !== 'resolved' ? `
                                                        <button class="btn btn-outline btn-sm" onclick="admin.resolveIncident(${inc.id}, 'investigating')" style="padding: 0.25rem 0.6rem;">Investigate</button>
                                                        <button class="btn btn-emerald btn-sm" onclick="admin.resolveIncident(${inc.id}, 'resolved')" style="padding: 0.25rem 0.6rem;">Mark Resolved</button>
                                                    ` : `
                                                        <span style="color: var(--safe-emerald-light); font-size: 0.8rem;">✓ Closed</span>
                                                    `}
                                                </td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        `}
                    </div>
                </div>

                <!-- Tab Pane: Geofences -->
                <div id="admin-tab-geofences" class="admin-pane" style="display: none;">
                    <div class="data-table-container">
                        <div class="data-table-header">
                            <h3 style="color: #ffffff; font-size: 1.15rem;">Active Safety & Hazard Geofences</h3>
                            <button class="btn btn-emerald btn-sm" onclick="admin.openNewGeofenceModal()">+ Add New Geofence</button>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Zone Type</th>
                                    <th>Coordinates</th>
                                    <th>Radius</th>
                                    <th>Warning Advisory</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${geofences.map(gf => {
                                    const badgeClass = gf.zone_type === 'restricted' ? 'badge-crimson' : 
                                                       gf.zone_type === 'hazard' ? 'badge-amber' : 'badge-emerald';
                                    return `
                                        <tr>
                                            <td><strong>${gf.name}</strong></td>
                                            <td><span class="badge ${badgeClass}">${gf.zone_type}</span></td>
                                            <td>${gf.center_latitude.toFixed(4)}, ${gf.center_longitude.toFixed(4)}</td>
                                            <td>${gf.radius_meters}m</td>
                                            <td style="font-size: 0.82rem; color: var(--text-muted); max-width: 250px;">${gf.warning_message}</td>
                                            <td>
                                                <button class="btn btn-outline btn-sm" style="color: #f87171;" onclick="admin.deleteGeofence(${gf.id})">Delete</button>
                                            </td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Tab Pane: Users -->
                <div id="admin-tab-users" class="admin-pane" style="display: none;">
                    <div class="data-table-container">
                        <div class="data-table-header">
                            <h3 style="color: #ffffff; font-size: 1.15rem;">Registered Platform Accounts</h3>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>User Name</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                    <th>Role</th>
                                    <th>Nationality</th>
                                    <th>Registration Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${users.map(u => `
                                    <tr>
                                        <td><strong>${u.name}</strong></td>
                                        <td>${u.email}</td>
                                        <td>${u.phone}</td>
                                        <td><span class="badge ${u.role === 'admin' ? 'badge-crimson' : 'badge-emerald'}">${u.role}</span></td>
                                        <td>${u.nationality}</td>
                                        <td style="font-size: 0.8rem; color: var(--text-muted);">${new Date(u.created_at).toLocaleDateString()}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Tab Pane: Audit Logs -->
                <div id="admin-tab-audit" class="admin-pane" style="display: none;">
                    <div class="data-table-container">
                        <div class="data-table-header">
                            <h3 style="color: #ffffff; font-size: 1.15rem;">Security Audit Trail</h3>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Action</th>
                                    <th>Details</th>
                                    <th>IP Address</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${auditLogs.map(log => `
                                    <tr>
                                        <td style="font-size: 0.8rem; color: var(--text-muted);">${new Date(log.created_at).toLocaleString()}</td>
                                        <td><strong style="color: #60a5fa;">${log.action}</strong></td>
                                        <td style="font-size: 0.85rem;">${log.details}</td>
                                        <td style="font-size: 0.8rem; color: var(--text-muted);">${log.ip_address}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }

    switchAdminTab(tabKey, clickedElem) {
        document.querySelectorAll('.filter-tabs .tab-btn').forEach(b => b.classList.remove('active'));
        if (clickedElem) clickedElem.classList.add('active');

        document.querySelectorAll('.admin-pane').forEach(p => p.style.display = 'none');
        const target = document.getElementById(`admin-tab-${tabKey}`);
        if (target) target.style.display = 'block';
    }

    async resolveIncident(id, status) {
        const adminNotes = prompt('Enter incident resolution notes:', 'Coordinated with tourist police and assistance dispatched.');
        if (adminNotes === null) return;

        try {
            await api.updateIncident(id, { status, admin_notes: adminNotes });
            window.showToast(`Incident #${id} marked as ${status}.`, 'success');
            this.loadStats();
        } catch (e) {
            window.showToast('Failed to update incident: ' + e.message, 'danger');
        }
    }

    openNewGeofenceModal() {
        const modal = document.getElementById('auth-modal');
        const modalBody = document.getElementById('auth-modal-body');
        const modalTitle = document.getElementById('auth-modal-title');

        modalTitle.textContent = 'Create New Geofence Boundary';
        modalBody.innerHTML = `
            <form onsubmit="admin.handleCreateGeofence(event)">
                <div class="form-group">
                    <label class="form-label">Zone Name</label>
                    <input type="text" id="gf-name" class="form-input" placeholder="e.g. Mumbai Marine Drive Safe Corridor" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Zone Type</label>
                    <select id="gf-type" class="form-select">
                        <option value="tourist_safety">Tourist Safety Zone (Green)</option>
                        <option value="hazard">Hazard Caution Zone (Amber)</option>
                        <option value="restricted">Restricted / Protected Zone (Red)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input type="text" id="gf-desc" class="form-input" placeholder="High pedestrian safety and 24x7 security" required />
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="form-group">
                        <label class="form-label">Center Latitude</label>
                        <input type="number" step="any" id="gf-lat" class="form-input" placeholder="18.9438" required />
                    </div>
                    <div class="form-group">
                        <label class="form-label">Center Longitude</label>
                        <input type="number" step="any" id="gf-lng" class="form-input" placeholder="72.8233" required />
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Radius (meters)</label>
                    <input type="number" id="gf-radius" class="form-input" value="1000" min="100" max="50000" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Warning Message (Displayed on Entry)</label>
                    <textarea id="gf-warning" class="form-textarea" rows="2" placeholder="Warning advisory shown to approaching tourists..." required></textarea>
                </div>
                <button type="submit" class="btn btn-emerald btn-block" style="margin-top: 1rem;">Save Geofence</button>
            </form>
        `;

        modal.classList.add('open');
    }

    async handleCreateGeofence(e) {
        e.preventDefault();
        const name = document.getElementById('gf-name').value;
        const zone_type = document.getElementById('gf-type').value;
        const description = document.getElementById('gf-desc').value;
        const center_latitude = parseFloat(document.getElementById('gf-lat').value);
        const center_longitude = parseFloat(document.getElementById('gf-lng').value);
        const radius_meters = parseFloat(document.getElementById('gf-radius').value);
        const warning_message = document.getElementById('gf-warning').value;

        try {
            await api.createGeofence({
                name,
                zone_type,
                description,
                center_latitude,
                center_longitude,
                radius_meters,
                warning_message
            });

            auth.closeModal();
            window.showToast('Geofence created successfully and synchronized with live map!', 'success');
            this.loadStats();
            if (window.mapManager) window.mapManager.loadGeofences();
        } catch (err) {
            window.showToast('Failed to create geofence: ' + err.message, 'danger');
        }
    }

    async deleteGeofence(id) {
        if (!confirm('Are you sure you want to remove this geofence?')) return;
        try {
            await api.deleteGeofence(id);
            window.showToast('Geofence removed.', 'info');
            this.loadStats();
            if (window.mapManager) window.mapManager.loadGeofences();
        } catch (err) {
            window.showToast('Failed to delete geofence: ' + err.message, 'danger');
        }
    }
}

const admin = new AdminManager();
window.admin = admin;
