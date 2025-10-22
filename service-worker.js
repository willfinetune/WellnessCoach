// service-worker.js
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

// Optional: network-first for launch page
self.addEventListener('fetch', (event) => {
  // Let the network handle everything; SW is present only to satisfy PWA installability
});
