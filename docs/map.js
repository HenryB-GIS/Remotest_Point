"use strict";

const byId = id => document.getElementById(id);
const svg = byId("map");
const ns = "http://www.w3.org/2000/svg";
const rules = {
  A: "Count tracks with pickup-passable smoothness or, where smoothness is unknown, grades 1–3.",
  B: "Also count tracks whose smoothness and grade are both unknown.",
  C: "Also count grades 4–5 where smoothness is unknown. This includes the ground track east of the default pin."
};
const addresses = {
  "47.674647,14.011258": "stirrup.employed.deserters",
  "47.675188,14.006859": "dangerous.leafy.polkas"
};
let rule = "B";
let centre = [0, 0];
let zoom = 0;
let unitsPerPixel = 1;
let drag = null;
const context = {};
const tiles = new Map();

function attrs(el, values) {
  for (const [key, value] of Object.entries(values)) el.setAttribute(key, value);
}

for (const [key, path] of Object.entries(atlas.context)) {
  const layer = document.createElementNS(ns, "path");
  layer.setAttribute("d", path);
  byId("context").append(layer);
  context[key] = layer;
}

function updateTiles(left, top, width, height) {
  const level = Math.min(17, Math.max(10, Math.round(13 - Math.log2(unitsPerPixel))));
  const span = 256 * 2 ** (13 - level);
  const [ox, oy] = atlas.origin;
  const visible = new Set();
  for (let x = Math.floor((left + ox) / span); x <= Math.floor((left + width + ox) / span); x++) {
    for (let y = Math.floor((top + oy) / span); y <= Math.floor((top + height + oy) / span); y++) {
      const key = [level, y, x].join("/");
      visible.add(key);
      if (tiles.has(key)) continue;
      const tile = document.createElementNS(ns, "image");
      attrs(tile, {x: x * span - ox, y: y * span - oy, width: span, height: span});
      tile.addEventListener("error", () => {
        tile.dataset.failed = "true";
        terrainStatus();
      });
      tile.setAttribute("href", "https://mapsneu.wien.gv.at/basemap/geolandbasemap/normal/google3857/" + key + ".png");
      tiles.set(key, tile);
      byId("tiles").append(tile);
    }
  }
  for (const [key, tile] of tiles) {
    if (!visible.has(key)) {
      tile.remove();
      tiles.delete(key);
    }
  }
  terrainStatus();
}

function terrainStatus() {
  byId("tileStatus").hidden = !Array.from(tiles.values()).some(tile => tile.dataset.failed);
}

function drawView() {
  const {width, height} = svg.getBoundingClientRect();
  if (!width || !height) return;
  const w = atlas.winners[rule];
  const radius = Math.max(...w.ring.map(([x, y]) => Math.hypot(x - w.pin[0], y - w.pin[1])));
  unitsPerPixel = (2.24 * radius / Math.min(width, height)) / 2 ** zoom;
  const viewWidth = width * unitsPerPixel;
  const viewHeight = height * unitsPerPixel;
  const left = centre[0] - viewWidth / 2;
  const top = centre[1] - viewHeight / 2;
  svg.setAttribute("viewBox", [left, top, viewWidth, viewHeight].join(" "));
  byId("pin").setAttribute("r", 6 * unitsPerPixel);
  byId("foot").setAttribute("r", 4 * unitsPerPixel);
  const [x, y] = atlas.reference;
  const r = 6 * unitsPerPixel;
  byId("benchmark").setAttribute("d", "M" + [x, y-r] + "L" + [x+r, y] + " " + [x, y+r] + " " + [x-r, y] + "Z");
  byId("zoomIn").disabled = zoom === 4;
  byId("zoomOut").disabled = zoom === -1;
  updateTiles(left, top, viewWidth, viewHeight);
}

function fit() {
  centre = [...atlas.winners[rule].pin];
  zoom = 0;
  drawView();
}

function selectRule(key) {
  rule = key;
  const w = atlas.winners[key];
  const road = atlas.roads[w.way_id];
  const [lon, lat] = w.lonlat;
  byId("score").textContent = (w.distance_m / 1000).toFixed(3);
  byId("coords").textContent = lat.toFixed(6) + "° N, " + lon.toFixed(6) + "° E";
  const coordinates = [lat.toFixed(6), lon.toFixed(6)].join(",");
  const address = addresses[coordinates];
  byId("words").textContent = address ? "///" + address : "Look up on what3words";
  byId("words").href = "https://what3words.com/" + (address || coordinates);
  byId("topo").href = "https://maps.bev.gv.at/#/center/" + lon.toFixed(7) + "," + lat.toFixed(7) + "/zoom/14";
  byId("ruleDetail").textContent = rules[key];
  byId("osm").textContent = road.grade.replace("grade", "Grade-") + " " + road.surface + " track ↗";
  byId("osm").href = "https://www.openstreetmap.org/way/" + w.way_id;
  byId("ring").setAttribute("d", "M" + w.ring.join(" ") + "Z");
  byId("nearest").setAttribute("d", road.path);
  const changedRoad = atlas.rough_at_default.way_id;
  const showRough = key === "C" && changedRoad !== atlas.winners.B.way_id;
  byId("rough").setAttribute("d", atlas.roads[changedRoad].path);
  byId("rough").toggleAttribute("hidden", !showRough);
  byId("roughNote").hidden = !showRough;
  byId("roughLink").href = "https://www.openstreetmap.org/way/" + changedRoad;
  attrs(byId("pin"), {cx: w.pin[0], cy: w.pin[1]});
  attrs(byId("foot"), {cx: w.foot[0], cy: w.foot[1]});
  attrs(byId("radius"), {x1: w.pin[0], y1: w.pin[1], x2: w.foot[0], y2: w.foot[1]});
  for (const [grade, layer] of Object.entries(context)) layer.toggleAttribute("hidden", grade > key);
  const ref = w.reference;
  byId("refNote").textContent = "The purple diamond marks Land Steiermark’s published pin, " +
    Math.round(ref.separation_from_winner_m) + " m from this winner. Its nearest qualifying road is " +
    (ref.distance_m / 1000).toFixed(3) + " km away under rule " + key + ".";
  fit();
}

for (const input of document.querySelectorAll('input[name="rule"]')) {
  input.addEventListener("change", () => selectRule(input.value));
}
function compare() {
  const show = byId("compare").checked;
  byId("benchmark").toggleAttribute("hidden", !show);
  byId("refNote").hidden = !show;
}
byId("compare").addEventListener("change", compare);
byId("zoomIn").addEventListener("click", () => { zoom++; drawView(); });
byId("zoomOut").addEventListener("click", () => { zoom--; drawView(); });
byId("fit").addEventListener("click", fit);

svg.addEventListener("pointerdown", event => {
  if (event.button !== 0 || !event.isPrimary) return;
  drag = {x: event.clientX, y: event.clientY, centre: [...centre]};
  svg.setPointerCapture(event.pointerId);
  svg.classList.add("dragging");
});
svg.addEventListener("pointermove", event => {
  if (!drag || !event.isPrimary) return;
  centre = [drag.centre[0] - (event.clientX - drag.x) * unitsPerPixel,
            drag.centre[1] - (event.clientY - drag.y) * unitsPerPixel];
  drawView();
});
svg.addEventListener("lostpointercapture", () => {
  drag = null;
  svg.classList.remove("dragging");
});

selectRule(document.querySelector('input[name="rule"]:checked').value);
compare();
new ResizeObserver(drawView).observe(svg);
