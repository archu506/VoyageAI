// ATIG Main JavaScript

console.log('ATIG Application loaded');

// Utility function to load attractions
async function loadAttractions() {
    try {
        const response = await fetch('/api/attractions');
        const data = await response.json();
        return data.success ? data.data : [];
    } catch (error) {
        console.error('Error loading attractions:', error);
        return [];
    }
}

// Utility function to optimize itinerary
async function optimizeRoute(attractions, timeBudget, transportMode) {
    try {
        const response = await fetch('/api/optimize-itinerary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                attractions,
                time_budget_hours: timeBudget,
                transport_mode: transportMode
            })
        });
        const data = await response.json();
        return data.success ? data : null;
    } catch (error) {
        console.error('Error optimizing route:', error);
        return null;
    }
}

// Smooth scroll
function smoothScroll(target) {
    document.querySelector(target).scrollIntoView({
        behavior: 'smooth'
    });
}

// Format timestamp
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.getHours() + ':' + String(date.getMinutes()).padStart(2, '0');
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Add any global event listeners
    console.log('ATIG ready');
});
