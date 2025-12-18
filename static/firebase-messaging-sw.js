// Scripts for Firebase Cloud Messaging
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

// Initialize the Firebase app in the service worker by passing in the messagingSenderId
firebase.initializeApp({
    apiKey: "AIzaSyA_zXhDXEVZNsJiAcxFU1UnLJkvS6FhaIc",
    authDomain: "tutiontrack-48c6e.firebaseapp.com",
    projectId: "tutiontrack-48c6e",
    storageBucket: "tutiontrack-48c6e.firebasestorage.app",
    messagingSenderId: "608607247798",
    appId: "1:608607247798:web:2ca2ae115cf9c89f88b517"
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
