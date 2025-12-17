const API_BASE = "http://127.0.0.1:8000";

const presets = {
  balanced: {
    winter_driving: 0.2,
    fuel_efficiency: 0.2,
    price_fit: 0.2,
    ownership_cost: 0.2,
    acceleration: 0.1,
    reliability: 0.1,
  },
  budget: {
    winter_driving: 0.15,
    fuel_efficiency: 0.3,
    price_fit: 0.3,
    ownership_cost: 0.2,
    acceleration: 0.05,
    reliability: 0.0,
  },
  winter: {
    winter_driving: 0.35,
    fuel_efficiency: 0.2,
    price_fit: 0.2,
    ownership_cost: 0.1,
    acceleration: 0.05,
    reliability: 0.1,
  },
  performance: {
    winter_driving: 0.1,
    fuel_efficiency: 0.1,
    price_fit: 0.15,
    ownership_cost: 0.1,
    acceleration: 0.35,
    reliability: 0.2,
  },
};

const form = document.getElementById("recommend-form");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusEl.textContent = "Loading...";
  resultsEl.innerHTML = "";

  const formData = new FormData(form);
  const presetKey = document.getElementById("preset").value || "balanced";
  const weights = presets[presetKey] || presets.balanced;

  const payload = {
    budget: Number(formData.get("budget")),
    location: formData.get("location"),
    annual_km: Number(formData.get("annual_km")),
    passengers: Number(formData.get("passengers")),
    fuel_type: formData.get("fuel_type") || null,
    priorities: ["fuel", "winter", "price"],
    weights,
  };

  try {
    const res = await fetch(`${API_BASE}/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`);
    }
    const data = await res.json();
    renderResults(data);
  } catch (err) {
    statusEl.textContent = err.message || "Request failed";
  }
});

function renderResults(data) {
  const { results = [], using_mock_data, catalog_last_updated } = data;
  statusEl.textContent = using_mock_data
    ? "Using mock/seed data"
    : `Catalog updated: ${catalog_last_updated || "unknown"}`;

  if (!results.length) {
    resultsEl.textContent = "No results.";
    return;
  }

  resultsEl.innerHTML = results
    .map((car) => {
      return `
        <div class="card">
          <div class="row">
            <div><strong>${car.make} ${car.model} ${car.year}</strong></div>
            <div class="label">Score: ${car.total_score}</div>
          </div>
          <div class="row">
            <span class="label">Price: $${car.price}</span>
            <span class="label">Fuel: ${car.fuel_type || "n/a"}</span>
            <span class="label">0-60: ${car.zero_to_sixty || "n/a"}s</span>
          </div>
          <div class="metrics">
            <span>Winter: ${car.winter_points}</span>
            <span>Fuel: ${car.fuel_points}</span>
            <span>Price fit: ${car.price_points}</span>
            <span>Ownership: ${car.ownership_cost_points}</span>
            <span>Accel: ${car.acceleration_points}</span>
            <span>Reliability: ${car.reliability_points}</span>
          </div>
        </div>
      `;
    })
    .join("");
}
