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
