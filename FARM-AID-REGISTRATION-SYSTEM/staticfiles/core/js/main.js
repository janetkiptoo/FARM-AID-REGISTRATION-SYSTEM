const API_BASE = "http://127.0.0.1:8000/api";  // Django backend

// Registration form submit
document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const data = {
        name: document.getElementById("name").value,
        id_number: document.getElementById("idNumber").value,
        farm_size: document.getElementById("farmSize").value,
      };

      try {
        const response = await fetch(`${API_BASE}/applications/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });

        if (response.ok) {
          alert("✅ Application submitted successfully!");
          registerForm.reset();
        } else {
          alert("❌ Failed to submit application. Please try again.");
        }
      } catch (error) {
        console.error("Error submitting application:", error);
        alert("⚠️ Network error. Check backend server.");
      }
    });
  }

  // Status check
  const statusForm = document.getElementById("statusForm");
  if (statusForm) {
    statusForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const idNumber = document.getElementById("idNumberStatus").value;

      try {
        const response = await fetch(`${API_BASE}/applications/?id_number=${idNumber}`);
        if (response.ok) {
          const result = await response.json();
          document.getElementById("statusResult").textContent =
            `📌 Status: ${result.status || "Pending"}`;
        } else {
          document.getElementById("statusResult").textContent =
            "❌ Application not found.";
        }
      } catch (error) {
        console.error("Error checking status:", error);
        document.getElementById("statusResult").textContent =
          "⚠️ Network error. Try again later.";
      }
    });
  }
});

// === Password Toggle ===
function togglePassword(id) {
  const field = document.getElementById(id);
  const icon = field.nextElementSibling;

  if (field.type === "password") {
    field.type = "text";
    icon.textContent = "🙈"; // hide icon
  } else {
    field.type = "password";
    icon.textContent = "👁️"; // show icon
  }

}

// === Password Strength Checker ===
function checkStrength() {
  const password = document.getElementById("password1").value;
  const strength = document.getElementById("password-strength");

  let score = 0;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;

  if (password.length === 0) {
    strength.textContent = "";
  } else if (score <= 2) {
    strength.textContent = "Weak password ❌";
    strength.style.color = "red";
  } else if (score === 3) {
    strength.textContent = "Medium password ⚠️";
    strength.style.color = "orange";
  } else {
    strength.textContent = "Strong password ✅";
    strength.style.color = "green";
  }
}


document.addEventListener("DOMContentLoaded", function () {
  // Initialize map centered in Kenya
  const map = L.map("map").setView([0.0236, 37.9062], 6);

  // Add OpenStreetMap tiles
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  // Add farmer markers
  if (Array.isArray(farmers) && farmers.length > 0) {
    farmers.forEach((farmer) => {
      if (farmer.latitude && farmer.longitude) {
        L.marker([farmer.latitude, farmer.longitude])
          .addTo(map)
          .bindPopup(
            `<b>${farmer.full_name}</b><br>County: ${farmer.county}`
          );
      }
    });
  } else {
    console.log("No farmer data available.");
  }
});

