
    < !--Native - like Back Button Handling-- >
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Only run on dashboard pages (root of the app)
            const isDashboard = window.location.pathname === '/dashboard' || window.location.pathname === '/student/dashboard' || window.location.pathname === '/';

        if (isDashboard) {
            // native-like "double back to exit" feel
            // In a browser, we can't truly "exit", but we can trap the back button 
            // to prevent going back to login/welcome pages.

            // Push a state to create a history entry we can trap
            history.pushState({ page: 'dashboard' }, document.title, window.location.href);

        let backPressedTime = 0;

        window.addEventListener('popstate', function(event) {
                    const now = Date.now();

        // If back pressed within 2 seconds
        if (now - backPressedTime < 2000) {
                        // Let it go back (which might exit PWA or go to previous site)
                        // Ideally we would close the app here if possible
                        // window.close() only works for scripts, but in PWA context 
                        // history.back() at root might minimize.
                        // However, since we pushed a state, "back" just popped that state.
                        // We are now at the state BEFORE we pushed.

                        // If we want to truly exit, we can try navigating to a special "exit" page or just let it be.
                        // But users requested "close the app".
                        // In browser, best we can do is let them leave the domain.
                        return; 
                    }

        // First back press: trap it and show toast
        backPressedTime = now;

        // Push state again to re-trap
        history.pushState({page: 'dashboard' }, document.title, window.location.href);

        // Show "Press back again to exit" toast
        const toast = Swal.mixin({
            toast: true,
        position: 'bottom',
        showConfirmButton: false,
        timer: 2000,
        timerProgressBar: false,
                        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
                            toast.addEventListener('mouseleave', Swal.resumeTimer)
                        }
                    });

        toast.fire({
            icon: 'info',
        title: 'Press back again to exit'
                    });
                });
            }
        });
    </script>
