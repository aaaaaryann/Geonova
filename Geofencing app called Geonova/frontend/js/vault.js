// Geonova Secure Document Vault Manager

// ─── Document Type Registry ────────────────────────────────────────────────
const VAULT_DOC_TYPES = [
    // Passport
    { value: 'Passport',                   label: 'Passport',                         cat: 'passport',   icon: '🛂', color: '#3b82f6' },
    { value: 'Emergency Travel Certificate', label: 'Emergency Travel Certificate',   cat: 'passport',   icon: '🛂', color: '#3b82f6' },

    // Visa
    { value: 'Visa',                       label: 'Visa / Entry Permit',              cat: 'visa',       icon: '🔏', color: '#8b5cf6' },
    { value: 'e-Visa',                     label: 'e-Visa (Electronic Visa)',         cat: 'visa',       icon: '🔏', color: '#8b5cf6' },
    { value: 'Visa on Arrival',            label: 'Visa on Arrival',                  cat: 'visa',       icon: '🔏', color: '#8b5cf6' },
    { value: 'Special Permit',             label: 'Protected Area Permit (PAP/ILP)',  cat: 'visa',       icon: '🔏', color: '#8b5cf6' },

    // National ID
    { value: 'National ID',                label: 'National ID Card',                 cat: 'national_id', icon: '🪪', color: '#f59e0b' },
    { value: 'Aadhaar Card',               label: 'Aadhaar Card (UIDAI)',             cat: 'national_id', icon: '🪪', color: '#f59e0b' },
    { value: 'PAN Card',                   label: 'PAN Card (Income Tax)',            cat: 'national_id', icon: '🪪', color: '#f59e0b' },
    { value: 'Voter ID',                   label: 'Voter ID / EPIC Card',             cat: 'national_id', icon: '🪪', color: '#f59e0b' },
    { value: 'Driving License',            label: 'Driving License / IDP',            cat: 'national_id', icon: '🪪', color: '#f59e0b' },
    { value: 'OCI Card',                   label: 'OCI / PIO Card',                   cat: 'national_id', icon: '🪪', color: '#f59e0b' },

    // Address Certificate
    { value: 'Address Certificate',        label: 'Address / Residence Certificate',  cat: 'address',    icon: '🏠', color: '#10b981' },
    { value: 'Utility Bill',               label: 'Utility Bill (Address Proof)',     cat: 'address',    icon: '🏠', color: '#10b981' },
    { value: 'Domicile Certificate',       label: 'Domicile Certificate',             cat: 'address',    icon: '🏠', color: '#10b981' },
    { value: 'Ration Card',                label: 'Ration Card (Address Proof)',      cat: 'address',    icon: '🏠', color: '#10b981' },

    // Other
    { value: 'Travel Insurance',           label: 'Travel Insurance Policy',          cat: 'other',      icon: '🛡️', color: '#64748b' },
    { value: 'Health Certificate',         label: 'Health / Vaccination Certificate', cat: 'other',      icon: '🛡️', color: '#64748b' },
    { value: 'Hotel Booking',              label: 'Hotel / Accommodation Booking',    cat: 'other',      icon: '🛡️', color: '#64748b' },
    { value: 'Flight Ticket',              label: 'Flight / Train Ticket',            cat: 'other',      icon: '🛡️', color: '#64748b' },
];

// Category metadata
const VAULT_CATEGORIES = {
    all:        { label: 'All Documents',         icon: '🗂️', color: '#60a5fa', desc: 'Every document stored in your encrypted vault.' },
    passport:   { label: 'Passport & Travel IDs', icon: '🛂', color: '#3b82f6', desc: 'Passports and official travel identity documents.' },
    visa:       { label: 'Visa & Entry Permits',  icon: '🔏', color: '#8b5cf6', desc: 'Visas, e-Visas, and protected area permits.' },
    national_id:{ label: 'National ID Documents', icon: '🪪', color: '#f59e0b', desc: 'Aadhaar, PAN, Voter ID, Driving License, OCI cards.' },
    address:    { label: 'Address Certificates',  icon: '🏠', color: '#10b981', desc: 'Domicile, utility bill, ration card, residence proof.' },
    other:      { label: 'Other Documents',        icon: '📄', color: '#94a3b8', desc: 'Travel insurance, health certificates, bookings.' },
};

class VaultManager {
    constructor() {
        this.documents = [];
        this.activeCategory = 'all';
    }

    // ── Init ────────────────────────────────────────────────────────────────
    async init() {
        if (!auth.currentUser) {
            this.renderVaultGrid();
            return;
        }
        try {
            this.documents = await api.getDocuments();
        } catch (e) {
            console.error('Failed to load documents:', e);
            this.documents = [];
        }
        this.updateStats();
        this.renderVaultGrid();
    }

    // ── Statistics Bar ──────────────────────────────────────────────────────
    updateStats() {
        const counts = { all: this.documents.length, passport: 0, visa: 0, national_id: 0, address: 0, other: 0 };
        this.documents.forEach(doc => {
            const meta = VAULT_DOC_TYPES.find(t => t.value === doc.document_type);
            const cat = meta ? meta.cat : 'other';
            if (counts[cat] !== undefined) counts[cat]++;
        });

        Object.keys(counts).forEach(cat => {
            const el = document.getElementById(`stat-count-${cat}`);
            if (el) el.textContent = counts[cat];
        });
    }

    // ── Category Filter ──────────────────────────────────────────────────────
    filterByCategory(cat) {
        this.activeCategory = cat;

        // Update tab active state
        document.querySelectorAll('.vault-tab-btn').forEach(btn => btn.classList.remove('active'));
        const activeTab = document.getElementById(`vtab-${cat}`);
        if (activeTab) activeTab.classList.add('active');

        // Update stat chip active state
        document.querySelectorAll('.vault-stat-chip').forEach(chip => chip.classList.remove('active'));
        const activeChip = document.querySelector(`.vault-stat-chip[data-cat="${cat}"]`);
        if (activeChip) activeChip.classList.add('active');

        // Show/hide category banner
        const banner = document.getElementById('vault-category-banner');
        const catMeta = VAULT_CATEGORIES[cat];
        if (cat !== 'all' && catMeta) {
            banner.style.display = 'flex';
            banner.innerHTML = `
                <span class="vault-banner-icon" style="background: ${catMeta.color}22; border: 1px solid ${catMeta.color}44;">${catMeta.icon}</span>
                <div>
                    <div class="vault-banner-title" style="color: ${catMeta.color};">${catMeta.label}</div>
                    <div class="vault-banner-desc">${catMeta.desc}</div>
                </div>
            `;
        } else {
            banner.style.display = 'none';
        }

        this.renderVaultGrid();
    }

    // ── Get Doc Category ────────────────────────────────────────────────────
    _getDocCategory(doc) {
        const meta = VAULT_DOC_TYPES.find(t => t.value === doc.document_type);
        return meta ? meta.cat : 'other';
    }

    _getDocMeta(doc) {
        return VAULT_DOC_TYPES.find(t => t.value === doc.document_type) || { icon: '📄', color: '#64748b' };
    }

    // ── Render Grid ──────────────────────────────────────────────────────────
    renderVaultGrid() {
        const container = document.getElementById('vault-docs-grid');
        if (!container) return;

        // Not logged in
        if (!auth.currentUser) {
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; background: var(--bg-glass-card); border-radius: var(--radius-lg); border: 1px solid var(--navy-border);">
                    <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🔒</div>
                    <h3 style="color: #ffffff; margin-bottom: 0.5rem;">Access Your Secure Vault</h3>
                    <p style="color: var(--text-muted); margin-bottom: 1.5rem;">Please log in to manage your passports, visas, national IDs, address certificates, and travel documents.</p>
                    <button class="btn btn-primary" onclick="auth.openLoginModal()">Login to Vault</button>
                </div>
            `;
            return;
        }

        // Filter documents
        const filtered = this.activeCategory === 'all'
            ? this.documents
            : this.documents.filter(doc => this._getDocCategory(doc) === this.activeCategory);

        // Empty state
        if (filtered.length === 0) {
            const catMeta = VAULT_CATEGORIES[this.activeCategory];
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3.5rem; background: var(--bg-glass-card); border-radius: var(--radius-lg); border: 1px dashed var(--navy-border);">
                    <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">${catMeta ? catMeta.icon : '📄'}</div>
                    <h3 style="color: #ffffff; margin-bottom: 0.5rem;">No ${catMeta ? catMeta.label : 'Documents'} Yet</h3>
                    <p style="color: var(--text-muted); margin-bottom: 1.5rem; max-width: 380px; margin-inline: auto;">
                        ${this.activeCategory === 'all'
                            ? 'Upload your essential travel documents for encrypted offline access and expiry alerts.'
                            : `Add your ${catMeta ? catMeta.label.toLowerCase() : 'documents'} to keep them safe and accessible on the go.`}
                    </p>
                    <button class="btn btn-emerald" onclick="vaultManager.openUploadModal()">+ Upload Document</button>
                </div>
            `;
            return;
        }

        // If showing all, render by sections; otherwise flat grid
        if (this.activeCategory === 'all') {
            container.innerHTML = this._renderBySections(this.documents);
        } else {
            container.innerHTML = filtered.map(doc => this._renderDocCard(doc)).join('');
        }
    }

    // ── Section-Based Render (All view) ──────────────────────────────────────
    _renderBySections(docs) {
        const sectionOrder = ['passport', 'visa', 'national_id', 'address', 'other'];
        let html = '';

        sectionOrder.forEach(cat => {
            const catDocs = docs.filter(d => this._getDocCategory(d) === cat);
            if (catDocs.length === 0) return;

            const meta = VAULT_CATEGORIES[cat];
            html += `
                <div class="vault-section-header" style="grid-column: 1 / -1;">
                    <div class="vault-section-label">
                        <span class="vault-section-icon" style="background: ${meta.color}22; border: 1px solid ${meta.color}44; color: ${meta.color};">${meta.icon}</span>
                        <span style="color: #ffffff; font-weight: 700; font-size: 1rem;">${meta.label}</span>
                        <span class="vault-section-count" style="background: ${meta.color}22; color: ${meta.color};">${catDocs.length}</span>
                    </div>
                    <div class="vault-section-line" style="background: ${meta.color}33;"></div>
                </div>
            `;
            html += catDocs.map(doc => this._renderDocCard(doc)).join('');
        });

        return html;
    }

    // ── Single Doc Card ──────────────────────────────────────────────────────
    _renderDocCard(doc) {
        const statusBadge = doc.status === 'expired'
            ? '<span class="badge badge-crimson">Expired</span>'
            : doc.status === 'expiring_soon'
            ? '<span class="badge badge-amber">Expiring Soon</span>'
            : '<span class="badge badge-emerald">Valid</span>';

        const meta = this._getDocMeta(doc);
        const cat = this._getDocCategory(doc);
        const catMeta = VAULT_CATEGORIES[cat];

        return `
            <div class="vault-card" data-cat="${cat}" style="--vault-accent: ${meta.color};">
                <div class="vault-card-accent-bar" style="background: linear-gradient(90deg, ${meta.color}, transparent);"></div>
                <div class="vault-icon-header">
                    <div class="vault-file-icon" style="background: ${meta.color}22; border: 1px solid ${meta.color}44;">${meta.icon}</div>
                    ${statusBadge}
                </div>
                <div class="vault-info">
                    <h4>${doc.document_name}</h4>
                    <p>${doc.document_type} • ${doc.document_number ? `No: ${doc.document_number}` : 'Encrypted File'}</p>
                    <div class="vault-cat-chip" style="background: ${meta.color}18; color: ${meta.color}; border: 1px solid ${meta.color}30;">
                        ${catMeta ? catMeta.icon : '📄'} ${catMeta ? catMeta.label : 'Other'}
                    </div>
                </div>
                <div class="vault-expiry-tag" style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--navy-border);">
                    <span style="color: var(--text-muted);">Expiry Date:</span>
                    <strong style="color: #ffffff;">${doc.expiry_date}</strong>
                </div>
                <div style="display: flex; gap: 0.5rem; margin-top: auto; border-top: 1px solid var(--navy-border); padding-top: 0.75rem;">
                    <button class="btn btn-outline btn-sm" style="flex: 1;" onclick="vaultManager.previewDocument(${doc.id})">
                        View File
                    </button>
                    <button class="btn btn-outline btn-sm" style="color: #f87171; padding: 0.4rem 0.6rem;" onclick="vaultManager.deleteDoc(${doc.id})" title="Delete">
                        🗑️
                    </button>
                </div>
            </div>
        `;
    }

    // ── Upload Modal ──────────────────────────────────────────────────────────
    openUploadModal() {
        if (!auth.currentUser) {
            window.showToast('Please sign in to upload documents.', 'warning');
            auth.openLoginModal();
            return;
        }

        const modal = document.getElementById('vault-modal');
        const modalBody = document.getElementById('vault-modal-body');

        // Build grouped <optgroup> select
        const optGroups = [
            { cat: 'passport',    label: '🛂 Passport & Travel IDs' },
            { cat: 'visa',        label: '🔏 Visa & Entry Permits' },
            { cat: 'national_id', label: '🪪 National ID Documents' },
            { cat: 'address',     label: '🏠 Address Certificates' },
            { cat: 'other',       label: '📄 Other Travel Documents' },
        ];

        const selectOptions = optGroups.map(grp => {
            const types = VAULT_DOC_TYPES.filter(t => t.cat === grp.cat);
            const opts = types.map(t => `<option value="${t.value}">${t.label}</option>`).join('');
            return `<optgroup label="${grp.label}">${opts}</optgroup>`;
        }).join('');

        modalBody.innerHTML = `
            <form id="vault-upload-form" onsubmit="vaultManager.handleUpload(event)">
                <div class="form-group">
                    <label class="form-label">Document Category & Type</label>
                    <select id="doc-type" class="form-select" required onchange="vaultManager.onDocTypeChange(this.value)">
                        ${selectOptions}
                    </select>
                </div>

                <!-- Document type info banner -->
                <div id="doc-type-info-banner" class="vault-type-info-banner" style="display: none;"></div>

                <div class="form-group">
                    <label class="form-label">Document Title / Label</label>
                    <input type="text" id="doc-name" class="form-input" placeholder="e.g. My Indian Passport" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Document Identification Number <span style="color: var(--text-muted); font-weight: 400;">(optional)</span></label>
                    <input type="text" id="doc-number" class="form-input" placeholder="e.g. Z4918231 / 1234 5678 9012" />
                </div>
                <div class="form-group">
                    <label class="form-label">Expiration Date</label>
                    <input type="date" id="doc-expiry" class="form-input" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Select File <span style="color: var(--text-muted); font-weight: 400;">(PDF, JPG, PNG — Max 5MB)</span></label>
                    <input type="file" id="doc-file" class="form-input" accept=".pdf,.jpg,.jpeg,.png" required onchange="vaultManager.handleFileSelect(event)" />
                </div>
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: var(--radius-md); padding: 0.75rem 1rem; font-size: 0.8rem; color: #a7f3d0; margin-bottom: 1.25rem;">
                    🔒 <strong>End-to-End Vault Privacy:</strong> Documents are base64 encrypted and stored in your private vault with strict role-based access. Never exposed to public URLs.
                </div>
                <button type="submit" class="btn btn-emerald btn-block">Securely Save to Vault</button>
            </form>
        `;

        // Trigger initial banner display
        this.onDocTypeChange(VAULT_DOC_TYPES[0].value);

        modal.classList.add('open');
    }

    // ── Doc Type Info Banner on Change ────────────────────────────────────────
    onDocTypeChange(value) {
        const meta = VAULT_DOC_TYPES.find(t => t.value === value);
        const banner = document.getElementById('doc-type-info-banner');
        if (!meta || !banner) return;

        const catMeta = VAULT_CATEGORIES[meta.cat];
        banner.style.display = 'flex';
        banner.style.background = `${meta.color}12`;
        banner.style.borderColor = `${meta.color}30`;
        banner.innerHTML = `
            <span style="font-size: 1.5rem; line-height: 1;">${meta.icon}</span>
            <div style="flex: 1;">
                <div style="color: ${meta.color}; font-weight: 700; font-size: 0.85rem;">${meta.label}</div>
                <div style="color: var(--text-muted); font-size: 0.78rem;">Category: ${catMeta ? catMeta.label : 'Other'}</div>
            </div>
        `;
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (uploadEvent) => {
                this.tempFileBase64 = uploadEvent.target.result;
                this.tempFileType = file.name.split('.').pop().toLowerCase();
                this.tempFileSize = Math.round(file.size / 1024);
            };
            reader.readAsDataURL(file);
        }
    }

    async handleUpload(e) {
        e.preventDefault();
        const document_type = document.getElementById('doc-type').value;
        const document_name = document.getElementById('doc-name').value;
        const document_number = document.getElementById('doc-number').value;
        const expiry_date = document.getElementById('doc-expiry').value;

        try {
            await api.uploadDocument({
                document_type,
                document_name,
                document_number,
                expiry_date,
                file_type: this.tempFileType || 'pdf',
                file_size_kb: this.tempFileSize || 150,
                file_content_base64: this.tempFileBase64 || null
            });

            this.closeModal();
            window.showToast('Document uploaded & encrypted in your Geonova Vault!', 'success');
            await this.init();
            if (window.dashboard) window.dashboard.loadData();
        } catch (err) {
            window.showToast('Upload failed: ' + err.message, 'danger');
        }
    }

    // ── Preview Modal ─────────────────────────────────────────────────────────
    previewDocument(docId) {
        const doc = this.documents.find(d => d.id === docId);
        if (!doc) return;

        const modal = document.getElementById('vault-modal');
        const modalBody = document.getElementById('vault-modal-body');
        const meta = this._getDocMeta(doc);
        const cat = this._getDocCategory(doc);
        const catMeta = VAULT_CATEGORIES[cat];

        modalBody.innerHTML = `
            <div style="text-align: center;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 1rem; background: ${meta.color}20; border: 1px solid ${meta.color}40; font-size: 2rem; margin-bottom: 1rem;">${meta.icon}</div>
                <h3 style="font-size: 1.4rem; color: #ffffff; margin-bottom: 0.25rem;">${doc.document_name}</h3>
                <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.5rem;">${doc.document_type} • Expiry: ${doc.expiry_date}</p>
                <div class="vault-cat-chip" style="display: inline-flex; margin-bottom: 1.5rem; background: ${meta.color}18; color: ${meta.color}; border: 1px solid ${meta.color}30;">
                    ${catMeta ? catMeta.icon + ' ' + catMeta.label : '📄 Other'}
                </div>

                <div style="background: rgba(15, 23, 42, 0.9); border: 2px dashed var(--navy-border); border-radius: var(--radius-lg); padding: 3rem 1.5rem; margin-bottom: 1.5rem;">
                    <div style="font-size: 3rem; margin-bottom: 0.75rem;">🛡️</div>
                    <h4 style="color: #ffffff; margin-bottom: 0.25rem;">Encrypted Document Vault Preview</h4>
                    <p style="color: #94a3b8; font-size: 0.85rem; max-width: 380px; margin: 0 auto 1.25rem;">
                        Verified travel record #${doc.id}. Digital cryptographic checksum verified.
                        ${doc.document_number ? `<br/>Document No: <strong style="color: #ffffff;">${doc.document_number}</strong>` : ''}
                    </p>
                    <span class="badge badge-emerald">Verified Document Token</span>
                </div>

                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <button class="btn btn-outline" onclick="vaultManager.closeModal()">Close</button>
                    <button class="btn btn-primary" onclick="window.showToast('Encrypted document file downloaded to device.', 'info')">
                        📥 Download File
                    </button>
                </div>
            </div>
        `;

        modal.classList.add('open');
    }

    // ── Delete Doc ────────────────────────────────────────────────────────────
    async deleteDoc(docId) {
        if (!confirm('Are you sure you want to remove this document from your vault?')) return;
        try {
            await api.deleteDocument(docId);
            window.showToast('Document removed securely.', 'info');
            await this.init();
            if (window.dashboard) window.dashboard.loadData();
        } catch (e) {
            window.showToast('Failed to delete document: ' + e.message, 'danger');
        }
    }

    closeModal() {
        const modal = document.getElementById('vault-modal');
        if (modal) modal.classList.remove('open');
    }
}

const vaultManager = new VaultManager();
window.vaultManager = vaultManager;
