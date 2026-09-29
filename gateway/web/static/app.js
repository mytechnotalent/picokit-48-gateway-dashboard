"use strict";

const tenths = (value) => (value === null || value === undefined)
  ? null
  : (value / 10.0).toFixed(1);

const label = (row) => new Date(row.utc).toLocaleTimeString();

async function getJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("request failed: " + path);
  }
  return response.json();
}

function renderNodeRows(rows) {
  const body = document.querySelector("#nodes tbody");
  body.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    [row.node, tenths(row.temp_tenths), tenths(row.hum_tenths), row.rssi]
      .forEach((cell) => {
        const td = document.createElement("td");
        td.textContent = cell === null ? "-" : cell;
        tr.appendChild(td);
      });
    body.appendChild(tr);
  });
}

function renderEventRows(rows) {
  const body = document.querySelector("#events tbody");
  body.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    [String(row.utc).slice(0, 19), row.node, row.kind, row.detail]
      .forEach((cell) => {
        const td = document.createElement("td");
        td.textContent = cell === null ? "-" : cell;
        tr.appendChild(td);
      });
    body.appendChild(tr);
  });
}

function renderSummaryRows(rows) {
  const body = document.querySelector("#summary tbody");
  body.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    [row.node, row.count, tenths(row.temp_min), tenths(row.temp_max)]
      .forEach((cell) => {
        const td = document.createElement("td");
        td.textContent = cell === null || cell === undefined ? "-" : cell;
        tr.appendChild(td);
      });
    body.appendChild(tr);
  });
}

function buildSignalChart(rows) {
  const context = document.getElementById("rssi");
  return new Chart(context, {
    type: "line",
    data: {
      labels: rows.map((row) => label(row)),
      datasets: [
        { label: "RSSI dBm", data: rows.map((row) => row.rssi),
          borderColor: "#b18cff", backgroundColor: "rgba(177,140,255,0.15)",
          tension: 0.3 }
      ]
    },
    options: {
      responsive: true,
      animation: false,
      scales: { y: { grid: { color: "#123" }, ticks: { color: "#6f8f7c" } },
                x: { grid: { color: "#123" }, ticks: { color: "#6f8f7c" } } },
      plugins: { legend: { labels: { color: "#f2f5ff" } } }
    }
  });
}

function buildChart(rows) {
  const context = document.getElementById("climate");
  const temps = rows.map((row) => tenths(row.temp_tenths));
  const hums = rows.map((row) => tenths(row.hum_tenths));
  const labels = rows.map((row) => label(row));
  return new Chart(context, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        { label: "Temp C", data: temps, borderColor: "#39ff88",
          backgroundColor: "rgba(57,255,136,0.15)", tension: 0.3 },
        { label: "Humidity %", data: hums, borderColor: "#7fd8e0",
          backgroundColor: "rgba(127,216,224,0.15)", tension: 0.3 }
      ]
    },
    options: {
      responsive: true,
      animation: false,
      scales: { y: { grid: { color: "#123" }, ticks: { color: "#6f8f7c" } },
                x: { grid: { color: "#123" }, ticks: { color: "#6f8f7c" } } },
      plugins: { legend: { labels: { color: "#f2f5ff" } } }
    }
  });
}

async function refresh(chart, signal) {
  const frames = await getJson("/api/telemetry");
  const events = await getJson("/api/events");
  const summary = await getJson("/api/summary");
  renderNodeRows(frames.slice(-12).reverse());
  renderEventRows(events);
  renderSummaryRows(summary);
  chart.data.labels = frames.map((row) => label(row));
  chart.data.datasets[0].data = frames.map((row) => tenths(row.temp_tenths));
  chart.data.datasets[1].data = frames.map((row) => tenths(row.hum_tenths));
  chart.update();
  signal.data.labels = frames.map((row) => label(row));
  signal.data.datasets[0].data = frames.map((row) => row.rssi);
  signal.update();
}

async function boot() {
  const frames = await getJson("/api/telemetry");
  const chart = buildChart(frames);
  const signal = buildSignalChart(frames);
  await refresh(chart, signal);
  window.setInterval(() => refresh(chart, signal), 5000);
}

boot().catch((error) => console.error(error));
