// static/service-worker.js
const CACHE_NAME = 'wellnesscoach-v4'; // bump to force clients to refresh

const ASSETS = [
  '/',                                   // app root
  '/static/manifest.webmanifest',        // manifest
  '/static/file_00000000c9b061fab40d391bb3ffd5d2.png', // 512
  '/static/file_00000000174c61f6a427f26b72baa8df.png', // 192
  '/static/file_000000001e8c62439bd32306d8c7ab28.png'  // 180
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((resp) =>
      resp || fetch(event.request).catch(() => caches.match('/'))
    )
  );
});
