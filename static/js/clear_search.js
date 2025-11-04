document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
      // Automatically clear the search field after search
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.has('q')) {
        searchInput.value = ''; // clear the field
        searchInput.focus();    // focus for next scan
      }
    }
  });
  