// Geonova Tourism Packages & Booking Marketplace

class PackageManager {
    constructor() {
        this.packages = [];
        this.selectedPackage = null;
    }

    async init() {
        try {
            const states = await api.getStates();
            
            // Map state overrides to use accurate images (re-using the logic from tourism)
            const stateDataOverrides = {
                'AP': { image: 'https://upload.wikimedia.org/wikipedia/commons/4/41/Tirumala_090615.jpg' },
                'AR': { image: 'https://upload.wikimedia.org/wikipedia/commons/6/6c/Tawang_Monastery_%282018%29.jpg' },
                'AS': { image: 'https://upload.wikimedia.org/wikipedia/commons/4/41/Kaziranga_National_Park_Elephant_Safari.jpg' },
                'BR': { image: 'https://upload.wikimedia.org/wikipedia/commons/6/6f/Mahabodhi_temple%2C_Bodh_Gaya.jpg' },
                'CT': { image: 'https://upload.wikimedia.org/wikipedia/commons/2/23/Chitrakoot_Waterfalls_Bastar.jpg' },
                'GA': { image: 'https://upload.wikimedia.org/wikipedia/commons/3/3e/Palolem_Beach_Goa.jpg' },
                'GJ': { image: 'https://upload.wikimedia.org/wikipedia/commons/3/30/Statue_of_Unity%2C_Kevadia%2C_India.jpg' },
                'HR': { image: 'https://upload.wikimedia.org/wikipedia/commons/0/07/Brahma_Sarovar_Kurukshetra.jpg' },
                'HP': { image: 'https://upload.wikimedia.org/wikipedia/commons/1/1a/Rohtang_Pass_Manali.jpg' },
                'JH': { image: 'https://upload.wikimedia.org/wikipedia/commons/6/68/Baidyanath_Jyotirlinga_temple.jpg' },
                'KA': { image: 'https://upload.wikimedia.org/wikipedia/commons/e/e5/Mysore_Palace_Morning.jpg' },
                'KL': { image: 'https://upload.wikimedia.org/wikipedia/commons/0/05/Kerala_backwaters.jpg' },
                'MP': { image: 'https://upload.wikimedia.org/wikipedia/commons/d/dd/Khajuraho_Lakshmana_Temple.jpg' },
                'MH': { image: 'https://upload.wikimedia.org/wikipedia/commons/0/01/Gateway_of_India%2C_Mumbai.jpg' },
                'MN': { image: 'https://upload.wikimedia.org/wikipedia/commons/6/62/Loktak_Lake_Manipur.jpg' },
                'ML': { image: 'https://upload.wikimedia.org/wikipedia/commons/2/23/Living_root_bridge_Mawlynnong.jpg' },
                'MZ': { image: 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Aizawl_city_view.jpg' },
                'NL': { image: 'https://upload.wikimedia.org/wikipedia/commons/5/52/Hornbill_festival_Kohima.jpg' },
                'OD': { image: 'https://upload.wikimedia.org/wikipedia/commons/9/91/Konark_Sun_Temple_India.jpg' },
                'PB': { image: 'https://upload.wikimedia.org/wikipedia/commons/9/94/Golden_Temple_Amritsar_India.jpg' },
                'RJ': { image: 'https://upload.wikimedia.org/wikipedia/commons/e/e0/Hawa_Mahal_2011.jpg' },
                'SK': { image: 'https://upload.wikimedia.org/wikipedia/commons/a/af/Gangtok_city_view.jpg' },
                'TN': { image: 'https://upload.wikimedia.org/wikipedia/commons/2/28/Meenakshi_Amman_West_Tower.jpg' },
                'TS': { image: 'https://upload.wikimedia.org/wikipedia/commons/0/05/Charminar_Hyderabad.jpg' },
                'TR': { image: 'https://upload.wikimedia.org/wikipedia/commons/9/9a/Ujjayanta_Palace_Agartala.jpg' },
                'UP': { image: 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Taj_Mahal_in_March_2004.jpg' },
                'UK': { image: 'https://upload.wikimedia.org/wikipedia/commons/4/4e/Kedarnath_Temple_India.jpg' },
                'WB': { image: 'https://upload.wikimedia.org/wikipedia/commons/2/29/Victoria_Memorial_Kolkata.jpg' },
                'AN': { image: 'https://upload.wikimedia.org/wikipedia/commons/4/42/Radhanagar_Beach_Havelock.jpg' },
                'CH': { image: 'https://upload.wikimedia.org/wikipedia/commons/1/14/Rock_Garden_Chandigarh.jpg' },
                'DN': { image: 'https://upload.wikimedia.org/wikipedia/commons/d/da/Dudhni_lake.jpg' },
                'DL': { image: 'https://upload.wikimedia.org/wikipedia/commons/2/25/Red_Fort_India.jpg' },
                'JK': { image: 'https://upload.wikimedia.org/wikipedia/commons/2/26/Dal_Lake_Srinagar.jpg' },
                'LA': { image: 'https://upload.wikimedia.org/wikipedia/commons/6/63/Pangong_Tso_Lake.jpg' },
                'LD': { image: 'https://upload.wikimedia.org/wikipedia/commons/7/75/Agatti_Island.jpg' },
                'PY': { image: 'https://upload.wikimedia.org/wikipedia/commons/2/25/Matrimandir_Auroville.jpg' }
            };

            this.packages = states.map((state, index) => {
                const durationDays = Math.floor(Math.random() * 5) + 3; // 3 to 7 days
                const overrides = stateDataOverrides[state.code] || {};
                return {
                    id: index + 1000,
                    provider_name: "Geonova Official Partners",
                    title: `Ultimate ${state.name} Tour Package`,
                    destination: state.name,
                    duration_days: durationDays,
                    duration_nights: durationDays - 1,
                    price: Math.floor(Math.random() * 15000) + 15000,
                    discount_price: Math.floor(Math.random() * 5000) + 10000,
                    travel_type: state.category === 'state' ? "Heritage & Culture" : "Exclusive Retreat",
                    max_group_size: Math.floor(Math.random() * 8) + 4,
                    accommodation: "4-Star Hotel",
                    transportation: "AC Coach / SUV",
                    meals: "Breakfast & Dinner",
                    guide_included: true,
                    safety_features: "GPS Tracking, SOS Support",
                    itinerary: `Explore the vibrant culture and landmarks of ${state.name}. The tour covers famous spots like ${state.capital} and much more.`,
                    image_url: state.banner_image || overrides.image,
                    rating: (Math.random() * 1 + 4).toFixed(1), // 4.0 to 5.0
                    reviews_count: Math.floor(Math.random() * 400) + 50
                };
            });
            this.renderPackagesGrid();
        } catch (e) {
            console.error('Failed to load packages:', e);
        }
    }

    renderPackagesGrid() {
        const container = document.getElementById('packages-cards-grid');
        if (!container) return;

        if (this.packages.length === 0) {
            container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">No tourism packages available at the moment.</div>`;
            return;
        }

        container.innerHTML = this.packages.map(pkg => `
            <div class="package-card">
                <div class="package-image">
                    <img src="${pkg.image_url}" alt="${pkg.title}" loading="lazy" />
                    <div class="package-price-tag">
                        ₹${pkg.discount_price ? pkg.discount_price.toLocaleString() : pkg.price.toLocaleString()}
                        ${pkg.discount_price ? `<span style="font-size: 0.8rem; text-decoration: line-through; color: #94a3b8; margin-left: 6px;">₹${pkg.price.toLocaleString()}</span>` : ''}
                    </div>
                </div>
                <div class="package-body">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span class="badge badge-emerald" style="font-size: 0.72rem;">${pkg.travel_type}</span>
                        <span style="font-size: 0.82rem; color: var(--alert-amber-light); font-weight: 700;">
                            ⭐ ${pkg.rating} (${pkg.reviews_count} reviews)
                        </span>
                    </div>

                    <h3 style="font-size: 1.3rem; color: var(--text-main); margin-bottom: 0.4rem;">${pkg.title}</h3>
                    <p style="color: var(--text-muted); font-size: 0.88rem; margin-bottom: 0.75rem;">
                        📍 ${pkg.destination} • ⏱️ ${pkg.duration_days} Days / ${pkg.duration_nights} Nights
                    </p>

                    <div class="package-features">
                        <span class="feature-pill">🚗 ${pkg.transportation.split('/')[0]}</span>
                        <span class="feature-pill">🏨 ${pkg.accommodation.split(' ')[0]} Certified</span>
                        <span class="feature-pill">🛡️ GPS Monitored</span>
                        <span class="feature-pill">👥 Max ${pkg.max_group_size} Travelers</span>
                    </div>

                    <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 1.5rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                        ${pkg.itinerary}
                    </p>

                    <div style="margin-top: auto; display: flex; gap: 0.75rem;">
                        <button class="btn btn-primary btn-block" onclick="packageManager.openBookingModal(${pkg.id})">
                            Book Tour Package
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    openBookingModal(pkgId) {
        if (!auth.currentUser) {
            window.showToast('Please sign in or register to book a travel package.', 'warning');
            auth.openLoginModal();
            return;
        }

        const pkg = this.packages.find(p => p.id === pkgId);
        if (!pkg) return;
        this.selectedPackage = pkg;

        const modal = document.getElementById('booking-modal');
        const modalBody = document.getElementById('booking-modal-body');
        const effectivePrice = pkg.discount_price || pkg.price;

        modalBody.innerHTML = `
            <div>
                <div style="display: flex; gap: 1rem; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--navy-border);">
                    <img src="${pkg.image_url}" style="width: 80px; height: 80px; border-radius: var(--radius-md); object-fit: cover;" />
                    <div>
                        <span class="badge badge-emerald" style="font-size: 0.7rem;">Verified Safe Package</span>
                        <h3 style="font-size: 1.25rem; color: #ffffff; margin: 0.25rem 0;">${pkg.title}</h3>
                        <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0;">${pkg.destination} • ₹${effectivePrice.toLocaleString()} per traveler</p>
                    </div>
                </div>

                <form id="booking-form" onsubmit="packageManager.handleBooking(event)">
                    <div class="form-group">
                        <label class="form-label">Select Travel Start Date</label>
                        <input type="date" id="booking-date" class="form-input" required min="${new Date().toISOString().split('T')[0]}" value="${new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0]}" />
                    </div>

                    <div class="form-group">
                        <label class="form-label">Number of Travelers</label>
                        <input type="number" id="travelers-count" class="form-input" min="1" max="${pkg.max_group_size}" value="1" onchange="packageManager.updateTotal(${effectivePrice})" required />
                    </div>

                    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--navy-border); border-radius: var(--radius-md); padding: 1.25rem; margin-bottom: 1.5rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">
                            <span>Package Fare:</span>
                            <span id="booking-subtotal">₹${effectivePrice.toLocaleString()}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">
                            <span>Tourist Safety Insurance:</span>
                            <span style="color: var(--safe-emerald-light);">Included Free</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-top: 1px solid var(--navy-border); padding-top: 0.75rem; font-weight: 700; font-size: 1.2rem; color: #ffffff;">
                            <span>Total Payable:</span>
                            <span id="booking-total-amount" style="color: #60a5fa;">₹${effectivePrice.toLocaleString()}</span>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Payment Mode (Sandbox Simulated)</label>
                        <select id="payment-mode" class="form-select">
                            <option value="UPI (Google Pay / PhonePe)">UPI (Google Pay / PhonePe Sandbox)</option>
                            <option value="Credit / Debit Card">Credit / Debit Card (Visa/Mastercard Sandbox)</option>
                            <option value="NetBanking">NetBanking Verified Gateway</option>
                        </select>
                    </div>

                    <button type="submit" class="btn btn-emerald btn-block btn-lg" style="margin-top: 1rem;">
                        Confirm & Complete Payment
                    </button>
                </form>
            </div>
        `;

        modal.classList.add('open');
    }

    updateTotal(unitPrice) {
        const count = parseInt(document.getElementById('travelers-count').value, 10) || 1;
        const total = unitPrice * count;
        const subtotalElem = document.getElementById('booking-subtotal');
        const totalElem = document.getElementById('booking-total-amount');
        if (subtotalElem) subtotalElem.textContent = `₹${total.toLocaleString()}`;
        if (totalElem) totalElem.textContent = `₹${total.toLocaleString()}`;
    }

    async handleBooking(e) {
        e.preventDefault();
        const travel_date = document.getElementById('booking-date').value;
        const travelers_count = parseInt(document.getElementById('travelers-count').value, 10) || 1;
        const payment_method = document.getElementById('payment-mode').value;

        try {
            const booking = await api.bookPackage({
                package_id: this.selectedPackage.id,
                travel_date,
                travelers_count,
                payment_method
            });

            this.closeBookingModal();
            this.showInvoiceModal(booking);
            window.showToast(`Booking ${booking.booking_reference} confirmed successfully!`, 'success');
            
            // Reload tourist dashboard
            if (window.dashboard) window.dashboard.loadData();
        } catch (err) {
            window.showToast('Booking failed: ' + err.message, 'danger');
        }
    }

    showInvoiceModal(booking) {
        const modal = document.getElementById('booking-modal');
        const modalBody = document.getElementById('booking-modal-body');

        modalBody.innerHTML = `
            <div style="text-align: center; padding: 1rem 0;">
                <div style="width: 64px; height: 64px; border-radius: 50%; background: var(--grad-emerald); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: #ffffff; font-size: 2rem;">
                    ✓
                </div>
                <h3 style="font-size: 1.6rem; color: #ffffff; margin-bottom: 0.25rem;">Payment & Booking Confirmed!</h3>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">Booking Reference: <strong style="color: #60a5fa;">${booking.booking_reference}</strong></p>

                <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid var(--navy-border); border-radius: var(--radius-md); padding: 1.25rem; text-align: left; margin-bottom: 1.5rem; font-size: 0.9rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: var(--text-muted);">Package:</span>
                        <span style="color: #ffffff; font-weight: 600;">${booking.package_title}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: var(--text-muted);">Travel Date:</span>
                        <span style="color: #ffffff;">${booking.travel_date}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: var(--text-muted);">Travelers:</span>
                        <span style="color: #ffffff;">${booking.travelers_count} Person(s)</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-top: 1px solid var(--navy-border); padding-top: 0.5rem; font-weight: 700;">
                        <span style="color: var(--text-muted);">Amount Paid:</span>
                        <span style="color: var(--safe-emerald-light);">₹${booking.total_amount.toLocaleString()}</span>
                    </div>
                </div>

                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <button class="btn btn-outline" onclick="packageManager.closeBookingModal()">Done</button>
                    <button class="btn btn-primary" onclick="window.print()">🖨️ Print Booking Receipt</button>
                </div>
            </div>
        `;
    }

    closeBookingModal() {
        const modal = document.getElementById('booking-modal');
        if (modal) modal.classList.remove('open');
    }
}

const packageManager = new PackageManager();
window.packageManager = packageManager;
