// Geonova Interactive Map & Real-Time Geofencing Engine

class MapManager {
    constructor() {
        this.map = null;
        this.userMarker = null;
        this.geofenceLayers = [];
        this.authorityMarkers = [];
        this.destinationMarkers = [];
        this.currentCoords = { lat: 28.6315, lng: 77.2167 }; // Default: Connaught Place, New Delhi
        this.isTracking = false;
        this.isSimulating = false;
        this.simInterval = null;
        this.simStep = 0;
        
        // Measurement Tool
        this.isMeasuring = false;
        this.measurePoints = [];
        this.measureLine = null;
        this.measureMarkers = [];
        this.measureDistance = 0;

        // Simulation Routes
        this.routes = {
            delhi: [
                { lat: 28.6315, lng: 77.2167, name: "Connaught Place Safe Zone" },
                { lat: 28.6129, lng: 77.2295, name: "India Gate Boulevard" },
                { lat: 28.5244, lng: 77.1855, name: "Qutub Minar Complex" },
                { lat: 28.4850, lng: 77.2340, name: "Entering Asola Wildlife Restricted Buffer!" } // Triggers hazard!
            ],
            goa: [
                { lat: 15.5009, lng: 73.9116, name: "Old Goa UNESCO Basilica" },
                { lat: 15.5430, lng: 73.7550, name: "Calangute Beach Safe Corridor" },
                { lat: 15.5560, lng: 73.7510, name: "Entering Baga Creek Rip-Current Danger Hazard!" } // Triggers hazard!
            ],
            rishikesh: [
                { lat: 30.0869, lng: 78.2676, name: "Rishikesh Triveni Ghat Safe Zone" },
                { lat: 30.1250, lng: 78.3200, name: "Tapovan Suspension Walkway" },
                { lat: 30.1360, lng: 78.3880, name: "Entering Shivpuri River Cliff Hazard!" } // Triggers hazard!
            ]
        };
        this.activeRouteKey = 'delhi';
    }

    init() {
        if (this.map) return; // already initialized

        const mapContainer = document.getElementById('map');
        if (!mapContainer) return;

        // Initialize Leaflet Map
        this.map = L.map('map', {
            center: [this.currentCoords.lat, this.currentCoords.lng],
            zoom: 13,
            zoomControl: false
        });

        // Use Esri's public ArcGIS REST tile services for richer basemap detail.
        const esriAttr = 'Tiles &copy; Esri &mdash; Maxar, Earthstar Geographics, and the GIS User Community';
        const esri = 'https://server.arcgisonline.com/ArcGIS/rest/services';

        const satellite = L.tileLayer(`${esri}/World_Imagery/MapServer/tile/{z}/{y}/{x}`, { attribution: esriAttr, maxZoom: 19 });
        const streets = L.tileLayer(`${esri}/World_Street_Map/MapServer/tile/{z}/{y}/{x}`, { attribution: esriAttr, maxZoom: 19 });
        const topo = L.tileLayer(`${esri}/World_Topo_Map/MapServer/tile/{z}/{y}/{x}`, { attribution: esriAttr, maxZoom: 19 });
        const terrain = L.tileLayer(`${esri}/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}`, { attribution: esriAttr, maxZoom: 13 });
        const labels = L.tileLayer(`${esri}/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}`, { attribution: esriAttr, maxZoom: 19 });

        satellite.addTo(this.map);
        labels.addTo(this.map);

        L.control.layers(
            { 'Satellite': satellite, 'Streets': streets, 'Topographic': topo, 'Terrain Relief': terrain },
            { 'Place Labels': labels }
        ).addTo(this.map);

        L.control.zoom({ position: 'bottomright' }).addTo(this.map);

        // Add user marker
        this.updateUserMarker(this.currentCoords.lat, this.currentCoords.lng);

        // Load Geofences and Authorities
        this.loadGeofences();
        this.loadAuthorities();
        this.loadDestinations();
    }

    updateUserMarker(lat, lng) {
        this.currentCoords = { lat, lng };

        if (!this.userMarker) {
            const userIcon = L.divIcon({
                className: 'custom-user-marker',
                html: '<div class="pulse-user-marker"></div>',
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            });
            this.userMarker = L.marker([lat, lng], { icon: userIcon }).addTo(this.map);
            this.userMarker.bindPopup("<strong>Your Verified GPS Position</strong><br/>Live Location Sharing Active");
        } else {
            this.userMarker.setLatLng([lat, lng]);
        }

        // Update coordinate readouts in UI
        const latDisplay = document.getElementById('live-lat-display');
        const lngDisplay = document.getElementById('live-lng-display');
        if (latDisplay && lngDisplay) {
            latDisplay.textContent = lat.toFixed(5);
            lngDisplay.textContent = lng.toFixed(5);
        }
    }

    async loadGeofences() {
        try {
            const geofences = await api.getGeofences();

            // Clear existing geofence layers
            this.geofenceLayers.forEach(l => this.map.removeLayer(l));
            this.geofenceLayers = [];

            geofences.forEach(gf => {
                let color = '#10b981'; // safe
                let fillColor = '#10b981';
                if (gf.zone_type === 'restricted') {
                    color = '#dc2626';
                    fillColor = '#dc2626';
                } else if (gf.zone_type === 'hazard') {
                    color = '#f59e0b';
                    fillColor = '#f59e0b';
                }

                const circle = L.circle([gf.center_latitude, gf.center_longitude], {
                    color: color,
                    fillColor: fillColor,
                    fillOpacity: 0.22,
                    weight: 2,
                    radius: gf.radius_meters
                }).addTo(this.map);

                const typeBadge = gf.zone_type === 'restricted' ? '<span style="color:#ef4444; font-weight:700;">Restricted Zone</span>' :
                    gf.zone_type === 'hazard' ? '<span style="color:#f59e0b; font-weight:700;">Hazard Caution Zone</span>' :
                        '<span style="color:#10b981; font-weight:700;">Safe Tourist Zone</span>';

                circle.bindPopup(`
                    <div style="min-width: 220px; font-family: 'Plus Jakarta Sans', sans-serif;">
                        <div style="margin-bottom: 4px;">${typeBadge}</div>
                        <h4 style="margin: 0 0 6px 0; color:#ffffff; font-size:1rem;">${gf.name}</h4>
                        <p style="margin: 0 0 8px 0; font-size:0.85rem; color:#cbd5e1;">${gf.description}</p>
                        <div style="font-size:0.75rem; color:#94a3b8; border-top:1px solid #334155; padding-top:4px;">
                            Radius: ${(gf.radius_meters).toFixed(0)}m | Geonova Geofence Guard
                        </div>
                    </div>
                `, { className: 'custom-zone-popup' });

                this.geofenceLayers.push(circle);
            });
        } catch (e) {
            console.error('Failed to load geofences:', e);
        }
    }

    async loadAuthorities() {
        try {
            const authorities = await api.getAuthorities();
            this.authorityMarkers.forEach(m => this.map.removeLayer(m));
            this.authorityMarkers = [];

            authorities.forEach(a => {
                const iconColor = a.category === 'hospital' ? '#ef4444' : '#3b82f6';
                const label = a.category === 'hospital' ? '🏥 Hospital' : '🛡️ Police';

                const marker = L.circleMarker([a.latitude, a.longitude], {
                    radius: 7,
                    fillColor: iconColor,
                    color: '#ffffff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.9
                }).addTo(this.map);

                marker.bindPopup(`
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif;">
                        <strong style="color: ${iconColor}; font-size: 0.8rem; text-transform: uppercase;">${label}</strong>
                        <h4 style="margin: 4px 0; color: #ffffff;">${a.name}</h4>
                        <p style="margin: 4px 0; font-size: 0.85rem; color: #cbd5e1;">${a.address}</p>
                        <div style="margin-top: 8px;">
                            <a href="tel:${a.phone}" class="btn btn-primary btn-sm" style="display:inline-flex; padding: 4px 10px; font-size: 0.8rem;">
                                📞 Call ${a.phone}
                            </a>
                        </div>
                    </div>
                `, { className: 'custom-zone-popup' });

                this.authorityMarkers.push(marker);
            });
        } catch (e) {
            console.error('Failed to load authorities:', e);
        }
    }

    async loadDestinations() {
        try {
            const destinations = await api.getDestinations({ featured_only: true });
            this.destinationMarkers.forEach(m => this.map.removeLayer(m));
            this.destinationMarkers = [];

            destinations.forEach(d => {
                const marker = L.circleMarker([d.latitude, d.longitude], {
                    radius: 6,
                    fillColor: '#8b5cf6',
                    color: '#ffffff',
                    weight: 1.5,
                    opacity: 0.9,
                    fillOpacity: 0.8
                }).addTo(this.map);

                marker.bindPopup(`
                    <div style="max-width: 220px; font-family: 'Plus Jakarta Sans', sans-serif;">
                        <div style="color: #a78bfa; font-size: 0.75rem; text-transform: uppercase; font-weight:700;">📍 ${d.category} Attraction</div>
                        <h4 style="margin: 4px 0; color: #ffffff;">${d.name}</h4>
                        <p style="margin: 4px 0; font-size: 0.82rem; color: #cbd5e1;">${d.description}</p>
                        <div style="font-size:0.75rem; color:#94a3b8; margin-top: 6px;">Safety Score: ⭐ ${d.safety_score}/5.0</div>
                    </div>
                `, { className: 'custom-zone-popup' });

                this.destinationMarkers.push(marker);
            });
        } catch (e) {
            console.error('Failed to load destinations:', e);
        }
    }

    // Live Geolocation API toggle
    toggleRealLocation() {
        if (!navigator.geolocation) {
            window.showToast('Geolocation is not supported by your browser.', 'warning');
            return;
        }

        if (this.isTracking) {
            this.isTracking = false;
            api.stopLocationTracking();
            window.showToast('Live location sharing paused.', 'info');
            this.updateTrackingUI();
            return;
        }

        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                this.isTracking = true;
                const { latitude, longitude } = pos.coords;
                this.updateUserMarker(latitude, longitude);
                this.map.flyTo([latitude, longitude], 15);
                window.showToast('Live GPS Location synchronized with Geonova shield.', 'success');
                this.updateTrackingUI();

                // Send to backend and check geofence
                await this.sendLocationCheck(latitude, longitude);
            },
            (err) => {
                window.showToast(`Location access denied or unavailable: ${err.message}`, 'warning');
            },
            { enableHighAccuracy: true }
        );
    }

    updateTrackingUI() {
        const btn = document.getElementById('toggle-gps-btn');
        const statusBadge = document.getElementById('tracking-status-badge');
        if (btn) {
            btn.innerHTML = this.isTracking ?
                '<span class="badge badge-emerald">● Live GPS Active</span> (Click to Stop)' :
                '<span>📡 Share Live Location</span>';
        }
        if (statusBadge) {
            statusBadge.className = this.isTracking ? 'badge badge-emerald' : 'badge badge-amber';
            statusBadge.textContent = this.isTracking ? 'Active Live GPS' : 'Standby / Simulated';
        }
    }

    // Simulation Engine
    startRouteSimulation() {
        if (this.isSimulating) {
            this.stopRouteSimulation();
            return;
        }

        const route = this.routes[this.activeRouteKey];
        if (!route) return;

        this.isSimulating = true;
        this.simStep = 0;
        const simBtn = document.getElementById('sim-toggle-btn');
        if (simBtn) simBtn.innerHTML = '⏸️ Pause Route Simulation';

        window.showToast(`Starting simulated tour on ${this.activeRouteKey.toUpperCase()} route. Watch geofence alerts!`, 'info');

        this.stepSimulation();
        this.simInterval = setInterval(() => {
            this.stepSimulation();
        }, 3500);
    }

    async stepSimulation() {
        const route = this.routes[this.activeRouteKey];
        if (this.simStep >= route.length) {
            this.simStep = 0; // Loop simulation
        }

        const point = route[this.simStep];
        this.updateUserMarker(point.lat, point.lng);
        this.map.panTo([point.lat, point.lng], { animate: true, duration: 1 });

        const stepNameDisplay = document.getElementById('sim-checkpoint-name');
        if (stepNameDisplay) stepNameDisplay.textContent = point.name;

        // Perform geofence check
        await this.sendLocationCheck(point.lat, point.lng);
        this.simStep++;
    }

    stopRouteSimulation() {
        this.isSimulating = false;
        clearInterval(this.simInterval);
        const simBtn = document.getElementById('sim-toggle-btn');
        if (simBtn) simBtn.innerHTML = '▶️ Start Route Simulation';
        this.hideHazardAlert();
    }

    setSimulationRoute(routeKey) {
        this.activeRouteKey = routeKey;
        if (this.isSimulating) {
            this.stopRouteSimulation();
            this.startRouteSimulation();
        } else {
            const firstPoint = this.routes[routeKey][0];
            this.updateUserMarker(firstPoint.lat, firstPoint.lng);
            this.map.flyTo([firstPoint.lat, firstPoint.lng], 13);
        }
    }

    async sendLocationCheck(latitude, longitude) {
        try {
            const check = await api.checkGeofence({ latitude, longitude });
            await api.updateLocation({ latitude, longitude, share_with_contacts: true });

            if (check.alert_level === 'danger' || check.alert_level === 'warning') {
                this.showHazardAlert(check.message, check.alert_level);
                this.playWarningBeep();
            } else {
                this.hideHazardAlert();
            }
        } catch (e) {
            console.warn('Geofence check error:', e);
        }
    }

    showHazardAlert(message, level) {
        const banner = document.getElementById('geofence-alert-banner');
        const text = document.getElementById('geofence-alert-text');
        if (banner && text) {
            banner.className = `geofence-alert-banner active ${level === 'danger' ? 'danger-alert' : 'warning-alert'}`;
            text.textContent = message;
        }
    }

    hideHazardAlert() {
        const banner = document.getElementById('geofence-alert-banner');
        if (banner) banner.classList.remove('active');
    }

    playWarningBeep() {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            const ctx = new AudioContext();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(440, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.3);
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.4);
        } catch (e) {
            // Audio policy or unsupported
        }
    }

    // Distance Measurement Tool
    toggleMeasure() {
        this.isMeasuring = !this.isMeasuring;
        const btn = document.getElementById('measure-toggle-btn');
        if (this.isMeasuring) {
            if (btn) btn.innerHTML = '🛑 Stop Measuring';
            if (window.showToast) window.showToast('Distance Measurement activated. Click on the map to add points.', 'info');
            this.map.getContainer().style.cursor = 'crosshair';
            
            if (!this._onMapClickBound) {
                this._onMapClickBound = this.onMapClick.bind(this);
            }
            this.map.on('click', this._onMapClickBound);
        } else {
            if (btn) btn.innerHTML = '📏 Measure Distance';
            this.map.getContainer().style.cursor = '';
            
            if (this._onMapClickBound) {
                this.map.off('click', this._onMapClickBound);
            }
            this.clearMeasurements();
        }
    }
    
    onMapClick(e) {
        if (!this.isMeasuring) return;
        
        const latlng = e.latlng;
        this.measurePoints.push(latlng);
        
        const marker = L.circleMarker(latlng, {
            radius: 4,
            fillColor: '#ffffff',
            color: '#10b981',
            weight: 2,
            opacity: 1,
            fillOpacity: 1
        }).addTo(this.map);
        
        this.measureMarkers.push(marker);
        
        if (this.measurePoints.length > 1) {
            if (this.measureLine) {
                this.measureLine.setLatLngs(this.measurePoints);
            } else {
                this.measureLine = L.polyline(this.measurePoints, {
                    color: '#10b981',
                    weight: 3,
                    dashArray: '5, 5'
                }).addTo(this.map);
            }
            
            let dist = 0;
            for (let i = 0; i < this.measurePoints.length - 1; i++) {
                dist += this.measurePoints[i].distanceTo(this.measurePoints[i+1]);
            }
            this.measureDistance = dist;
            
            marker.bindTooltip(`Distance: ${(this.measureDistance / 1000).toFixed(2)} km`, {
                permanent: true,
                direction: 'right'
            }).openTooltip();
        } else {
            marker.bindTooltip('Start', { permanent: true, direction: 'right' }).openTooltip();
        }
    }
    
    clearMeasurements() {
        if (this.measureLine) {
            this.map.removeLayer(this.measureLine);
            this.measureLine = null;
        }
        this.measureMarkers.forEach(m => this.map.removeLayer(m));
        this.measureMarkers = [];
        this.measurePoints = [];
        this.measureDistance = 0;
    }
}

const mapManager = new MapManager();
window.mapManager = mapManager;
