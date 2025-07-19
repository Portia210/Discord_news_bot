/**
 * News Report JavaScript
 * Handles theme switching and initialization for news reports
 */

// Theme handling
let reportTime = window.reportTime || 'auto'; // Get from template or default

function setTheme() {
    const morningTheme = document.getElementById('morning-theme');
    const eveningTheme = document.getElementById('evening-theme');
    const themeIcon = document.getElementById('theme-icon');
    
    if (reportTime === 'morning') {
        // Morning theme
        morningTheme.disabled = false;
        eveningTheme.disabled = true;
        document.body.setAttribute('data-theme', 'morning');
        themeIcon.textContent = '☀️';
    } else if (reportTime === 'evening') {
        // Evening theme
        morningTheme.disabled = true;
        eveningTheme.disabled = false;
        document.body.setAttribute('data-theme', 'evening');
        themeIcon.textContent = '🌙';
    } else {
        // Auto-detect based on current time
        const now = new Date();
        const hour = now.getHours();
        
        if (hour >= 6 && hour < 18) {
            // Morning theme
            morningTheme.disabled = false;
            eveningTheme.disabled = true;
            document.body.setAttribute('data-theme', 'morning');
            themeIcon.textContent = '☀️';
        } else {
            // Evening theme
            morningTheme.disabled = true;
            eveningTheme.disabled = false;
            document.body.setAttribute('data-theme', 'evening');
            themeIcon.textContent = '🌙';
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    setTheme();
    
    // Set generation time if not already set
    const generationTime = document.getElementById('generation-time');
    if (!generationTime.textContent) {
        generationTime.textContent = new Date().toLocaleString('he-IL');
    }
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { setTheme };
} 