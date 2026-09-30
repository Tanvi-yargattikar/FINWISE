let income = 75000;

const savingsPercentage = 0.2666;
const investmentPercentage = 0.2;

function updateIncome() {
  const input = document.getElementById("incomeInput").value;
  const parsed = parseFloat(input);
  if (!isNaN(parsed) && parsed > 0) {
    income = parsed;
    updateDashboard();
  }
}

function updateDashboard() {
  const savings = income * savingsPercentage;
  const investments = income * investmentPercentage;

  document.getElementById("incomeAmount").textContent = `₹${income.toLocaleString()}`;
  document.getElementById("savingsAmount").textContent = `₹${savings.toLocaleString()}`;
  document.getElementById("investmentsAmount").textContent = `₹${investments.toLocaleString()}`;

  renderChart(income, savings, investments);
}

let chart;

function renderChart(income, savings, investments) {
  const ctx = document.getElementById("incomeChart").getContext("2d");
  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: ["Income", "Savings", "Investments"],
      datasets: [
        {
          data: [income, savings, investments],
          backgroundColor: ["#8884d8", "#82ca9d", "#ffc658"],
        },
      ],
    },
  });
}

// Initialize dashboard on load
window.onload = () => {
  updateDashboard();
};