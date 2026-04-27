document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("toggleSidebarBtn");
  const layout = document.querySelector(".sidebar-layout");
  const STORAGE_KEY = "eduplanner_sidebar_collapsed";

  function applyState(collapsed) {
    if (!layout) return;
    if (collapsed) layout.classList.add("sidebar-collapsed");
    else layout.classList.remove("sidebar-collapsed");
  }

  // restore state
  try {
    const saved = localStorage.getItem(STORAGE_KEY) === "1";
    applyState(saved);
  } catch (e) {
    // ignore
  }

  if (!btn || !layout) return;

  btn.addEventListener("click", function () {
    const collapsed = layout.classList.toggle("sidebar-collapsed");
    try {
      localStorage.setItem(STORAGE_KEY, collapsed ? "1" : "0");
    } catch (e) {}
  });
});
