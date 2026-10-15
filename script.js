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
var list = box.querySelector(".results");
var items = [];
fetch(new URL("search-index.json", base).href)
.then(function (r) { return r.ok ? r.json() : []; })
.then(function (data) {
items = data;
if (items.length) { box.hidden = false; }
})
.catch(function () { items = []; });
function render() {
var q = input.value.trim().toLowerCase();
list.textContent = "";
if (!q) { list.hidden = true; return; }
var hits = items.filter(function (it) {
return (it.t + " " + it.p + " " + it.s).toLowerCase().indexOf(q) !== -1;
}).slice(0, 8);
hits.forEach(function (it) {
var li = document.createElement("li");
var a = document.createElement("a");
a.href = new URL(it.u, base).href;
a.textContent = it.t;
var span = document.createElement("span");
span.textContent = " \u00b7 " + it.p;
li.appendChild(a);
li.appendChild(span);
list.appendChild(li);
});
list.hidden = false;
announce(hits.length ? hits.length + (hits.length === 1 ? " result" : " results") : "No results");
}
input.addEventListener("input", render);
input.addEventListener("keydown", function (e) {
if (e.key === "ArrowDown") {
var first = list.querySelector("a");
if (first) { e.preventDefault(); first.focus(); }
} else if (e.key === "Escape") {
input.value = "";
render();
}
});
list.addEventListener("keydown", function (e) {
var links = Array.prototype.slice.call(list.querySelectorAll("a"));
var i = links.indexOf(document.activeElement);
if (e.key === "ArrowDown") {
e.preventDefault();
if (links[i + 1]) { links[i + 1].focus(); }
} else if (e.key === "ArrowUp") {
e.preventDefault();
if (i > 0) { links[i - 1].focus(); } else { input.focus(); }
} else if (e.key === "Escape") {
e.preventDefault();
input.value = "";
render();
input.focus();
}
});
}
})();
