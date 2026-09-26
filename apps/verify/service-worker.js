const CACHE = "bhu3d-verify-v2";
const ASSETS = ["./", "./index.html", "./styles.css", "./app.js", "./unit-302-qr.svg", "./manifest.webmanifest", "./trusted-issuers.json", "../../data/generated/citizen_payload.json"];
self.addEventListener("install", (event) => event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS))));
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (event) => event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request))));
