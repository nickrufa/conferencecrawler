// Configuration for Conference Crawler
// This gets the conference ID from URL parameters since ColdFusion variables don't work in external JS files

function getConferenceId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('confid') || urlParams.get('conference_id') || '1'; // Default to 1 if not specified
}

// Export for use in other scripts
window.CONFERENCE_CONFIG = {
    getConferenceId: getConferenceId
};