/**
 * Push Notification Subscription Management
 * Handles subscribing and unsubscribing from push notifications
 */

const VAPID_PUBLIC_KEY = window.VAPID_PUBLIC_KEY || '';

// Convert VAPID public key from base64url to Uint8Array
function urlBase64ToUint8Array(base64String) {
    if (!base64String || typeof base64String !== 'string') {
        throw new Error('VAPID public key is missing or invalid');
    }

    // Remove any whitespace
    base64String = base64String.trim();

    // Add padding if needed (base64url doesn't use padding, but atob needs it)
    const padding = '='.repeat((4 - base64String.length % 4) % 4);

    // Convert base64url to base64 (replace - with + and _ with /)
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    try {
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    } catch (error) {
        console.error('Error decoding base64:', error);
        throw new Error('Failed to decode VAPID public key: ' + error.message);
    }
}

// Update foreground message handling
function handleForegroundMessage(payload) {
    console.log('Received foreground message:', payload);
    const notification = payload.notification || {};
    const data = payload.data || {};

    // Show SweetAlert for foreground notifications
    if (window.Swal) {
        window.Swal.fire({
            title: notification.title || 'Notification',
            text: notification.body || '',
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'View',
            cancelButtonText: 'Close',
            toast: true,
            position: 'top-end',
            timer: 10000,
            timerProgressBar: true
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = data.url || data.click_action || '/';
            }
        });
    }
}

// Get FCM Token
async function getFCMToken() {
    try {
        if (!window.messaging) {
            console.log('Firebase Messaging not initialized');
            return null;
        }

        // VAPID key for FCM
        const vapidKey = window.FIREBASE_WEB_VAPID_KEY || '';

        const currentToken = await window.messaging.getToken({
            vapidKey: vapidKey
        });

        if (currentToken) {
            console.log('FCM Token generated:', currentToken);
            return currentToken;
        } else {
            console.log('No registration token available. Request permission to generate one.');
            return null;
        }
    } catch (err) {
        console.error('An error occurred while retrieving token: ', err);
        return null;
    }
}

// Subscribe to push notifications
async function subscribeToPushNotifications() {
    console.log('subscribeToPushNotifications called');

    // Check for required APIs
    const hasServiceWorker = 'serviceWorker' in navigator;
    const hasPushManager = 'PushManager' in window;
    const hasNotifications = 'Notification' in window;
    const isLocalhost = location.hostname === 'localhost' || location.hostname === '127.0.0.1';
    const isSecureContext = window.isSecureContext || location.protocol === 'https:' || isLocalhost;

    if (!hasNotifications) {
        return { success: false, message: 'Notifications API is not supported' };
    }

    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
        return { success: false, message: 'Permission denied' };
    }

    // Try FCM first if messaging is available
    if (window.messaging) {
        const fcmToken = await getFCMToken();
        if (fcmToken) {
            // Subscribe to FCM on server
            try {
                const response = await fetch('/api/push/subscribe', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        token_type: 'fcm',
                        fcm_token: fcmToken
                    })
                });

                if (response.ok) {
                    console.log('FCM subscription successful');

                    // Listen for foreground messages
                    window.messaging.onMessage((payload) => {
                        handleForegroundMessage(payload);
                    });

                    return { success: true, message: 'Subscribed via FCM' };
                }
            } catch (err) {
                console.error('FCM subscription failed, falling back to Web Push:', err);
            }
        }
    }

    // Fallback to Web Push
    if (!hasServiceWorker || !hasPushManager || !isSecureContext || !VAPID_PUBLIC_KEY) {
        return { success: false, message: 'Push notifications not supported or configured' };
    }

    try {
        const registration = await navigator.serviceWorker.ready;
        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            const applicationServerKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: applicationServerKey
            });
        }

        const subscriptionJson = {
            token_type: 'webpush',
            endpoint: subscription.endpoint,
            keys: {
                p256dh: btoa(String.fromCharCode.apply(null, new Uint8Array(subscription.getKey('p256dh')))),
                auth: btoa(String.fromCharCode.apply(null, new Uint8Array(subscription.getKey('auth'))))
            }
        };

        const response = await fetch('/api/push/subscribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(subscriptionJson)
        });

        if (response.ok) {
            return { success: true, message: 'Subscribed via Web Push' };
        } else {
            const error = await response.json();
            return { success: false, message: error.error || 'Failed to subscribe' };
        }
    } catch (error) {
        console.error('Web Push subscription error:', error);
        return { success: false, message: error.message || 'Subscription failed' };
    }
}

// Unsubscribe from push notifications
async function unsubscribeFromPushNotifications() {
    try {
        let fcmSuccess = false;
        let webPushSuccess = false;

        // Try FCM unsubscribe if available
        if (window.messaging) {
            const fcmToken = await getFCMToken();
            if (fcmToken) {
                const response = await fetch('/api/push/unsubscribe', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ fcm_token: fcmToken })
                });
                if (response.ok) fcmSuccess = true;
            }
        }

        // Web Push unsubscribe
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();

        if (subscription) {
            const endpoint = subscription.endpoint;
            await subscription.unsubscribe();

            const response = await fetch('/api/push/unsubscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ endpoint: endpoint })
            });
            if (response.ok) webPushSuccess = true;
        }

        if (fcmSuccess || webPushSuccess) {
            console.log('Successfully unsubscribed from push notifications');
            return { success: true, message: 'Unsubscribed from push notifications' };
        }

        return { success: false, message: 'Not subscribed' };
    } catch (error) {
        console.error('Error unsubscribing:', error);
        return { success: false, message: error.message };
    }
}

// Check subscription status
async function checkPushSubscriptionStatus() {
    try {
        // Check if Notification API is available
        if (!('Notification' in window)) {
            return { subscribed: false, permission: 'default' };
        }

        const permission = Notification.permission || 'default';

        // If push notifications aren't supported, just return permission status
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
            return { subscribed: false, permission: permission };
        }

        // Wait for service worker to be ready (with longer timeout and retry)
        let registration;
        try {
            // First check if service worker is already registered
            if (navigator.serviceWorker.controller) {
                // Service worker is controlling the page
                registration = await navigator.serviceWorker.ready;
            } else {
                // Wait for service worker to be ready (with timeout)
                registration = await Promise.race([
                    navigator.serviceWorker.ready,
                    new Promise((_, reject) => setTimeout(() => reject(new Error('Service worker timeout')), 10000))
                ]);
            }

            // Check subscription
            const subscription = await registration.pushManager.getSubscription();
            const isSubscribed = !!subscription;

            console.log('Subscription status check:', {
                hasSubscription: isSubscribed,
                permission: permission,
                endpoint: subscription ? subscription.endpoint.substring(0, 50) + '...' : 'none'
            });

            return { subscribed: isSubscribed, permission: permission };
        } catch (swError) {
            // Service worker not ready or error accessing it
            console.log('Service worker not ready, checking registration:', swError);

            // Try to get registration without waiting
            try {
                const registrations = await navigator.serviceWorker.getRegistrations();
                if (registrations.length > 0) {
                    const reg = registrations[0];
                    const subscription = await reg.pushManager.getSubscription();
                    return { subscribed: !!subscription, permission: permission };
                }
            } catch (regError) {
                console.log('Could not get registrations:', regError);
            }

            return { subscribed: false, permission: permission };
        }
    } catch (error) {
        console.error('Error checking subscription status:', error);
        return { subscribed: false, permission: Notification.permission || 'default' };
    }
}

// Make functions globally available
window.subscribeToPushNotifications = subscribeToPushNotifications;
window.unsubscribeFromPushNotifications = unsubscribeFromPushNotifications;
window.checkPushSubscriptionStatus = checkPushSubscriptionStatus;

