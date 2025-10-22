// static/service-worker.js
const CACHE_NAME = 'wellnesscoach-v1';
const ASSETS = [
  '/',                              // app shell
  '/static/manifest.webmanifest',
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
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return; // don’t cache posts/uploads

  event.respondWith(
    caches.match(req).then((cached) => {
      const fetchPromise = fetch(req).then((networkResp) => {
        const copy = networkResp.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
        return networkResp;
      }).catch(() => cached); // offline fallback
      return cached || fetchPromise;
    })
  );
});
