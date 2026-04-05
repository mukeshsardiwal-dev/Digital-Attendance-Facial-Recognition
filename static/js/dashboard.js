// dashboard.js
document.addEventListener("DOMContentLoaded", () => {
  const trainBtn = document.getElementById("trainBtn");
  const cleanupBtn = document.getElementById("cleanupBtn");
  const trainProgress = document.getElementById("trainProgress");
  const trainMsg = document.getElementById("trainMsg");

  async function pollStatus() {
    try {
      const res = await fetch("/train_status");
      const data = await res.json();
      trainProgress.style.width = data.progress + "%";
      trainProgress.innerText = data.progress + "%";
      trainMsg.innerText = data.message || "";
      return data;
    } catch (e) {
      console.error(e);
      return null;
    }
  }

  // Cleanup button handler
  cleanupBtn.addEventListener("click", async () => {
    if (!confirm("Remove all empty student records (those without photos)?")) {
      return;
    }
    cleanupBtn.disabled = true;
    try {
      const res = await fetch("/cleanup_empty_students", { method: "POST" });
      const data = await res.json();
      alert(data.message);
      location.reload();
    } catch (e) {
      alert("Cleanup failed: " + e.message);
    } finally {
      cleanupBtn.disabled = false;
    }
  });

  trainBtn.addEventListener("click", async () => {
    trainBtn.disabled = true;
    const start = await fetch("/train_model");
    const startData = await start.json();

    if (!start.ok && start.status !== 202) {
      alert(
        `Failed to start training: ${startData.message || "Unknown error"}`,
      );
      trainBtn.disabled = false;
      return;
    }

    trainMsg.innerText = startData.message || "Training started...";
    // poll until progress==100 or not running
    const t = setInterval(async () => {
      const s = await pollStatus();
      if (s && s.progress >= 100) {
        clearInterval(t);
        trainBtn.disabled = false;
        alert("Training completed successfully!");
      }
    }, 1500);
  });

  // Chart initial render & update every 10s
  let chart = null;
  async function updateChart() {
    const res = await fetch("/attendance_stats");
    const data = await res.json();
    const ctx = document.getElementById("attendanceChart").getContext("2d");
    if (!chart) {
      chart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: data.dates,
          datasets: [
            {
              label: "Attendance",
              data: data.counts,
              backgroundColor: "rgba(59,130,246,0.7)",
            },
          ],
        },
        options: { responsive: true, maintainAspectRatio: false },
      });
    } else {
      chart.data.labels = data.dates;
      chart.data.datasets[0].data = data.counts;
      chart.update();
    }
  }
  updateChart();
  setInterval(updateChart, 10000);
});
