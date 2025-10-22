// static/service-worker.js
const CACHE_NAME = 'wellnesscoach-v3'; // bumped version to force reload

const ASSETS = [
  '/WellnessCoach/',

  // Static assets
  '/WellnessCoach/static/manifest.webmanifest',
  '/WellnessCoach/static/file_00000000c9b061fab40d391bb3ffd5d2.png',
  '/WellnessCoach/static/file_00000000174c61f6a427f26b72baa8df.png',
  '/WellnessCoach/static/file_000000001e8c62439bd32306d8c7ab28.png'
];

// Install service worker and cache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate and clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Serve cached files when offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((resp) =>
      resp || fetch(event.request).catch(() => caches.match('/WellnessCoach/'))
    )
  );
});
