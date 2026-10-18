(function () {
"use strict";
var script = document.querySelector('script[src$="script.js"]');
var base = script ? script.src : location.href;
var live = document.createElement("p");
live.className = "visually-hidden";
live.setAttribute("aria-live", "polite");
document.body.appendChild(live);
function announce(message) {
live.textContent = "";
setTimeout(function () { live.textContent = message; }, 50);
}
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
var COPY_ICON = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
'<rect x="8.5" y="8.5" width="11" height="11" rx="2"/><path d="M5.5 15.5h-1a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v1"/></svg>';
document.querySelectorAll(".code-block pre").forEach(function (pre) {
var box = pre.parentNode;
var bar = box.querySelector(".code-head");
if (!bar) {
bar = document.createElement("div");
bar.className = "code-head";
box.insertBefore(bar, pre);
}
var button = document.createElement("button");
button.type = "button";
button.className = "copy-button";
var icon=document.createElementNS("http://www.w3.org/2000/svg","svg");icon.setAttribute("class","icon");icon.setAttribute("viewBox","0 0 24 24");icon.setAttribute("aria-hidden","true");icon.setAttribute("focusable","false");var rect=document.createElementNS("http://www.w3.org/2000/svg","rect");rect.setAttribute("x","8.5");rect.setAttribute("y","8.5");rect.setAttribute("width","11");rect.setAttribute("height","11");rect.setAttribute("rx","2");var path=document.createElementNS("http://www.w3.org/2000/svg","path");path.setAttribute("d","M5.5 15.5h-1a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v1");icon.appendChild(rect);icon.appendChild(path);button.appendChild(icon);var labelText=document.createElement("span");labelText.textContent="Copy";button.appendChild(labelText);
bar.appendChild(button);
var label = button.querySelector("span");
button.addEventListener("click", function () {
copyText(pre.textContent).then(function (ok) {
label.textContent = ok ? "Copied" : "Copy failed";
announce(ok ? "Copied to the clipboard." : "Copy failed. Select the command and copy it.");
clearTimeout(button.resetTimer);
button.resetTimer = setTimeout(function () { label.textContent = "Copy"; }, 2000);
});
});
});
var box = document.querySelector(".search");
if (box) {
var input = box.querySelector("input");
var panel = box.querySelector(".results");
var items = [];
var leaveTimer = null;
function leave() {
if (panel.hidden) { return; }
clearTimeout(leaveTimer);
var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (reduce) { panel.hidden = true; return; }
panel.classList.add("is-leaving");
leaveTimer = setTimeout(function () {
panel.hidden = true;
panel.classList.remove("is-leaving");
}, 150);
}
fetch(new URL("search-index.json", base).href)
.then(function (r) { return r.ok ? r.json() : []; })
.then(function (data) {
items = data;
if (items.length) { box.hidden = false; window.dispatchEvent(new Event("resize")); }
})
.catch(function () { items = []; });
function links() { return Array.prototype.slice.call(panel.querySelectorAll("a")); }
function render() {
var q = input.value.trim().toLowerCase();
if (!q) { leave(); return; }
var words = q.split(/\s+/);
panel.textContent = "";
var hits = items.filter(function (it) {
var text = (it.t + " " + it.p + " " + it.s).toLowerCase();
return words.every(function (w) { return text.indexOf(w) !== -1; });
}).slice(0, 12);
var order = [];
var groups = {};
hits.forEach(function (it) {
if (!groups[it.p]) { groups[it.p] = []; order.push(it.p); }
groups[it.p].push(it);
});
order.forEach(function (page) {
var head = document.createElement("p");
head.className = "results-page";
head.textContent = page;
panel.appendChild(head);
var ul = document.createElement("ul");
groups[page].forEach(function (it) {
var li = document.createElement("li");
var a = document.createElement("a");
a.href = new URL(it.u, base).href;
a.textContent = it.t;
li.appendChild(a);
ul.appendChild(li);
});
panel.appendChild(ul);
});
if (!hits.length) {
var none = document.createElement("p");
none.className = "results-page";
none.textContent = "No results";
panel.appendChild(none);
}
clearTimeout(leaveTimer);
panel.classList.remove("is-leaving");
panel.hidden = false;
announce(hits.length ? hits.length + (hits.length === 1 ? " result" : " results") : "No results");
}
input.addEventListener("input", render);
input.addEventListener("keydown", function (e) {
var all = links();
if (e.key === "ArrowDown" && all.length) {
e.preventDefault();
all[0].focus();
} else if (e.key === "Enter" && all.length) {
e.preventDefault();
window.location.href = all[0].href;
} else if (e.key === "Escape") {
input.value = "";
render();
}
});
panel.addEventListener("keydown", function (e) {
var all = links();
var i = all.indexOf(document.activeElement);
if (e.key === "ArrowDown") {
e.preventDefault();
if (all[i + 1]) { all[i + 1].focus(); }
} else if (e.key === "ArrowUp") {
e.preventDefault();
if (i > 0) { all[i - 1].focus(); } else { input.focus(); }
} else if (e.key === "Escape") {
e.preventDefault();
input.value = "";
render();
input.focus();
}
});
}
// Landing page demos. The videos autoplay from their markup, so they still play without JavaScript.
// When the reader asks for less motion, pause them so they hold their poster frame instead.
var demos = Array.prototype.slice.call(document.querySelectorAll("video.demo-video"));
if (demos.length && window.matchMedia) {
var motion = window.matchMedia("(prefers-reduced-motion: reduce)");
function syncDemos() {
demos.forEach(function (video) {
if (motion.matches) {
video.removeAttribute("autoplay");
video.pause();
} else {
video.setAttribute("autoplay", "");
var started = video.play();
if (started && started.catch) { started.catch(function () {}); }
}
});
}
syncDemos();
if (motion.addEventListener) { motion.addEventListener("change", syncDemos); }
else if (motion.addListener) { motion.addListener(syncDemos); }
}
var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.toc a[href^="#"]'));
var tocTargets = tocLinks.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
if (tocLinks.length) {
var toc = tocLinks[0].closest(".toc");
var list = tocLinks[0].closest("ol");
function textBox(a) {
var node = a.firstChild;
while (node && !(node.nodeType === 3 && node.textContent.trim())) { node = node.nextSibling; }
if (!node) { return a.getBoundingClientRect(); }
var range = document.createRange();
range.selectNodeContents(node);
return range.getBoundingClientRect();
}
var indicator = document.createElement("span");
indicator.className = "toc-indicator";
indicator.setAttribute("aria-hidden", "true");
toc.appendChild(indicator);
var lastId = null;
// Groups and features the reader closed on purpose, so scrolling does not spring them open again.
var closedFolders = [];
Array.prototype.slice.call(toc.querySelectorAll("details")).forEach(function (folder) {
folder.addEventListener("toggle", function () {
var i = closedFolders.indexOf(folder);
if (folder.open) {
if (i !== -1) { closedFolders.splice(i, 1); }
} else if (i === -1) {
closedFolders.push(folder);
}
});
});
function openFolder(folder) {
if (closedFolders.indexOf(folder) !== -1) { return; }
folder.open = true;
}
function markCurrent() {
// Find the new current section from rect reads only.
var current = null;
tocTargets.forEach(function (t) {
if (t && t.getBoundingClientRect().top <= 120) { current = t.id; }
});
// At the bottom of the page the last section cannot scroll up under the top edge, so the last one is current.
var scrollable = document.documentElement.scrollHeight > window.innerHeight + 4;
var atBottom = scrollable && window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4;
var lastTarget = tocTargets[tocTargets.length - 1];
if (atBottom && lastTarget) { current = lastTarget.id; }
if (!current && tocTargets[0]) { current = tocTargets[0].id; }
// A section chosen from the navigation stays current while the page scrolls to it, until the reader scrolls by hand.
if (pinnedId) { current = pinnedId; }
var active = null;
tocLinks.forEach(function (a) {
if (current !== null && a.getAttribute("href") === "#" + current) { active = a; }
});
if (active) {
// Open the groups and features around the current section, so its entry is visible in the
// navigation, but only when the active section changes and never against the reader's choice.
// This moves the entry, so it happens before the indicator is measured.
if (current !== lastId) {
var folder = active.closest("details");
while (folder) {
openFolder(folder);
folder = folder.parentElement ? folder.parentElement.closest("details") : null;
}
}
}
// Read every rect before writing any class or style, so the whole update needs one layout pass.
var box = active ? textBox(active) : null;
var origin = active ? toc.getBoundingClientRect() : null;
var listLeft = list.offsetLeft;
tocLinks.forEach(function (a) {
var on = current !== null && a.getAttribute("href") === "#" + current;
a.classList.toggle("is-active", on);
if (on) { a.setAttribute("aria-current", "location"); } else { a.removeAttribute("aria-current"); }
});
if (active) {
indicator.style.height = box.height + "px";
indicator.style.transform = "translate(" + listLeft + "px," + (box.top - origin.top) + "px)";
}
lastId = current;
}
var pinnedId = null;
tocLinks.forEach(function (a) {
a.addEventListener("click", function () {
pinnedId = a.getAttribute("href").slice(1);
// Following a link shows where it goes, even inside a group the reader closed.
var folder = a.closest("details");
while (folder) {
folder.open = true;
folder = folder.parentElement ? folder.parentElement.closest("details") : null;
}
markCurrent();
});
});
["wheel", "touchstart", "keydown"].forEach(function (name) {
window.addEventListener(name, function () { pinnedId = null; }, { passive: true });
});
window.addEventListener("resize", markCurrent);
window.addEventListener("load", markCurrent);
if (document.fonts && document.fonts.ready) { document.fonts.ready.then(markCurrent); }
if (window.ResizeObserver) { new ResizeObserver(markCurrent).observe(toc); }
// A wheel or trackpad can fire many scroll events per frame; coalesce them into one update per animation frame.
var scrollQueued = false;
function onScroll() {
if (scrollQueued) { return; }
scrollQueued = true;
requestAnimationFrame(function () {
scrollQueued = false;
markCurrent();
});
}
window.addEventListener("scroll", onScroll, { passive: true });
markCurrent();
}
})();

// Offline reading: register the service worker that sw.js describes, at the site root, from any page served over HTTP(S).
if ("serviceWorker" in navigator && /^https?:/.test(location.protocol)) {
var scriptTag = document.querySelector('script[src$="script.js"]');
navigator.serviceWorker.register(new URL("../sw.js", scriptTag ? scriptTag.src : location.href).href).catch(function () {});
}
