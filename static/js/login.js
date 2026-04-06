let currentStep = 1;
let userId = null;
let sessionData = {};

// Setup OTP input auto-focus
document.addEventListener("DOMContentLoaded", () => {
  const otpInputs = document.querySelectorAll(".otp-input");
  otpInputs.forEach((input, index) => {
    input.addEventListener("keyup", (e) => {
      if (e.key === "Backspace") {
        input.value = "";
        if (index > 0) otpInputs[index - 1].focus();
      } else if (input.value.length === 1) {
        if (index < otpInputs.length - 1) {
          otpInputs[index + 1].focus();
        }
      }
    });

    input.addEventListener("input", (e) => {
      if (!/^\d$/.test(e.target.value)) {
        e.target.value = "";
      }
    });
  });

  // Setup facial video
  setupFacialCamera();
});

// Setup facial camera
async function setupFacialCamera() {
  try {
    const video = document.getElementById("facialVideo");
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: "user",
      },
    });
    video.srcObject = stream;
  } catch (err) {
    console.error("Camera error:", err);
  }
}

// Step 1: Handle Username & Password
async function handleStep1(event) {
  event.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const alertDiv = document.getElementById("alertSection1");

  try {
    const response = await fetch("/api/auth/step1", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      showAlert(alertDiv, data.message || "Login failed", "danger");
      return;
    }

    userId = data.user_id;
    showAlert(
      alertDiv,
      "Credentials verified! Check your email for OTP.",
      "success",
    );

    setTimeout(() => {
      goToStep(2);
    }, 1000);
  } catch (error) {
    showAlert(alertDiv, "Error: " + error.message, "danger");
  }
}

// Step 2: Handle OTP Verification
async function handleStep2(event) {
  event.preventDefault();
  const otpInputs = document.querySelectorAll(".otp-input");
  const otpCode = Array.from(otpInputs)
    .map((input) => input.value)
    .join("");
  const alertDiv = document.getElementById("alertSection2");

  if (otpCode.length !== 6) {
    showAlert(alertDiv, "Please enter a valid 6-digit OTP", "danger");
    return;
  }

  try {
    const response = await fetch("/api/auth/step2", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, otp_code: otpCode }),
    });

    const data = await response.json();

    if (!response.ok) {
      showAlert(alertDiv, data.message || "Invalid OTP", "danger");
      return;
    }

    showAlert(
      alertDiv,
      "OTP verified! Now verify with facial recognition.",
      "success",
    );

    setTimeout(() => {
      goToStep(3);
    }, 1000);
  } catch (error) {
    showAlert(alertDiv, "Error: " + error.message, "danger");
  }
}

// Step 3: Capture Facial Image
async function captureFacialImage() {
  const video = document.getElementById("facialVideo");
  const canvas = document.getElementById("facialCanvas");
  const ctx = canvas.getContext("2d");
  const alertDiv = document.getElementById("alertSection3");

  if (!userId) {
    showAlert(
      alertDiv,
      "Error: User ID not set. Please start from Step 1.",
      "danger",
    );
    return;
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);

  canvas.toBlob(
    async (blob) => {
      try {
        if (!blob) {
          showAlert(alertDiv, "Error: Failed to capture image", "danger");
          return;
        }

        console.log("[STEP3] Preparing FormData with user_id:", userId);
        const formData = new FormData();
        formData.append("user_id", String(userId));
        formData.append("image", blob, "facial.jpg");

        console.log("[STEP3] Sending facial image to server...");
        const response = await fetch("/api/auth/step3", {
          method: "POST",
          body: formData,
        });

        console.log("[STEP3] Response status:", response.status);
        const data = await response.json();
        console.log("[STEP3] Response data:", data);

        if (!response.ok) {
          showAlert(
            alertDiv,
            data.message || "Facial recognition failed",
            "danger",
          );
          console.error("[STEP3] Server returned error:", data.message);
          return;
        }

        console.log(
          "[STEP3] Login successful! Token:",
          data.token ? "Received" : "Missing",
        );
        showAlert(
          alertDiv,
          "Facial recognition successful! Logging in...",
          "success",
        );

        setTimeout(() => {
          // Redirect to dashboard
          console.log(
            "[STEP3] Storing token in localStorage and redirecting...",
          );
          sessionData.token = data.token;
          sessionData.user = data.user;
          localStorage.setItem("token", data.token);
          localStorage.setItem("user_id", data.user_id);
          localStorage.setItem("username", data.user.username);
          console.log("[STEP3] Token stored in localStorage");
          console.log("[STEP3] Redirecting to dashboard...");
          window.location.href =
            "/dashboard?token=" + encodeURIComponent(data.token);
        }, 1000);
      } catch (error) {
        console.error("[STEP3] Exception:", error);
        showAlert(alertDiv, "Error: " + error.message, "danger");
      }
    },
    "image/jpeg",
    0.9,
  );
}

// Handle Step 3 Form Submit
async function handleStep3(event) {
  event.preventDefault();
  captureFacialImage();
}

// Navigation functions
function goToStep(step) {
  // Hide current section
  document.getElementById(`section${currentStep}`).classList.remove("active");
  document.getElementById(`step${currentStep}`).classList.remove("active");

  // Show new section
  document.getElementById(`section${step}`).classList.add("active");
  document.getElementById(`step${step}`).classList.add("active");

  // Mark previous steps as completed
  for (let i = 1; i < step; i++) {
    document.getElementById(`step${i}`).classList.add("completed");
  }

  currentStep = step;
}

function goBack(fromStep) {
  goToStep(fromStep - 1);
  // Clear form inputs
  if (fromStep === 2) {
    document.getElementById("form1").reset();
  } else if (fromStep === 3) {
    document
      .querySelectorAll(".otp-input")
      .forEach((input) => (input.value = ""));
  }
}

// Utility function to show alerts
function showAlert(element, message, type) {
  element.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

// OTP Auto-submit when all digits are entered
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".otp-input").forEach((input) => {
    input.addEventListener("input", () => {
      const allFilled = Array.from(
        document.querySelectorAll(".otp-input"),
      ).every((i) => i.value);
      if (allFilled) {
        // Auto-submit after slight delay for better UX
        // Uncomment if desired: setTimeout(() => handleStep2(new Event('submit')), 300);
      }
    });
  });
});
