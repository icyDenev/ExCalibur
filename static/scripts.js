function acceptSuggestion(suggestionId) {
    window.location.href = '/accept_suggestion/' + suggestionId;
}

function declineSuggestion(suggestionId) {
    window.location.href = '/decline_suggestion/' + suggestionId;
}
