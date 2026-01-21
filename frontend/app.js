const API_BASE = "http://127.0.0.1:8000";

const presets = {
  balanced: {
    winter_driving: 0.15,
    fuel_efficiency: 0.15,
    price_fit: 0.20,
    ownership_cost: 0.15,
    acceleration: 0.10,
    reliability: 0.15,
    safety: 0.10,
  },
  budget: {
    winter_driving: 0.10,
    fuel_efficiency: 0.25,
    price_fit: 0.35,
    ownership_cost: 0.20,
    acceleration: 0.05,
    reliability: 0.05,
    safety: 0.00,
  },
  winter: {
    winter_driving: 0.35,
    fuel_efficiency: 0.15,
    price_fit: 0.15,
    ownership_cost: 0.10,
    acceleration: 0.05,
    reliability: 0.10,
    safety: 0.10,
  },
  performance: {
    winter_driving: 0.10,
    fuel_efficiency: 0.10,
    price_fit: 0.10,
    ownership_cost: 0.10,
    acceleration: 0.35,
    reliability: 0.15,
    safety: 0.10,
  },
};

const form = document.getElementById("recommend-form");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

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
      const safetyInfo =
        car.complaints_count !== undefined && car.recalls_count !== undefined
          ? `<span class="label">Safety: ${car.complaints_count} complaints, ${car.recalls_count} recalls</span>`
          : "";
      const priceLabel = car.price ? currency.format(car.price) : "n/a";
      
      return `
        <div class="card">
          <div class="row">
            <div><strong>${car.make} ${car.model} ${car.year}</strong></div>
            <div class="label">Score: ${car.total_score}</div>
          </div>
          <div class="row">
            <span class="label">Price: ${priceLabel}</span>
            <span class="label">Fuel: ${car.fuel_type || "n/a"}</span>
            <span class="label">0-60: ${car.zero_to_sixty || "n/a"}s</span>
          </div>
          ${safetyInfo ? `<div class="row">${safetyInfo}</div>` : ""}
          <div class="metrics">
            <span>Winter: ${car.winter_points}</span>
            <span>Fuel: ${car.fuel_points}</span>
            <span>Price fit: ${car.price_points}</span>
            <span>Ownership: ${car.ownership_cost_points}</span>
            <span>Accel: ${car.acceleration_points}</span>
            <span>Reliability: ${car.reliability_points}</span>
            <span>Safety: ${car.safety_points || 0}</span>
          </div>
        </div>
      `;
    })
    .join("");
}
