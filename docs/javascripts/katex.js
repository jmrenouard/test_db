/* Render Arithmatex / LaTeX expressions with KaTeX across Material instant navigation. */
function renderTestDbMath() {
  if (typeof renderMathInElement !== "function") {
    return;
  }
  renderMathInElement(document.body, {
    delimiters: [
      { left: "$$", right: "$$", display: true },
      { left: "$", right: "$", display: false },
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true }
    ],
    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
    throwOnError: false
  });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(() => {
    if (typeof renderMathInElement === "function") {
      renderTestDbMath();
    } else {
      window.addEventListener("DOMContentLoaded", renderTestDbMath, { once: true });
    }
  });
} else {
  window.addEventListener("DOMContentLoaded", renderTestDbMath, { once: true });
}
