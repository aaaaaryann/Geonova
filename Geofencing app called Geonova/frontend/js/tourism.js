// Geonova 36 States & Union Territories Tourism Explorer

class TourismManager {
    constructor() {
        this.states = [];
        this.filteredStates = [];
        this.activeRegion = 'all';
    }

    // Gradient placeholder shown when an image fails to load
    getStatePlaceholder(label, gradient) {
        const gradients = [
            'linear-gradient(135deg,#1e3a5f,#0f5132)',
            'linear-gradient(135deg,#3d1f5c,#1a3a6e)',
            'linear-gradient(135deg,#1a4731,#0d3260)',
            'linear-gradient(135deg,#5c1a1a,#3d1a5c)',
            'linear-gradient(135deg,#1a3a5c,#5c3a1a)',
            'linear-gradient(135deg,#0f3460,#533483)',
            'linear-gradient(135deg,#1b4332,#2d6a4f)',
        ];
        const bg = gradient || gradients[Math.abs(label.charCodeAt(0) + label.charCodeAt(1)) % gradients.length];
        return `<div style="width:100%;height:100%;background:${bg};display:flex;align-items:center;justify-content:center;flex-direction:column;gap:0.5rem;">
            <span style="font-size:2.5rem;">🏛️</span>
            <span style="color:rgba(255,255,255,0.8);font-size:0.85rem;font-weight:600;text-align:center;padding:0 0.5rem;">${label}</span>
        </div>`;
    }

    async init() {
        try {
            this.states = await api.getStates();
            this.filteredStates = [...this.states];
            this.renderStatesGrid();
        } catch (e) {
            console.error('Failed to load states:', e);
        }
    }

    filterByRegion(region, btnElem) {
        this.activeRegion = region;
        document.querySelectorAll('#region-filter-tabs .tab-btn').forEach(b => b.classList.remove('active'));
        if (btnElem) btnElem.classList.add('active');

        if (region === 'all') {
            this.filteredStates = [...this.states];
        } else {
            this.filteredStates = this.states.filter(s => s.region.toLowerCase().includes(region.toLowerCase()));
        }
        this.renderStatesGrid();
    }

    searchStates(query) {
        const q = query.trim().toLowerCase();
        if (!q) {
            this.filterByRegion(this.activeRegion);
            return;
        }

        this.filteredStates = this.states.filter(s => 
            s.name.toLowerCase().includes(q) || 
            s.capital.toLowerCase().includes(q) ||
            s.description.toLowerCase().includes(q)
        );
        this.renderStatesGrid();
    }

    renderStatesGrid() {
        const container = document.getElementById('states-cards-grid');
        const countDisplay = document.getElementById('states-count-badge');
        if (!container) return;

        if (countDisplay) {
            countDisplay.textContent = `Showing ${this.filteredStates.length} of ${this.states.length} States & UTs`;
        }

        if (this.filteredStates.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">
                    <h3>No destinations matched your criteria.</h3>
                    <p>Try clearing filters or searching for another Indian state.</p>
                </div>
            `;
            return;
        }
            const stateDataOverrides = {
            'AP': { famous: 'Tirupati Balaji Temple', image: 'https://upload.wikimedia.org/wikipedia/commons/4/41/Tirumala_090615.jpg' },
            'AR': { famous: 'Tawang Monastery', image: 'https://upload.wikimedia.org/wikipedia/commons/6/6c/Tawang_Monastery_%282018%29.jpg' },
            'AS': { famous: 'Kaziranga National Park', image: 'https://upload.wikimedia.org/wikipedia/commons/4/41/Kaziranga_National_Park_Elephant_Safari.jpg' },
            'BR': { famous: 'Mahabodhi Temple, Bodh Gaya', image: 'https://upload.wikimedia.org/wikipedia/commons/6/6f/Mahabodhi_temple%2C_Bodh_Gaya.jpg' },
            'CT': { famous: 'Chitrakote Waterfalls', image: 'https://upload.wikimedia.org/wikipedia/commons/2/23/Chitrakoot_Waterfalls_Bastar.jpg' },
            'GA': { famous: 'Baga Beach & Nightlife', image: 'https://upload.wikimedia.org/wikipedia/commons/3/3e/Palolem_Beach_Goa.jpg' },
            'GJ': { famous: 'Statue of Unity', image: 'https://upload.wikimedia.org/wikipedia/commons/3/30/Statue_of_Unity%2C_Kevadia%2C_India.jpg' },
            'HR': { famous: 'Sultanpur National Park', image: 'https://upload.wikimedia.org/wikipedia/commons/0/07/Brahma_Sarovar_Kurukshetra.jpg' },
            'HP': { famous: 'Manali & Rohtang Pass', image: 'https://upload.wikimedia.org/wikipedia/commons/1/1a/Rohtang_Pass_Manali.jpg' },
            'JH': { famous: 'Baidyanath Jyotirlinga', image: 'https://upload.wikimedia.org/wikipedia/commons/6/68/Baidyanath_Jyotirlinga_temple.jpg' },
            'KA': { famous: 'Mysore Palace & Hampi', image: 'https://upload.wikimedia.org/wikipedia/commons/e/e5/Mysore_Palace_Morning.jpg' },
            'KL': { famous: 'Alleppey Backwaters', image: 'https://upload.wikimedia.org/wikipedia/commons/0/05/Kerala_backwaters.jpg' },
            'MP': { famous: 'Khajuraho Temples', image: 'https://upload.wikimedia.org/wikipedia/commons/d/dd/Khajuraho_Lakshmana_Temple.jpg' },
            'MH': { famous: 'Gateway of India', image: 'https://upload.wikimedia.org/wikipedia/commons/0/01/Gateway_of_India%2C_Mumbai.jpg' },
            'MN': { famous: 'Loktak Lake', image: 'https://upload.wikimedia.org/wikipedia/commons/6/62/Loktak_Lake_Manipur.jpg' },
            'ML': { famous: 'Living Root Bridges', image: 'https://upload.wikimedia.org/wikipedia/commons/2/23/Living_root_bridge_Mawlynnong.jpg' },
            'MZ': { famous: 'Phawngpui Blue Mountain', image: 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Aizawl_city_view.jpg' },
            'NL': { famous: 'Hornbill Festival', image: 'https://upload.wikimedia.org/wikipedia/commons/5/52/Hornbill_festival_Kohima.jpg' },
            'OD': { famous: 'Konark Sun Temple', image: 'https://upload.wikimedia.org/wikipedia/commons/9/91/Konark_Sun_Temple_India.jpg' },
            'PB': { famous: 'Golden Temple, Amritsar', image: 'https://upload.wikimedia.org/wikipedia/commons/9/94/Golden_Temple_Amritsar_India.jpg' },
            'RJ': { famous: 'Jaipur Pink City & Forts', image: 'https://upload.wikimedia.org/wikipedia/commons/e/e0/Hawa_Mahal_2011.jpg' },
            'SK': { famous: 'Nathu La & Kanchenjunga', image: 'https://upload.wikimedia.org/wikipedia/commons/a/af/Gangtok_city_view.jpg' },
            'TN': { famous: 'Meenakshi Temple', image: 'https://upload.wikimedia.org/wikipedia/commons/2/28/Meenakshi_Amman_West_Tower.jpg' },
            'TS': { famous: 'Charminar, Hyderabad', image: 'https://upload.wikimedia.org/wikipedia/commons/0/05/Charminar_Hyderabad.jpg' },
            'TR': { famous: 'Ujjayanta Palace', image: 'https://upload.wikimedia.org/wikipedia/commons/9/9a/Ujjayanta_Palace_Agartala.jpg' },
            'UP': { famous: 'Taj Mahal, Agra', image: 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Taj_Mahal_in_March_2004.jpg' },
            'UK': { famous: 'Rishikesh & Badrinath', image: 'https://upload.wikimedia.org/wikipedia/commons/4/4e/Kedarnath_Temple_India.jpg' },
            'WB': { famous: 'Sundarbans & Victoria Memorial', image: 'https://upload.wikimedia.org/wikipedia/commons/2/29/Victoria_Memorial_Kolkata.jpg' },
            'AN': { famous: 'Radhanagar Beach', image: 'https://upload.wikimedia.org/wikipedia/commons/4/42/Radhanagar_Beach_Havelock.jpg' },
            'CH': { famous: 'Rock Garden', image: 'https://upload.wikimedia.org/wikipedia/commons/1/14/Rock_Garden_Chandigarh.jpg' },
            'DN': { famous: 'Dudhani Lake', image: 'https://upload.wikimedia.org/wikipedia/commons/d/da/Dudhni_lake.jpg' },
            'DL': { famous: 'India Gate & Red Fort', image: 'https://upload.wikimedia.org/wikipedia/commons/2/25/Red_Fort_India.jpg' },
            'JK': { famous: 'Dal Lake & Gulmarg', image: 'https://upload.wikimedia.org/wikipedia/commons/2/26/Dal_Lake_Srinagar.jpg' },
            'LA': { famous: 'Pangong Lake', image: 'https://upload.wikimedia.org/wikipedia/commons/6/63/Pangong_Tso_Lake.jpg' },
            'LD': { famous: 'Agatti Island', image: 'https://upload.wikimedia.org/wikipedia/commons/7/75/Agatti_Island.jpg' },
            'PY': { famous: 'French Quarter & Auroville', image: 'https://upload.wikimedia.org/wikipedia/commons/2/25/Matrimandir_Auroville.jpg' }
        };

        container.innerHTML = this.filteredStates.map(state => {
            const badgeLabel = state.category === 'state' ? 'State' : 'Union Territory';
            const badgeColor = state.category === 'state' ? 'badge-blue' : 'badge-emerald';
            
            const overrides = stateDataOverrides[state.code] || { famous: state.capital, image: state.banner_image };
            const displayImage = overrides.image || state.banner_image;

            return `
                <div class="state-card" onclick="tourism.openStateDetail('${state.code}')">
                    <div class="state-card-image" id="img-wrap-${state.code}">
                        <img
                            src="${displayImage}"
                            alt="${state.name}"
                            loading="lazy"
                            onerror="this.style.display='none';document.getElementById('img-wrap-${state.code}').insertAdjacentHTML('afterbegin',tourism.getStatePlaceholder('${state.name}'));"
                        />
                        <span class="badge ${badgeColor} state-card-badge">${badgeLabel}</span>
                    </div>
                    <div class="state-card-body">
                        <h3 class="state-card-title">${state.name}</h3>
                        <div class="state-card-capital">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                            Capital: ${state.capital}
                        </div>
                        <div style="font-size: 0.85rem; color: #f59e0b; font-weight: 600; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 4px;">
                            ✨ Famous for: ${overrides.famous}
                        </div>
                        <p class="state-card-desc">${state.description}</p>
                        <div class="state-card-footer">
                            <span style="font-size: 0.78rem; color: var(--safe-emerald-light); font-weight: 600; display: flex; align-items: center; gap: 4px;">
                                🛡️ ${state.emergency_helpline.split('/')[0]} Active
                            </span>
                            <button class="btn btn-outline btn-sm" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;">
                                Explore Guide →
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    async openStateDetail(code) {
        try {
            const state = await api.getStateDetail(code);
            const modal = document.getElementById('state-detail-modal');
            const modalBody = document.getElementById('state-modal-body');

            modalBody.innerHTML = `
                <div style="position: relative; height: 260px; border-radius: var(--radius-lg); overflow: hidden; margin-bottom: 1.75rem;" id="modal-img-wrap-${state.code}">
                    <img
                        src="${state.banner_image}"
                        style="width: 100%; height: 100%; object-fit: cover;"
                        alt="${state.name}"
                        onerror="this.style.display='none';document.getElementById('modal-img-wrap-${state.code}').insertAdjacentHTML('afterbegin',tourism.getStatePlaceholder('${state.name}'));"
                    />
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; padding: 1.5rem; background: linear-gradient(transparent, rgba(15, 23, 42, 0.95)); display: flex; align-items: flex-end; justify-content: space-between;">
                        <div>
                            <span class="badge badge-emerald" style="margin-bottom: 0.4rem;">${state.region} India • ${state.category.replace('_', ' ').toUpperCase()}</span>
                            <h2 style="font-size: 2.2rem; color: #ffffff; margin: 0;">${state.name}</h2>
                            <p style="color: var(--text-muted); font-size: 0.9rem; margin: 0;">Capital: <strong>${state.capital}</strong></p>
                        </div>
                        <a href="${state.official_website}" target="_blank" rel="noopener" class="btn btn-outline btn-sm" style="backdrop-filter: blur(8px); background: rgba(15, 23, 42, 0.6);">
                            🌐 Official Tourism Portal ↗
                        </a>
                    </div>
                </div>

                <div style="margin-bottom: 2rem;">
                    <h4 style="color: #ffffff; font-size: 1.15rem; margin-bottom: 0.5rem;">About ${state.name}</h4>
                    <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.7;">${state.description}</p>
                </div>

                <!-- Best Season & Helplines Bar -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid var(--navy-border); border-radius: var(--radius-md); padding: 1rem;">
                        <span style="font-size: 0.75rem; color: var(--safe-emerald-light); font-weight: 700; text-transform: uppercase;">Best Visiting Season</span>
                        <div style="font-size: 0.95rem; font-weight: 600; color: #ffffff; margin-top: 0.2rem;">${state.best_season}</div>
                    </div>
                    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid var(--navy-border); border-radius: var(--radius-md); padding: 1rem;">
                        <span style="font-size: 0.75rem; color: #f87171; font-weight: 700; text-transform: uppercase;">Tourist Emergency Line</span>
                        <div style="font-size: 0.95rem; font-weight: 600; color: #ffffff; margin-top: 0.2rem;">${state.emergency_helpline}</div>
                    </div>
                </div>

                <!-- Major Destinations Grid -->
                <div style="margin-bottom: 2rem;">
                    <h4 style="color: #ffffff; font-size: 1.15rem; margin-bottom: 1rem;">Major Tourist Destinations</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem;">
                        ${state.destinations.map((d, di) => `
                            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid var(--navy-border); border-radius: var(--radius-md); overflow: hidden;">
                                <div id="dest-img-wrap-${state.code}-${di}" style="width:100%;height:140px;overflow:hidden;">
                                    <img
                                        src="${d.image_url}"
                                        style="width: 100%; height: 140px; object-fit: cover;"
                                        alt="${d.name}"
                                        onerror="this.style.display='none';document.getElementById('dest-img-wrap-${state.code}-${di}').insertAdjacentHTML('afterbegin',tourism.getStatePlaceholder('${d.name}'));"
                                    />
                                </div>
                                <div style="padding: 1rem;">
                                    <span class="badge badge-blue" style="font-size: 0.7rem; margin-bottom: 0.4rem;">${d.category}</span>
                                    <h5 style="color: #ffffff; font-size: 1rem; margin-bottom: 0.4rem;">${d.name}</h5>
                                    <p style="color: var(--text-muted); font-size: 0.82rem; margin-bottom: 0.75rem; line-height: 1.4;">${d.description}</p>
                                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); border-top: 1px solid var(--navy-border); padding-top: 0.5rem;">
                                        <span>Entry: <strong>${d.entry_fee}</strong></span>
                                        <span>Rating: ⭐ <strong>${d.safety_score}</strong></span>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Culture and Food -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
                    <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid var(--navy-border); border-radius: var(--radius-md); padding: 1.25rem;">
                        <h4 style="color: #ffffff; font-size: 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                            🎭 Culture & Traditions
                        </h4>
                        <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">${state.culture_traditions}</p>
                    </div>
                    <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid var(--navy-border); border-radius: var(--radius-md); padding: 1.25rem;">
                        <h4 style="color: #ffffff; font-size: 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                            🍲 Local Culinary Delicacies
                        </h4>
                        <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">${state.local_food}</p>
                    </div>
                </div>

                <div style="display: flex; justify-content: flex-end; gap: 1rem;">
                    <button class="btn btn-outline" onclick="tourism.closeStateModal()">Close</button>
                    <button class="btn btn-emerald" onclick="tourism.closeStateModal(); app.navigate('packages');">
                        View Packages for ${state.name}
                    </button>
                </div>
            `;

            modal.classList.add('open');
        } catch (e) {
            window.showToast('Failed to load state details: ' + e.message, 'danger');
        }
    }

    closeStateModal() {
        const modal = document.getElementById('state-detail-modal');
        if (modal) modal.classList.remove('open');
    }
}

const tourism = new TourismManager();
window.tourism = tourism;
