// Geonova Subscription & Payment Gateway Sandbox

class PaymentManager {
    constructor() {
        this.plans = [];
    }

    async init() {
        try {
            this.plans = await api.getPlans();
            this.renderPricingTable();
        } catch (e) {
            console.error('Failed to load plans:', e);
        }
    }

    renderPricingTable() {
        const container = document.getElementById('pricing-plans-grid');
        if (!container) return;

        container.innerHTML = this.plans.map(plan => `
            <div class="pricing-card ${plan.is_popular ? 'popular' : ''}">
                ${plan.is_popular ? '<div class="popular-badge">Most Popular for Tourists</div>' : ''}
                <h3 style="font-size: 1.4rem; color: #ffffff;">${plan.name}</h3>
                <div class="pricing-amount">
                    ${plan.price === 0 ? 'Free' : `₹${plan.price.toLocaleString()}`}
                    <span style="font-size: 0.85rem; font-weight: 500; color: var(--text-muted);">/${plan.billing}</span>
                </div>
                <p style="color: var(--text-muted); font-size: 0.88rem; line-height: 1.5; min-height: 42px;">${plan.description}</p>
                
                <ul class="pricing-features-list">
                    ${plan.features.map(f => `
                        <li>
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${plan.is_popular ? '#10b981' : '#3b82f6'}" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                            <span>${f}</span>
                        </li>
                    `).join('')}
                </ul>

                <button class="btn ${plan.is_popular ? 'btn-emerald' : 'btn-outline'} btn-block btn-lg" onclick="paymentManager.openCheckoutModal('${plan.id}', ${plan.price}, '${plan.name}')">
                    ${plan.price === 0 ? 'Current Free Tier' : 'Upgrade to ' + plan.name}
                </button>
            </div>
        `).join('');
    }

    openCheckoutModal(planId, price, planName) {
        if (!auth.currentUser) {
            window.showToast('Please sign in or register to upgrade subscription.', 'warning');
            auth.openLoginModal();
            return;
        }

        if (price === 0) {
            window.showToast('You are already on the free tier.', 'info');
            return;
        }

        const modal = document.getElementById('checkout-modal');
        const modalBody = document.getElementById('checkout-modal-body');

        modalBody.innerHTML = `
            <div style="font-family: 'Inter', sans-serif;">
                <div style="text-align: center; margin-bottom: 2rem;">
                    <div style="width: 48px; height: 48px; background: rgba(16, 185, 129, 0.15); color: #10b981; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin: 0 auto 1rem;">
                        🛡️
                    </div>
                    <h3 style="color: #ffffff; font-size: 1.5rem; margin-bottom: 0.5rem; font-weight: 700;">Complete Your Upgrade</h3>
                    <p style="color: var(--text-muted); font-size: 0.95rem; max-width: 300px; margin: 0 auto;">You're upgrading to the <strong style="color: #60a5fa;">${planName}</strong> plan.</p>
                </div>

                <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid var(--navy-border); border-radius: 12px; padding: 1.25rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; margin-bottom: 0.3rem;">Total Amount Due</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #ffffff; display: flex; align-items: baseline; gap: 4px;">
                            <span style="font-size: 1.2rem; color: #94a3b8;">₹</span>${price.toLocaleString()}
                        </div>
                    </div>
                    <div style="background: rgba(16, 185, 129, 0.1); padding: 0.5rem 0.75rem; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
                        <span style="color: #10b981; font-weight: 700; font-size: 0.85rem;">Sandbox Mode Active</span>
                    </div>
                </div>

                <form id="subscription-payment-form" onsubmit="paymentManager.handleSubscribe(event, '${planId}')">
                    <div class="form-group" style="margin-bottom: 1.5rem;">
                        <label class="form-label" style="font-weight: 600; color: #cbd5e1; margin-bottom: 0.75rem;">Select Payment Method</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem;">
                            <label style="cursor: pointer; border: 1px solid var(--navy-border); border-radius: 8px; padding: 1rem; text-align: center; background: rgba(15, 23, 42, 0.4); transition: all 0.2s;">
                                <input type="radio" name="pay_method" value="UPI" checked style="display: none;" onchange="document.getElementById('upi-fields').style.display='block'; document.getElementById('card-fields').style.display='none';" />
                                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📱</div>
                                <div style="font-size: 0.85rem; font-weight: 600; color: #ffffff;">UPI</div>
                            </label>
                            <label style="cursor: pointer; border: 1px solid var(--navy-border); border-radius: 8px; padding: 1rem; text-align: center; background: rgba(15, 23, 42, 0.4); transition: all 0.2s;">
                                <input type="radio" name="pay_method" value="Card" style="display: none;" onchange="document.getElementById('upi-fields').style.display='none'; document.getElementById('card-fields').style.display='block';" />
                                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💳</div>
                                <div style="font-size: 0.85rem; font-weight: 600; color: #ffffff;">Card</div>
                            </label>
                            <label style="cursor: pointer; border: 1px solid var(--navy-border); border-radius: 8px; padding: 1rem; text-align: center; background: rgba(15, 23, 42, 0.4); transition: all 0.2s;">
                                <input type="radio" name="pay_method" value="NetBanking" style="display: none;" onchange="document.getElementById('upi-fields').style.display='none'; document.getElementById('card-fields').style.display='none';" />
                                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🏦</div>
                                <div style="font-size: 0.85rem; font-weight: 600; color: #ffffff;">NetBanking</div>
                            </label>
                        </div>
                    </div>

                    <div id="upi-fields" style="background: rgba(15, 23, 42, 0.4); padding: 1rem; border-radius: 8px; border: 1px solid var(--navy-border); margin-bottom: 1.5rem;">
                        <div class="form-group" style="margin-bottom: 0;">
                            <label class="form-label" style="font-size: 0.85rem; color: #94a3b8;">Enter UPI ID (VPA)</label>
                            <div style="position: relative;">
                                <span style="position: absolute; left: 12px; top: 50%; transform: translateY(-50%); font-size: 1.1rem;">📱</span>
                                <input type="text" id="sub-pay-method-val" class="form-input" style="padding-left: 2.5rem; background: rgba(11, 19, 43, 0.6);" placeholder="e.g. tourist@okhdfcbank" value="tourist@okhdfcbank" />
                            </div>
                        </div>
                    </div>

                    <div id="card-fields" style="display: none; background: rgba(15, 23, 42, 0.4); padding: 1rem; border-radius: 8px; border: 1px solid var(--navy-border); margin-bottom: 1.5rem;">
                        <div class="form-group">
                            <label class="form-label" style="font-size: 0.85rem; color: #94a3b8;">Card Number</label>
                            <input type="text" class="form-input" style="background: rgba(11, 19, 43, 0.6);" placeholder="0000 0000 0000 0000" />
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                            <div class="form-group" style="margin-bottom: 0;">
                                <label class="form-label" style="font-size: 0.85rem; color: #94a3b8;">Expiry Date</label>
                                <input type="text" class="form-input" style="background: rgba(11, 19, 43, 0.6);" placeholder="MM/YY" />
                            </div>
                            <div class="form-group" style="margin-bottom: 0;">
                                <label class="form-label" style="font-size: 0.85rem; color: #94a3b8;">CVV</label>
                                <input type="password" class="form-input" style="background: rgba(11, 19, 43, 0.6);" placeholder="•••" />
                            </div>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-emerald btn-block btn-lg" style="margin-top: 1rem; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3); font-size: 1.05rem; padding: 1rem;">
                        Authorize Payment & Activate Shield
                    </button>
                    
                    <div style="text-align: center; margin-top: 1rem; font-size: 0.75rem; color: #64748b; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                        🔒 <span>Secured by 256-bit SSL Encryption. Sandbox Environment.</span>
                    </div>
                </form>
            </div>
        `;

        modal.classList.add('open');
    }

    async handleSubscribe(e, planId) {
        e.preventDefault();
        
        let payment_method = "UPI";
        const selectedRadio = document.querySelector('input[name="pay_method"]:checked');
        if (selectedRadio) {
            payment_method = selectedRadio.value;
        }

        try {
            const res = await api.subscribe({ plan: planId, payment_method });
            this.closeModal();
            window.showToast(res.message || 'Subscription updated!', 'success');
            
            // Reload user state
            if (window.auth) await window.auth.init();
            if (window.dashboard) window.dashboard.loadData();
        } catch (err) {
            window.showToast('Subscription upgrade failed: ' + err.message, 'danger');
        }
    }

    closeModal() {
        const modal = document.getElementById('checkout-modal');
        if (modal) modal.classList.remove('open');
    }
}

const paymentManager = new PaymentManager();
window.paymentManager = paymentManager;
