// --- CSRF helper ---
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// --- Form submission ---
const form = document.getElementById('regForm');
if (form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const fd = new FormData(form);

    // Capture location before sending
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(async (pos) => {
        fd.set('latitude', pos.coords.latitude);
        fd.set('longitude', pos.coords.longitude);

        await submitForm(fd);
      }, () => {
        // fallback if user denies location
        submitForm(fd);
      });
    } else {
      submitForm(fd);
    }
  });
}

// --- Submit function ---
async function submitForm(fd) {
  try {
    const res = await fetch('/api/applications/', {
      method: 'POST',
      headers: { 'X-CSRFToken': csrftoken },
      body: fd,
    });

    const data = await res.json();
    if (res.ok) {
      document.getElementById('message').textContent =
        '✅ Application received! Reference ID: ' + data.id;
      form.reset();
    } else {
      document.getElementById('message').textContent =
        '❌ ' + (data.error || 'Submission failed');
    }
  } catch (err) {
    document.getElementById('message').textContent =
      '⚠️ Network error. Try again later.';
  }
}

