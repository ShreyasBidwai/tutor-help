// Service Worker for TuitionTrack PWA
const CACHE_NAME = 'tuitiontrack-v1';
const STATIC_CACHE = 'static-v1';
const DYNAMIC_CACHE = 'dynamic-v1';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/TutionTrack_appIcon.png',
  '/static/TutionTrack_headerLogo.png',
  '/static/TutionTrack_logoNoBG.png',
  '/static/js/swipe-gestures.js',
  '/static/js/form-validation.js',
  '/static/js/tours.js'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE).then((cache) => {
            console.log('Caching static assets');
            return cache.addAll(STATIC_ASSETS.map(url => new Request(url, { cache: 'reload' })));
        }).catch((error) => {
            console.error('Error caching static assets:', error);
        })
    );
    self.skipWaiting(); // Activate immediately
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME && 
                        cacheName !== STATIC_CACHE && 
                        cacheName !== DYNAMIC_CACHE) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    return self.clients.claim(); // Take control of all pages
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip cross-origin requests
    if (url.origin !== location.origin) {
        return;
    }

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Strategy: Cache First, then Network
    event.respondWith(
        caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
                return cachedResponse;
            }

            return fetch(request).then((response) => {
                // Don't cache non-successful responses
                if (!response || response.status !== 200 || response.type !== 'basic') {
                    return response;
                }

                // Clone the response
                const responseToCache = response.clone();

                // Cache dynamic content
                caches.open(DYNAMIC_CACHE).then((cache) => {
                    cache.put(request, responseToCache);
                });

                return response;
            }).catch(() => {
                // Network failed, try to serve offline page
                if (request.headers.get('accept').includes('text/html')) {
                    return caches.match('/');
                }
            });
        })
    );
});

// Push event - handle incoming push notifications
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event);
    
    let notificationData = {
        title: 'TuitionTrack',
        body: 'You have a new notification',
        icon: '/static/TutionTrack_appIcon.png',
        badge: '/static/TutionTrack_appIcon.png',
        tag: 'default',
        requireInteraction: false,
        data: {}
    };

    // Parse push data if available
    if (event.data) {
        try {
            const data = event.data.json();
            notificationData = {
                title: data.title || notificationData.title,
                body: data.body || notificationData.body,
                icon: data.icon || notificationData.icon,
                badge: data.badge || notificationData.badge,
                tag: data.tag || notificationData.tag,
                requireInteraction: data.requireInteraction || false,
                data: data.data || {},
                actions: data.actions || []
            };
        } catch (e) {
            notificationData.body = event.data.text();
        }
    }

    // Check if app is open (has active clients)
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            if (clientList.length > 0) {
                // App is open - send message to show SweetAlert instead of browser notification
                console.log('App is open, sending message to show SweetAlert');
                clientList.forEach(client => {
                    client.postMessage({
                        type: 'push-notification',
                        title: notificationData.title,
                        body: notificationData.body,
                        icon: notificationData.icon,
                        data: notificationData.data,
                        url: notificationData.data.url || '/'
                    });
                });
            } else {
                // App is closed - show browser notification
                console.log('App is closed, showing browser notification');
                return self.registration.showNotification(notificationData.title, {
                    body: notificationData.body,
                    icon: notificationData.icon,
                    badge: notificationData.badge,
                    tag: notificationData.tag,
                    requireInteraction: notificationData.requireInteraction,
                    data: notificationData.data,
                    actions: notificationData.actions,
                    vibrate: [200, 100, 200],
                    timestamp: Date.now()
                });
            }
        })
    );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();

    const notificationData = event.notification.data;
    let urlToOpen = '/';

    // Determine URL based on notification type
    if (notificationData.type === 'homework') {
        urlToOpen = '/student/homework';
    } else if (notificationData.type === 'attendance') {
        urlToOpen = '/student/dashboard';
    } else if (notificationData.type === 'batch_start') {
        urlToOpen = '/student/dashboard';
    } else if (notificationData.url) {
        urlToOpen = notificationData.url;
    }

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            // Check if app is already open
            for (let i = 0; i < clientList.length; i++) {
                const client = clientList[i];
                if (client.url.includes(urlToOpen) && 'focus' in client) {
                    return client.focus();
                }
            }
            // Open new window if app is not open
            if (clients.openWindow) {
                return clients.openWindow(urlToOpen);
            }
        })
    );
});

// Background sync (for offline support)
self.addEventListener('sync', (event) => {
    console.log('Background sync:', event.tag);
    
    if (event.tag === 'sync-attendance') {
        event.waitUntil(syncAttendance());
    } else if (event.tag === 'sync-homework') {
        event.waitUntil(syncHomework());
    }
});

// Sync attendance data
async function syncAttendance() {
    try {
        // Get pending attendance from IndexedDB or cache
        // Then sync with server
        console.log('Syncing attendance...');
        // Implementation depends on your offline storage strategy
    } catch (error) {
        console.error('Error syncing attendance:', error);
    }
}

// Sync homework data
async function syncHomework() {
    try {
        console.log('Syncing homework...');
        // Implementation depends on your offline storage strategy
    } catch (error) {
        console.error('Error syncing homework:', error);
    }
}

// Message event - handle messages from main thread
self.addEventListener('message', (event) => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(DYNAMIC_CACHE).then((cache) => {
                return cache.addAll(event.data.urls);
            })
        );
    }
});

