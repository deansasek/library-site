// Library site: copy buttons on code blocks, and docs search. Same-origin only. Works without this file.
(function () {
  "use strict";

  var script = document.querySelector('script[src$="script.js"]');
  var base = script ? script.src : location.href;

  // Visually hidden live region for copy and search results.
  var live = document.createElement("p");
  live.className = "visually-hidden";
  live.setAttribute("aria-live", "polite");
  document.body.appendChild(live);

  function announce(message) {
    live.textContent = "";
    setTimeout(function () { live.textContent = message; }, 50);
  }

  // Copy with the Clipboard API; fall back to a hidden textarea and execCommand.
  function copyWithTextarea(text) {
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.top = "-1000px";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(area);
    return ok;
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(function () { return true; }, function () {
        return copyWithTextarea(text);
      });
    }
    return Promise.resolve(copyWithTextarea(text));
  }

  document.querySelectorAll(".code-block pre").forEach(function (pre) {
    var box = pre.parentNode;
    var button = document.createElement("button");
    button.type = "button";
    button.className = "copy-button";
    button.textContent = "Copy";
    box.classList.add("has-copy");
    box.appendChild(button);
    button.addEventListener("click", function () {
      copyText(pre.textContent).then(function (ok) {
        button.textContent = ok ? "Copied" : "Copy failed";
        announce(ok ? "Copied to the clipboard." : "Copy failed. Select the command and copy it.");
        clearTimeout(button.resetTimer);
        button.resetTimer = setTimeout(function () { button.textContent = "Copy"; }, 2000);
      });
    });
  });
})();
