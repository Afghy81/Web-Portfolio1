(function() {
    'use strict';

    // Fungsi untuk mendeteksi dan menonaktifkan Developer Tools
    function detectDevTools() {
        const widthThreshold = window.outerWidth - window.innerWidth > 160;
        const heightThreshold = window.outerHeight - window.innerHeight > 160;
        
        if (widthThreshold || heightThreshold) {
            document.documentElement.innerHTML = 'Access Denied';
            window.location.reload();
        }
    }

    // Disable right click
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        return false;
    }, true);

    // Disable keyboard shortcuts dan dev tools
    document.addEventListener('keydown', function(e) {
        if ([123, 73, 74, 67, 83, 85].includes(e.keyCode) || // F12, I, J, C, S, U
            (e.ctrlKey && e.shiftKey) || // Ctrl+Shift combinations
            (e.ctrlKey && ['s', 'u', 'c', 'i', 'j'].includes(e.key.toLowerCase()))) { // Ctrl combinations
            e.preventDefault();
            return false;
        }
    }, true);

    // Disable text selection and copy/paste
    document.addEventListener('selectstart', e => e.preventDefault());
    document.addEventListener('copy', e => e.preventDefault());
    document.addEventListener('cut', e => e.preventDefault());
    document.addEventListener('paste', e => e.preventDefault());

    // Advanced protection
    setInterval(detectDevTools, 100);
    
    // Console protection
    ['log','debug','info','warn','error','dir','trace'].forEach(function(method) {
        console[method] = function() {};
    });

    // Prevent source viewing
    document.onkeydown = function(e) {
        if (e.ctrlKey && 
            (e.keyCode === 85 || // U
             e.keyCode === 83 || // S
             e.keyCode === 73 || // I
             e.keyCode === 74)) { // J
            return false;
        }
    };

    // Debug prevention
    setInterval(function() {
        debugger;
    }, 100);

})();

// Disable text selection
document.addEventListener('selectstart', (e) => e.preventDefault());

// Disable copy paste
document.addEventListener('copy', (e) => e.preventDefault());
document.addEventListener('cut', (e) => e.preventDefault());
document.addEventListener('paste', (e) => e.preventDefault());

// Additional protection against dev tools
(function () {
    const devtools = {
        isOpen: false,
        orientation: undefined
    };
    
    setInterval(() => {
        const widthThreshold = window.outerWidth - window.innerWidth > 160;
        const heightThreshold = window.outerHeight - window.innerHeight > 160;
        
        if (widthThreshold || heightThreshold) {
            // Dev tools detected
            document.body.innerHTML = 'Developer tools detected!';
        }
    }, 1000);
})();