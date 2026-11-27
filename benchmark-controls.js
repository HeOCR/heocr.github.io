/* The HTML carries every view. Enhance the native disclosures into controls
   and keep just the selected score table in each panel. */
for (const panel of document.querySelectorAll("[data-score-panel]")) {
  const prefix = panel.dataset.scorePanel;
  const controls = panel.querySelector("[data-score-controls]");
  const active = panel.querySelector("[data-score-active]");
  const fallback = panel.querySelector(":scope > details");
  const status = panel.querySelector("[data-score-status]");
  const notes = panel.querySelectorAll("[data-score-note]");
  const captureNotes = panel.querySelectorAll("[data-score-capture-note]");
  const tables = new Map([...panel.querySelectorAll(".benchmark-table")].map(table => [table.id, table]));

  function render() {
    const view = controls.querySelector("[data-score-view]:checked").value;
    const capture = controls.querySelector("[data-score-capture]:checked")?.value || "pooled";
    const table = tables.get(`${prefix}-${view}-${capture}`);
    if (!table) return;
    if (active.firstElementChild !== table) active.replaceChildren(table);
    for (const note of notes) note.hidden = note.dataset.scoreNote !== view;
    for (const note of captureNotes) note.hidden = note.dataset.scoreCaptureNote !== capture;
    status.textContent = table.querySelector("caption").textContent;
  }

  function followLink() {
    const fragment = window.location.hash.slice(1)
      .replace(/^(p-mod-open-(?:all|filtered)-phone)-[ab]$/, "$1");
    const table = tables.get(fragment) || tables.get(`${fragment}-pooled`);
    if (!table) return;
    const suffix = table.id.slice(prefix.length + 1);
    const separator = suffix.indexOf("-");
    const view = suffix.slice(0, separator);
    const capture = suffix.slice(separator + 1);
    for (const radio of controls.querySelectorAll("[data-score-view]")) radio.checked = radio.value === view;
    for (const radio of controls.querySelectorAll("[data-score-capture]")) radio.checked = radio.value === capture;
    render();
    table.scrollIntoView();
  }

  render();
  controls.addEventListener("change", render);
  window.addEventListener("hashchange", followLink);
  fallback.remove();
  controls.hidden = false;
  followLink();
}
