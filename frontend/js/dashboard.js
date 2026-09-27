// Geonova Tourist Personal Dashboard Manager

class DashboardManager {
    constructor() {
        this.activeTab = 'overview';
    }

    async init() {
        this.loadData();
    }

    async loadData() {
        if (!auth.currentUser) return;

        try {
            const [contacts, docs, bookings, invoices] = await Promise.all([
                api.getEmergencyContacts().catch(() => []),
                api.getDocuments().catch(() => []),
                api.getMyBookings().catch(() => []),
                api.getInvoices().catch(() => [])
            ]);

            this.renderDashboard(contacts, docs, bookings, invoices);
        } catch (e) {
            console.error('Failed to load dashboard data:', e);
        }
    }

    renderDashboard(contacts, docs, bookings, invoices) {
        const container = document.getElementById('dashboard-view');
        if (!container) return;

        if (!auth.currentUser) {
            container.innerHTML = `
                <div style="text-align: center; padding: 4rem; background: var(--bg-glass-card); border-radius: var(--radius-xl); border: 1px solid var(--navy-border);">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🧭</div>
                    <h2 style="color: #ffffff; margin-bottom: 0.5rem;">Tourist Dashboard</h2>
                    <p style="color: var(--text-muted); margin-bottom: 1.5rem;">Sign in to view your live trip tracking, emergency contacts, documents, and bookings.</p>
                    <button class="btn btn-primary" onclick="auth.openLoginModal()">Login to Dashboard</button>
                </div>
            `;
            return;
        }

        const expiringDocs = docs.filter(d => d.status === 'expiring_soon' || d.status === 'expired');

        container.innerHTML = `
            <div class="dashboard-grid">
                <!-- Sidebar -->
                <aside class="dashboard-sidebar">
                    <div class="user-profile-summary">
                        <div class="user-avatar-circle">
                            ${auth.currentUser.full_name.charAt(0)}
                        </div>
                        <h3 style="color: #ffffff; font-size: 1.2rem; margin-bottom: 0.25rem;">${auth.currentUser.full_name}</h3>
                        <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.5rem;">${auth.currentUser.email}</p>
                        <span class="badge badge-emerald">${auth.currentUser.nationality} Traveler</span>
                    </div>

                    <ul class="sidebar-menu">
                        <li class="sidebar-menu-item active" onclick="dashboard.switchTab('overview', this)">
                            📊 Trip Overview
                        </li>
                        <li class="sidebar-menu-item" onclick="dashboard.switchTab('contacts', this)">
                            🛡️ Emergency Contacts (${contacts.length})
                        </li>
                        <li class="sidebar-menu-item" onclick="dashboard.switchTab('bookings', this)">
                            🧳 Booked Tours (${bookings.length})
                        </li>
                        <li class="sidebar-menu-item" onclick="dashboard.switchTab('invoices', this)">
                            🧾 Invoices & Payments (${invoices.length})
                        </li>
                    </ul>

                    <div style="margin-top: 2rem; padding: 1rem; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: var(--radius-md); text-align: center;">
                        <span style="font-size: 0.75rem; color: var(--safe-emerald-light); font-weight: 700; text-transform: uppercase;">Active Protection</span>
                        <h4 style="color: #ffffff; margin: 4px 0 8px 0; font-size: 0.95rem;">Geonova Shield</h4>
                        <button class="btn btn-outline btn-sm btn-block" onclick="app.navigate('pricing')">Manage Plan</button>
                    </div>
                </aside>

                <!-- Main Content Area -->
                <div class="dashboard-content-area">
                    <!-- KPI Cards Grid -->
                    <div class="stats-cards-grid">
                        <div class="stat-card">
                            <div class="stat-card-info">
                                <h5>Active Status</h5>
                                <div class="stat-card-value" style="font-size: 1.3rem; color: var(--safe-emerald-light);">Protected</div>
                            </div>
                            <div class="stat-card-icon stat-icon-emerald">🛡️</div>
                        </div>

                        <div class="stat-card">
                            <div class="stat-card-info">
                                <h5>Emergency Contacts</h5>
                                <div class="stat-card-value">${contacts.length}</div>
                            </div>
                            <div class="stat-card-icon stat-icon-blue">👥</div>
                        </div>

                        <div class="stat-card">
                            <div class="stat-card-info">
                                <h5>Vault Documents</h5>
                                <div class="stat-card-value">${docs.length}</div>
                            </div>
                            <div class="stat-card-icon stat-icon-amber">📑</div>
                        </div>

                        <div class="stat-card">
                            <div class="stat-card-info">
                                <h5>Booked Tours</h5>
                                <div class="stat-card-value">${bookings.length}</div>
                            </div>
                            <div class="stat-card-icon stat-icon-crimson">✈️</div>
                        </div>
                    </div>

                    ${expiringDocs.length > 0 ? `
                        <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: var(--radius-lg); padding: 1rem 1.25rem; display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <span style="font-size: 1.5rem;">⚠️</span>
                                <div>
                                    <strong style="color: var(--alert-amber-light); font-size: 0.95rem;">Document Expiry Alert:</strong>
                                    <div style="color: #ffffff; font-size: 0.85rem;">You have ${expiringDocs.length} document(s) expiring soon or expired.</div>
                                </div>
                            </div>
                            <button class="btn btn-outline btn-sm" onclick="app.navigate('vault')">Inspect Vault</button>
                        </div>
                    ` : ''}

                    <!-- Tab Pane: Overview -->
                    <div id="tab-overview" class="dash-tab-pane">
                        <div class="data-table-container">
                            <div class="data-table-header">
                                <h3 style="color: #ffffff; font-size: 1.2rem;">Live Geonova Trip Radar</h3>
                                <button class="btn btn-outline btn-sm" onclick="app.navigate('map')">Open Full Map</button>
                            </div>
                            <div style="padding: 1.5rem;">
                                <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem;">
                                    Your live location is encrypted and monitored against verified hazardous and restricted geofences.
                                </p>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                                    <div style="background: rgba(15, 23, 42, 0.6); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--navy-border);">
                                        <span style="color: var(--text-muted); font-size: 0.75rem;">CURRENT ZONE</span>
                                        <div style="font-weight: 700; color: #ffffff; margin-top: 4px;">Connaught Place Safe Corridor</div>
                                    </div>
                                    <div style="background: rgba(15, 23, 42, 0.6); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--navy-border);">
                                        <span style="color: var(--text-muted); font-size: 0.75rem;">NEAREST TOURIST POLICE</span>
                                        <div style="font-weight: 700; color: #60a5fa; margin-top: 4px;">Janpath Tourist Station (450m)</div>
                                    </div>
                                    <div style="background: rgba(15, 23, 42, 0.6); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--navy-border);">
                                        <span style="color: var(--text-muted); font-size: 0.75rem;">NEAREST EMERGENCY TRAUMA</span>
                                        <div style="font-weight: 700; color: #f87171; margin-top: 4px;">AIIMS New Delhi (3.2 km)</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Tab Pane: Contacts -->
                    <div id="tab-contacts" class="dash-tab-pane" style="display: none;">
                        <div class="data-table-container">
                            <div class="data-table-header">
                                <h3 style="color: #ffffff; font-size: 1.2rem;">Emergency Contacts Directory</h3>
                                <button class="btn btn-emerald btn-sm" onclick="dashboard.openAddContactModal()">+ Add Contact</button>
                            </div>
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Relationship</th>
                                        <th>Phone Number</th>
                                        <th>Primary Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${contacts.map(c => `
                                        <tr>
                                            <td><strong>${c.name}</strong></td>
                                            <td>${c.relationship_type}</td>
                                            <td><a href="tel:${c.phone_number}" style="color: #60a5fa;">${c.phone_number}</a></td>
                                            <td>${c.is_primary ? '<span class="badge badge-emerald">Primary Contact</span>' : '<span class="badge badge-blue">Secondary</span>'}</td>
                                            <td>
                                                <button class="btn btn-outline btn-sm" style="color: #f87171; padding: 0.3rem 0.6rem;" onclick="dashboard.deleteContact(${c.id})">Remove</button>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Tab Pane: Bookings -->
                    <div id="tab-bookings" class="dash-tab-pane" style="display: none;">
                        <div class="data-table-container">
                            <div class="data-table-header">
                                <h3 style="color: #ffffff; font-size: 1.2rem;">My Booked Tour Packages</h3>
                                <button class="btn btn-primary btn-sm" onclick="app.navigate('packages')">Explore More Tours</button>
                            </div>
                            ${bookings.length === 0 ? `
                                <div style="text-align: center; padding: 3rem; color: var(--text-muted);">No tour bookings found yet.</div>
                            ` : `
                                <table class="data-table">
                                    <thead>
                                        <tr>
                                            <th>Reference</th>
                                            <th>Package</th>
                                            <th>Travel Date</th>
                                            <th>Travelers</th>
                                            <th>Total Paid</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${bookings.map(b => `
                                            <tr>
                                                <td><strong style="color: #60a5fa;">${b.booking_reference}</strong></td>
                                                <td>${b.package_title}</td>
                                                <td>${b.travel_date}</td>
                                                <td>${b.travelers_count}</td>
                                                <td style="color: var(--safe-emerald-light); font-weight: 700;">₹${b.total_amount.toLocaleString()}</td>
                                                <td><span class="badge badge-emerald">${b.booking_status}</span></td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            `}
                        </div>
                    </div>

                    <!-- Tab Pane: Invoices -->
                    <div id="tab-invoices" class="dash-tab-pane" style="display: none;">
                        <div class="data-table-container">
                            <div class="data-table-header">
                                <h3 style="color: #ffffff; font-size: 1.2rem;">Payment History & Official Invoices</h3>
                            </div>
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Invoice #</th>
                                        <th>Transaction ID</th>
                                        <th>Amount</th>
                                        <th>Payment Mode</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${invoices.map(inv => `
                                        <tr>
                                            <td><strong>${inv.invoice_number}</strong></td>
                                            <td style="color: var(--text-muted); font-size: 0.8rem;">${inv.transaction_id}</td>
                                            <td style="font-weight: 700;">₹${inv.amount.toLocaleString()}</td>
                                            <td>${inv.payment_method}</td>
                                            <td><span class="badge badge-emerald">${inv.status}</span></td>
                                            <td>
                                                <button class="btn btn-outline btn-sm" onclick="window.print()">Print</button>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    switchTab(tabKey, clickedElem) {
        document.querySelectorAll('.sidebar-menu-item').forEach(i => i.classList.remove('active'));
        if (clickedElem) clickedElem.classList.add('active');

        document.querySelectorAll('.dash-tab-pane').forEach(p => p.style.display = 'none');
        const target = document.getElementById(`tab-${tabKey}`);
        if (target) target.style.display = 'block';
    }

    openAddContactModal() {
        const modal = document.getElementById('auth-modal');
        const modalBody = document.getElementById('auth-modal-body');
        const modalTitle = document.getElementById('auth-modal-title');

        modalTitle.textContent = 'Add Emergency Contact';
        modalBody.innerHTML = `
            <form onsubmit="dashboard.handleAddContact(event)">
                <div class="form-group">
                    <label class="form-label">Contact Full Name</label>
                    <input type="text" id="contact-name" class="form-input" placeholder="e.g. Sunita Sharma" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Relationship</label>
                    <select id="contact-rel" class="form-select">
                        <option value="Parent">Parent</option>
                        <option value="Spouse">Spouse / Partner</option>
                        <option value="Sibling">Sibling</option>
                        <option value="Friend">Friend / Traveling Companion</option>
                        <option value="Guardian">Guardian</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Phone Number (with Country Code)</label>
                    <input type="tel" id="contact-phone" class="form-input" placeholder="+91 9811122233" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Email Address (Optional)</label>
                    <input type="email" id="contact-email" class="form-input" placeholder="contact@example.com" />
                </div>
                <button type="submit" class="btn btn-emerald btn-block" style="margin-top: 1rem;">Save Emergency Contact</button>
            </form>
        `;

        modal.classList.add('open');
    }

    async handleAddContact(e) {
        e.preventDefault();
        const name = document.getElementById('contact-name').value;
        const relationship_type = document.getElementById('contact-rel').value;
        const phone_number = document.getElementById('contact-phone').value;
        const email = document.getElementById('contact-email').value;

        try {
            await api.addEmergencyContact({ name, relationship_type, phone_number, email });
            auth.closeModal();
            window.showToast('Emergency contact added successfully!', 'success');
            this.loadData();
        } catch (err) {
            window.showToast('Failed to add contact: ' + err.message, 'danger');
        }
    }

    async deleteContact(id) {
        if (!confirm('Are you sure you want to remove this emergency contact?')) return;
        try {
            await api.deleteEmergencyContact(id);
            window.showToast('Contact removed.', 'info');
            this.loadData();
        } catch (err) {
            window.showToast('Failed to delete contact: ' + err.message, 'danger');
        }
    }
}

const dashboard = new DashboardManager();
window.dashboard = dashboard;
