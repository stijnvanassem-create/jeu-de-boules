// Offline support: network first (so new photos/versions arrive), cache as fallback.
const CACHE = 'boules-v1';
const ASSETS = [
  './', 'index.html', 'manifest.json',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png',
  'players/sos.jpg', 'players/dollo.jpg', 'players/tobihash.jpg', 'players/mrneus.jpg'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = await cache.match(req, { ignoreSearch: true });
    const net = fetch(req).then(res => {
      if (res.ok) cache.put(req, res.clone());
      return res;
    });
    if (!cached) return net.catch(() => cache.match('./'));
    // Slow field connection: fall back to cache after 2.5 s
    return Promise.race([
      net.catch(() => cached),
      new Promise(r => setTimeout(() => r(cached), 2500))
    ]);
  })());
});
