// Scripts for Firebase Cloud Messaging
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

// Initialize the Firebase app in the service worker by passing in the messagingSenderId
firebase.initializeApp({
    apiKey: "FIREBASE_WEB_API_KEY", // Will be replaced or injected if possible, but senderId is often enough for SW
    authDomain: "FIREBASE_WEB_AUTH_DOMAIN",
    projectId: "FIREBASE_WEB_PROJECT_ID",
    storageBucket: "FIREBASE_WEB_STORAGE_BUCKET",
    messagingSenderId: "FIREBASE_MESSAGING_SENDER_ID",
    appId: "FIREBASE_WEB_APP_ID"
});

const messaging = firebase.messaging();

// Background message handler
messaging.onBackgroundMessage((payload) => {
    console.log('[firebase-messaging-sw.js] Received background message ', payload);

    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: payload.notification.image || '/static/TutionTrack_appIcon_192x192.png',
        badge: '/static/TutionTrack_appIcon_96x96.png',
        data: payload.data || {},
        vibrate: [200, 100, 200],
        tag: payload.data ? payload.data.type : 'default'
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});

// For TWA/APK support, we also listen to the same events as the existing SW
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    event.notification.close();

    const data = event.notification.data || {};
    let urlToOpen = data.url || data.click_action || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            for (let i = 0; i < clientList.length; i++) {
                const client = clientList[i];
                if (client.url.includes(urlToOpen) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(urlToOpen);
            }
        })
    );
});
