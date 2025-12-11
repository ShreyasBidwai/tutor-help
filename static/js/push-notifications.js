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

// Subscribe to push notifications
async function subscribeToPushNotifications() {
    console.log('subscribeToPushNotifications called');
    
    // Check for required APIs
    const hasServiceWorker = 'serviceWorker' in navigator;
    const hasPushManager = 'PushManager' in window;
    const hasNotifications = 'Notification' in window;
    // Allow localhost, 127.0.0.1, and local network IPs (192.168.x.x, 10.x.x.x, 172.16-31.x.x) for development
    const isLocalhost = location.hostname === 'localhost' || location.hostname === '127.0.0.1' || 
                       location.hostname.startsWith('192.168.') || location.hostname.startsWith('10.') || 
                       location.hostname.match(/^172\.(1[6-9]|2[0-9]|3[01])\./);
    const isSecureContext = window.isSecureContext || location.protocol === 'https:' || isLocalhost;
    
    console.log('Browser support check:', {
        serviceWorker: hasServiceWorker,
        pushManager: hasPushManager,
        notifications: hasNotifications,
        secureContext: isSecureContext,
        isLocalhost: isLocalhost,
        protocol: location.protocol,
        hostname: location.hostname
    });
    
    if (!hasNotifications) {
        return { success: false, message: 'Notifications API is not supported in this browser' };
    }
    
    if (!hasServiceWorker) {
        return { success: false, message: 'Service Workers are not supported in this browser. Please use a modern browser like Chrome, Firefox, or Edge.' };
    }
    
    if (!hasPushManager) {
        return { success: false, message: 'Push Manager is not supported in this browser. Please use a modern browser.' };
    }
    
    if (!isSecureContext) {
        return { success: false, message: 'Push notifications require HTTPS. Please access the site over HTTPS or use localhost.' };
    }
    
    // Check if VAPID key is available
    if (!VAPID_PUBLIC_KEY) {
        console.error('VAPID_PUBLIC_KEY is not set');
        return { success: false, message: 'Push notification configuration is missing' };
    }
    
    try {
        // Request notification permission
        console.log('Requesting notification permission...');
        const permission = await Notification.requestPermission();
        console.log('Permission result:', permission);
        
        if (permission !== 'granted') {
            return { success: false, message: 'Notification permission denied' };
        }
        
        // Get service worker registration with timeout
        console.log('Waiting for service worker to be ready...');
        let registration;
        try {
            registration = await Promise.race([
                navigator.serviceWorker.ready,
                new Promise((_, reject) => setTimeout(() => reject(new Error('Service worker timeout')), 10000))
            ]);
            console.log('Service worker ready:', registration);
        } catch (swError) {
            console.error('Service worker not ready:', swError);
            // Try to register service worker if not already registered
            try {
                registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
                await registration.ready;
                console.log('Service worker registered and ready');
            } catch (regError) {
                console.error('Failed to register service worker:', regError);
                return { success: false, message: 'Service worker not available. Please refresh the page.' };
            }
        }
        
        // Check if already subscribed
        let subscription = await registration.pushManager.getSubscription();
        console.log('Current subscription:', subscription ? 'exists' : 'none');
        
        if (!subscription) {
            // Subscribe to push
            console.log('Subscribing to push notifications...');
            console.log('VAPID_PUBLIC_KEY:', VAPID_PUBLIC_KEY ? VAPID_PUBLIC_KEY.substring(0, 20) + '...' : 'MISSING');
            
            // Convert VAPID key to Uint8Array
            let applicationServerKey;
            try {
                applicationServerKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
                console.log('ApplicationServerKey length:', applicationServerKey.length);
                
                // VAPID public key should be 65 bytes (uncompressed point: 0x04 + 32-byte X + 32-byte Y)
                if (applicationServerKey.length !== 65) {
                    console.error('Invalid VAPID key length. Expected 65 bytes, got:', applicationServerKey.length);
                    return { success: false, message: 'Invalid VAPID public key format. Please check server configuration.' };
                }
            } catch (keyError) {
                console.error('Error converting VAPID key:', keyError);
                return { success: false, message: 'Invalid VAPID public key. Please check server configuration.' };
            }
            
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: applicationServerKey
            });
            console.log('Subscribed successfully');
        }
        
        // Convert subscription to JSON format
        const subscriptionJson = {
            endpoint: subscription.endpoint,
            keys: {
                p256dh: btoa(String.fromCharCode.apply(null, new Uint8Array(subscription.getKey('p256dh')))),
                auth: btoa(String.fromCharCode.apply(null, new Uint8Array(subscription.getKey('auth'))))
            }
        };
        
        // Send subscription to server
        const response = await fetch('/api/push/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(subscriptionJson)
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Successfully subscribed to push notifications');
            return { success: true, message: 'Subscribed to push notifications' };
        } else {
            const error = await response.json();
            console.error('Failed to subscribe:', error);
            return { success: false, message: error.error || 'Failed to subscribe' };
        }
    } catch (error) {
        console.error('Error subscribing to push notifications:', error);
        return { success: false, message: error.message || 'Subscription failed' };
    }
}

// Unsubscribe from push notifications
async function unsubscribeFromPushNotifications() {
    try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        
        if (subscription) {
            await subscription.unsubscribe();
            
            // Notify server
            const response = await fetch('/api/push/unsubscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    endpoint: subscription.endpoint
                })
            });
            
            if (response.ok) {
                console.log('Successfully unsubscribed from push notifications');
                return { success: true, message: 'Unsubscribed from push notifications' };
            }
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

