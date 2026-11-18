/* HeOCR theme toggle. Light is the default whatever the OS setting; night mode
   is entered only through the toggle and is remembered per browser.
   The pages also run a one-line inline version of the "read" half in <head>,
   so a returning night-mode visitor never sees a light flash. */
(function () {
  var KEY = "heocr-theme";
  var root = document.documentElement;

  function apply(dark) {
    if (dark) root.dataset.theme = "dark";
    else delete root.dataset.theme;
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      button.setAttribute("aria-pressed", String(dark));
    });
  }

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* private mode: stay light */ }
  apply(saved === "dark");

  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-theme-toggle]");
    if (!button) return;
    var dark = root.dataset.theme !== "dark";
    apply(dark);
    try { localStorage.setItem(KEY, dark ? "dark" : "light"); } catch (e) { /* not remembered */ }
  });
})();
