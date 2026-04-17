// Custom navigation links for OpenWebUI
// This script adds external links to the OpenWebUI navbar

(function() {
    'use strict';
    
    // Wait for the page to load
    document.addEventListener('DOMContentLoaded', function() {
        addCustomLinks();
    });
    
    // Also try when the main app loads
    window.addEventListener('load', function() {
        setTimeout(addCustomLinks, 2000);
    });
    
    function addCustomLinks() {
        // Find the navbar - try multiple selectors
        const navbarSelectors = [
            'nav', 
            '.navbar', 
            '[class*="nav"]',
            'header'
        ];
        
        let navbar = null;
        for (const selector of navbarSelectors) {
            navbar = document.querySelector(selector);
            if (navbar) break;
        }
        
        if (!navbar) {
            console.log('CustomNav: Navbar not found, will retry...');
            setTimeout(addCustomLinks, 3000);
            return;
        }
        
        // Check if we've already added our links
        if (document.getElementById('custom-nav-grilo')) {
            return;
        }
        
        // Create the Grilo Falante link
        const griloLink = document.createElement('a');
        griloLink.id = 'custom-nav-grilo';
        griloLink.href = 'http://localhost:8005/visualizer';
        griloLink.target = '_blank';
        griloLink.className = 'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors';
        griloLink.innerHTML = `
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
            </svg>
            <span>Grilo Worlds</span>
        `;
        
        // Find a good place to add it - try to find the nav container
        const navContainer = navbar.querySelector('div[class*="flex"]') || navbar.querySelector('ul') || navbar;
        
        if (navContainer) {
            navContainer.appendChild(griloLink);
            console.log('CustomNav: Grilo Falante link added to navbar');
        }
    }
})();
