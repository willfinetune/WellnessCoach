// sw.js (root)
// Minimal SW: needed for installability + fast updates.
// No offline caching here to avoid stale content.

self.addEventListener('install', (event) => {
  // Activate the new SW immediately
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // Control open clients without reload
  event.waitUntil(self.clients.claim());
});
