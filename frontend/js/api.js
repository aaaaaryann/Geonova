// Geonova API Client Wrapper
const API_BASE_URL = window.location.origin;

class ApiClient {
    constructor() {
        this.token = localStorage.getItem('geonova_token') || null;
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('geonova_token', token);
        } else {
            localStorage.removeItem('geonova_token');
        }
    }

    getHeaders(customHeaders = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...customHeaders
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: this.getHeaders(options.headers),
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                // Expired or invalid token
                this.setToken(null);
                window.dispatchEvent(new CustomEvent('auth:expired'));
            }

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                const errorMsg = data.detail || response.statusText || 'Request failed';
                throw new Error(errorMsg);
            }

            return data;
        } catch (error) {
            console.error(`API Error on ${endpoint}:`, error);
            throw error;
        }
    }

    // Auth
    login(credentials) {
        return this.request('/api/auth/login', { method: 'POST', body: JSON.stringify(credentials) });
    }

    loginWithGoogle(payload) {
        return this.request('/api/auth/google', { method: 'POST', body: JSON.stringify(payload) });
    }

    sendPhoneOtp(payload) {
        return this.request('/api/auth/phone/send-otp', { method: 'POST', body: JSON.stringify(payload) });
    }

    verifyPhoneOtp(payload) {
        return this.request('/api/auth/phone/verify-otp', { method: 'POST', body: JSON.stringify(payload) });
    }

    sendAadhaarOtp(payload) {
        return this.request('/api/auth/aadhaar/send-otp', { method: 'POST', body: JSON.stringify(payload) });
    }

    verifyAadhaarOtp(payload) {
        return this.request('/api/auth/aadhaar/verify-otp', { method: 'POST', body: JSON.stringify(payload) });
    }

    register(userData) {
        return this.request('/api/auth/register', { method: 'POST', body: JSON.stringify(userData) });
    }

    getProfile() {
        return this.request('/api/auth/me');
    }

    updateProfile(data) {
        return this.request('/api/auth/profile', { method: 'PUT', body: JSON.stringify(data) });
    }

    getEmergencyContacts() {
        return this.request('/api/auth/emergency-contacts');
    }

    addEmergencyContact(data) {
        return this.request('/api/auth/emergency-contacts', { method: 'POST', body: JSON.stringify(data) });
    }

    deleteEmergencyContact(id) {
        return this.request(`/api/auth/emergency-contacts/${id}`, { method: 'DELETE' });
    }

    // Tourism
    getStates(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/tourism/states${query ? '?' + query : ''}`);
    }

    getStateDetail(code) {
        return this.request(`/api/tourism/states/${code}`);
    }

    getDestinations(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/tourism/destinations${query ? '?' + query : ''}`);
    }

    // Safety & Geofencing
    getGeofences() {
        return this.request('/api/safety/geofences');
    }

    checkGeofence(coords) {
        return this.request('/api/safety/geofence-check', { method: 'POST', body: JSON.stringify(coords) });
    }

    updateLocation(coords) {
        return this.request('/api/safety/tracking/update', { method: 'POST', body: JSON.stringify(coords) });
    }

    stopLocationTracking() {
        return this.request('/api/safety/tracking/stop', { method: 'POST' });
    }

    triggerSOS(sosData) {
        return this.request('/api/safety/sos', { method: 'POST', body: JSON.stringify(sosData) });
    }

    getAuthorities(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/safety/authorities${query ? '?' + query : ''}`);
    }

    getProtocols(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/safety/protocols${query ? '?' + query : ''}`);
    }

    // Packages & Bookings
    getPackages(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/packages/${query ? '?' + query : ''}`);
    }

    getPackageDetail(id) {
        return this.request(`/api/packages/${id}`);
    }

    bookPackage(bookingData) {
        return this.request('/api/packages/book', { method: 'POST', body: JSON.stringify(bookingData) });
    }

    getMyBookings() {
        return this.request('/api/packages/user/my-bookings');
    }

    // Vault
    getDocuments() {
        return this.request('/api/vault/documents');
    }

    uploadDocument(docData) {
        return this.request('/api/vault/documents', { method: 'POST', body: JSON.stringify(docData) });
    }

    deleteDocument(id) {
        return this.request(`/api/vault/documents/${id}`, { method: 'DELETE' });
    }

    // Payments & Subscriptions
    getPlans() {
        return this.request('/api/payments/plans');
    }

    subscribe(planData) {
        return this.request('/api/payments/subscribe', { method: 'POST', body: JSON.stringify(planData) });
    }

    getInvoices() {
        return this.request('/api/payments/invoices');
    }

    // Admin
    getAdminStats() {
        return this.request('/api/admin/stats');
    }

    getAdminIncidents() {
        return this.request('/api/admin/incidents');
    }

    updateIncident(id, data) {
        return this.request(`/api/admin/incidents/${id}`, { method: 'PUT', body: JSON.stringify(data) });
    }

    createGeofence(data) {
        return this.request('/api/admin/geofences', { method: 'POST', body: JSON.stringify(data) });
    }

    deleteGeofence(id) {
        return this.request(`/api/admin/geofences/${id}`, { method: 'DELETE' });
    }

    getAdminUsers() {
        return this.request('/api/admin/users');
    }

    getAuditLogs() {
        return this.request('/api/admin/audit-logs');
    }
}

const api = new ApiClient();
window.api = api;
