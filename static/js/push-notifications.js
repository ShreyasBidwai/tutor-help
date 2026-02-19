/**
 * Push Notification Subscription Management using Firebase Cloud Messaging (FCM)
 * Handles subscribing and unsubscribing from push notifications
 */

// Subscribe to push notifications
async function subscribeToPushNotifications() {
    console.log('subscribeToPushNotifications called');

    // Check if Firebase is initialized and messaging is supported
    if (typeof firebase === 'undefined' || !firebase.messaging || !messaging) {
        console.warn('Firebase messaging not initialized or not supported.');
        return { success: false, message: 'Push notifications not supported in this browser.' };
    }

    // Check for required APIs
    if (!('Notification' in window)) {
        return { success: false, message: 'Notifications API is not supported in this browser' };
    }

    if (!('serviceWorker' in navigator)) {
        return { success: false, message: 'Service Workers are not supported in this browser.' };
    }

    try {
        // Request notification permission
        const permission = await Notification.requestPermission();
        console.log('Permission result:', permission);

        if (permission !== 'granted') {
            return { success: false, message: 'Notification permission denied' };
        }

        // Wait for service worker
        const registration = await navigator.serviceWorker.ready;

        // Get FCM Token
        console.log('Getting FCM token...');

        // Delete old cached token to force fresh generation
        try {
            await messaging.deleteToken();
            console.log('Old token deleted');
        } catch (e) {
            console.log('No old token to delete');
        }

        const tokenOptions = { serviceWorkerRegistration: registration };
        // Add VAPID key if available (required for stable tokens)
        if (window.VAPID_PUBLIC_KEY && window.VAPID_PUBLIC_KEY !== 'your-vapid-public-key-here') {
            tokenOptions.vapidKey = window.VAPID_PUBLIC_KEY;
        }
        const currentToken = await messaging.getToken(tokenOptions);

        if (currentToken) {
            console.log('FCM Token received:', currentToken.substring(0, 20) + '...');

            // Send token to server
            const response = await fetch('/api/push/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: currentToken })
            });

            if (response.ok) {
                console.log('Successfully subscribed to push notifications');
                return { success: true, message: 'Subscribed to push notifications' };
            } else {
                const error = await response.json();
                console.error('Failed to subscribe:', error);
                return { success: false, message: error.error || 'Failed to subscribe' };
            }
        } else {
            console.log('No registration token available. Request permission to generate one.');
            return { success: false, message: 'Failed to generate token' };
        }

    } catch (error) {
        console.error('Error subscribing to push notifications:', error);
        return { success: false, message: error.message || 'Subscription failed' };
    }
}

// Unsubscribe from push notifications
async function unsubscribeFromPushNotifications() {
    try {
        if (typeof firebase === 'undefined' || !firebase.messaging) {
            return { success: false, message: 'Firebase not initialized' };
        }

        // Get current token to delete from server
        const currentToken = await messaging.getToken();

        if (currentToken) {
            // Delete from server first
            await fetch('/api/push/unsubscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: currentToken })
            });

            // Delete from Firebase
            await messaging.deleteToken();
            console.log('Token deleted.');
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
        if (!('Notification' in window)) {
            return { subscribed: false, permission: 'default' };
        }

        const permission = Notification.permission || 'default';

        if (permission === 'granted' && typeof firebase !== 'undefined') {
            const currentToken = await messaging.getToken();
            return { subscribed: !!currentToken, permission: permission };
        }

        return { subscribed: false, permission: permission };
    } catch (error) {
        console.error('Error checking subscription status:', error);
        return { subscribed: false, permission: Notification.permission || 'default' };
    }
}

// Make functions globally available
window.subscribeToPushNotifications = subscribeToPushNotifications;
window.unsubscribeFromPushNotifications = unsubscribeFromPushNotifications;
window.checkPushSubscriptionStatus = checkPushSubscriptionStatus;
