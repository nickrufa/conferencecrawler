/**
 * IDWeek 2025 PWA - Service Worker
 * Handles offline functionality, caching, and background sync
 */

const CACHE_NAME = 'idweek2025-v1.0.0';
const STATIC_CACHE = 'idweek2025-static-v1.0.0';
const DYNAMIC_CACHE = 'idweek2025-dynamic-v1.0.0';

// Static assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/styles.css',
    '/app.js',
    '/data-manager.js',
    '/ui-components.js',
    '/offline-manager.js',
    '/manifest.json',
    // External CDN assets that we want to cache
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// API endpoints that should be cached dynamically
const API_ENDPOINTS = [
    '../batch1_firecrawl_validated.json',
    '../batch1_firecrawl_summary.json'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('[SW] Installing service worker...');
    
    event.waitUntil(
        Promise.all([
            // Cache static assets
            caches.open(STATIC_CACHE).then(cache => {
                console.log('[SW] Caching static assets...');
                return cache.addAll(STATIC_ASSETS.map(url => 
                    new Request(url, { cache: 'reload' })
                ));
            }),
            // Skip waiting to activate immediately
            self.skipWaiting()
        ])
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[SW] Activating service worker...');
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE &&
                            cacheName !== CACHE_NAME) {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            // Take control immediately
            self.clients.claim()
        ])
    );
});

// Fetch event - serve from cache with network fallback
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip chrome-extension and other non-http(s) requests
    if (!url.protocol.startsWith('http')) {
        return;
    }
    
    // Handle different types of requests
    if (isStaticAsset(request)) {
        event.respondWith(handleStaticAsset(request));
    } else if (isAPIRequest(request)) {
        event.respondWith(handleAPIRequest(request));
    } else if (isNavigationRequest(request)) {
        event.respondWith(handleNavigationRequest(request));
    } else {
        event.respondWith(handleOtherRequest(request));
    }
});

// Handle static assets (cache first strategy)
function handleStaticAsset(request) {
    return caches.match(request).then(cachedResponse => {
        if (cachedResponse) {
            return cachedResponse;
        }
        
        return fetch(request).then(networkResponse => {
            // Cache successful responses
            if (networkResponse.status === 200) {
                const responseClone = networkResponse.clone();
                caches.open(STATIC_CACHE).then(cache => {
                    cache.put(request, responseClone);
                });
            }
            return networkResponse;
        }).catch(error => {
            console.warn('[SW] Failed to fetch static asset:', request.url, error);
            // Return a basic fallback for CSS/JS files
            if (request.url.includes('.css')) {
                return new Response('/* Offline - CSS unavailable */', {
                    headers: { 'Content-Type': 'text/css' }
                });
            }
            if (request.url.includes('.js')) {
                return new Response('// Offline - JS unavailable', {
                    headers: { 'Content-Type': 'application/javascript' }
                });
            }
            throw error;
        });
    });
}

// Handle API requests (network first, cache fallback)
function handleAPIRequest(request) {
    return fetch(request).then(networkResponse => {
        // Cache successful API responses
        if (networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(DYNAMIC_CACHE).then(cache => {
                cache.put(request, responseClone);
                console.log('[SW] Cached API response:', request.url);
            });
        }
        return networkResponse;
    }).catch(error => {
        console.warn('[SW] API request failed, checking cache:', request.url, error);
        
        return caches.match(request).then(cachedResponse => {
            if (cachedResponse) {
                console.log('[SW] Serving API response from cache:', request.url);
                return cachedResponse;
            }
            
            // Return empty response for session data if no cache available
            if (request.url.includes('batch1_firecrawl_validated.json')) {
                return new Response('[]', {
                    headers: { 'Content-Type': 'application/json' },
                    status: 200
                });
            }
            
            throw error;
        });
    });
}

// Handle navigation requests (cache first with network update)
function handleNavigationRequest(request) {
    return caches.match('/index.html').then(cachedResponse => {
        const fetchPromise = fetch(request).then(networkResponse => {
            // Update cache with fresh version
            if (networkResponse.status === 200) {
                const responseClone = networkResponse.clone();
                caches.open(STATIC_CACHE).then(cache => {
                    cache.put('/index.html', responseClone);
                });
            }
            return networkResponse;
        }).catch(error => {
            console.warn('[SW] Navigation request failed:', request.url, error);
            return cachedResponse;
        });
        
        // Return cached version immediately if available
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Otherwise wait for network
        return fetchPromise;
    });
}

// Handle other requests (network first)
function handleOtherRequest(request) {
    return fetch(request).then(networkResponse => {
        // Cache successful responses for future offline use
        if (networkResponse.status === 200 && 
            networkResponse.headers.get('content-type')?.includes('text/')) {
            const responseClone = networkResponse.clone();
            caches.open(DYNAMIC_CACHE).then(cache => {
                cache.put(request, responseClone);
            });
        }
        return networkResponse;
    }).catch(error => {
        console.warn('[SW] Other request failed:', request.url, error);
        
        return caches.match(request).then(cachedResponse => {
            if (cachedResponse) {
                return cachedResponse;
            }
            throw error;
        });
    });
}

// Background sync for data updates
self.addEventListener('sync', event => {
    console.log('[SW] Background sync triggered:', event.tag);
    
    if (event.tag === 'session-data-sync') {
        event.waitUntil(syncSessionData());
    } else if (event.tag === 'user-preferences-sync') {
        event.waitUntil(syncUserPreferences());
    }
});

// Sync session data in background
async function syncSessionData() {
    try {
        console.log('[SW] Syncing session data...');
        const response = await fetch('../batch1_firecrawl_validated.json');
        
        if (response.ok) {
            const data = await response.json();
            
            // Update cache
            const cache = await caches.open(DYNAMIC_CACHE);
            await cache.put('../batch1_firecrawl_validated.json', response.clone());
            
            // Notify clients of update
            const clients = await self.clients.matchAll();
            clients.forEach(client => {
                client.postMessage({
                    type: 'DATA_UPDATED',
                    data: { sessions: data.length }
                });
            });
            
            console.log('[SW] Session data synced successfully');
        }
    } catch (error) {
        console.error('[SW] Failed to sync session data:', error);
    }
}

// Sync user preferences (placeholder for future backend integration)
async function syncUserPreferences() {
    try {
        console.log('[SW] Syncing user preferences...');
        // This would sync bookmarks, filters, etc. with a backend service
        // For now, just log that sync was attempted
        console.log('[SW] User preferences sync completed (local only)');
    } catch (error) {
        console.error('[SW] Failed to sync user preferences:', error);
    }
}

// Handle push notifications (for future SMS integration)
self.addEventListener('push', event => {
    console.log('[SW] Push notification received');
    
    if (!event.data) {
        return;
    }
    
    try {
        const data = event.data.json();
        const options = {
            body: data.body || 'New update available',
            icon: '/icons/icon-192x192.png',
            badge: '/icons/icon-72x72.png',
            tag: data.tag || 'default',
            requireInteraction: data.requireInteraction || false,
            actions: data.actions || [
                {
                    action: 'view',
                    title: 'View',
                    icon: '/icons/icon-72x72.png'
                },
                {
                    action: 'dismiss',
                    title: 'Dismiss'
                }
            ],
            data: data.data || {}
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title || 'IDWeek 2025', options)
        );
    } catch (error) {
        console.error('[SW] Error handling push notification:', error);
    }
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/').then(client => {
                if (client && event.notification.data.sessionId) {
                    // Focus on specific session
                    client.postMessage({
                        type: 'SHOW_SESSION',
                        sessionId: event.notification.data.sessionId
                    });
                }
            })
        );
    }
});

// Message handling from main app
self.addEventListener('message', event => {
    console.log('[SW] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    } else if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(cacheUrls(event.data.urls));
    } else if (event.data && event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(clearCaches());
    }
});

// Cache additional URLs on demand
async function cacheUrls(urls) {
    try {
        const cache = await caches.open(DYNAMIC_CACHE);
        await cache.addAll(urls);
        console.log('[SW] Additional URLs cached:', urls.length);
    } catch (error) {
        console.error('[SW] Failed to cache additional URLs:', error);
    }
}

// Clear all caches
async function clearCaches() {
    try {
        const cacheNames = await caches.keys();
        await Promise.all(cacheNames.map(cacheName => caches.delete(cacheName)));
        console.log('[SW] All caches cleared');
    } catch (error) {
        console.error('[SW] Failed to clear caches:', error);
    }
}

// Utility functions
function isStaticAsset(request) {
    const url = new URL(request.url);
    return STATIC_ASSETS.some(asset => url.pathname.includes(asset)) ||
           url.pathname.includes('.css') ||
           url.pathname.includes('.js') ||
           url.pathname.includes('.png') ||
           url.pathname.includes('.jpg') ||
           url.pathname.includes('.ico');
}

function isAPIRequest(request) {
    const url = new URL(request.url);
    return API_ENDPOINTS.some(endpoint => url.pathname.includes(endpoint)) ||
           url.pathname.includes('.json');
}

function isNavigationRequest(request) {
    return request.mode === 'navigate' || 
           (request.method === 'GET' && 
            request.headers.get('accept')?.includes('text/html'));
}

// Error handling
self.addEventListener('error', event => {
    console.error('[SW] Service worker error:', event.error);
});

self.addEventListener('unhandledrejection', event => {
    console.error('[SW] Unhandled promise rejection:', event.reason);
});

console.log('[SW] Service worker loaded successfully');