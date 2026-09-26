/* Build replaces these constants; news-only publications keep the same shell version. */
const CACHE = "news-shell-__BUILD_ID__";
const SHELL = __SHELL_FILES__;
const PAGES = {
  "/": "/",
  "/index.html": "/",
  "/games": "/games/",
  "/games/": "/games/",
  "/games/index.html": "/games/",
};

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE);
      try {
        await cache.addAll(
          SHELL.map((url) => new Request(url, { cache: "reload" })),
        );
        // A deployment crossing the installation window must not mix HTML and assets.
        const html = (
          await Promise.all(
            ["/", "/games/"].map(async (path) =>
              (await cache.match(path)).text(),
            ),
          )
        ).join("\n");
        for (const asset of html.match(
          /\/assets\/news\/[\w.-]+\.[a-f0-9]{12}\.(?:js|css|svg)/g,
        ) || []) {
          if (!SHELL.includes(asset))
            throw new Error("Page assets belong to another deployment");
        }
        for (const asset of SHELL.filter((url) =>
          /\.[a-f0-9]{12}\.(js|css|svg)$/.test(url),
        )) {
          if (!html.includes(asset))
            throw new Error("Deployment changed during installation");
        }
      } catch (error) {
        await caches.delete(CACHE);
        throw error;
      }
    })(),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((key) => key.startsWith("news-shell-") && key !== CACHE)
          .map((key) => caches.delete(key)),
      );
      await self.clients.claim();
    })(),
  );
});

self.addEventListener("message", (event) => {
  if (event.data?.type === "ACTIVATE_UPDATE") self.skipWaiting();
  if (event.data?.type === "CHECK_OFFLINE" && event.ports[0]) {
    event.waitUntil(
      (async () => {
        try {
          const cache = await caches.open(CACHE);
          const paths = Array.isArray(event.data.paths) ? event.data.paths : [];
          const ready =
            paths.length > 0 &&
            paths.length <= 20 &&
            (
              await Promise.all(
                paths.map(
                  async (path) =>
                    SHELL.includes(path) && !!(await cache.match(path)),
                ),
              )
            ).every(Boolean);
          event.ports[0].postMessage({ ready });
        } catch {
          event.ports[0].postMessage({ ready: false });
        }
      })(),
    );
  }
});

async function navigation(request, page) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 4000);
  try {
    const response = await fetch(request, {
      signal: controller.signal,
      cache: "no-cache",
    });
    if (!response.ok) throw new Error("Page unavailable");
    return response;
  } catch {
    // Keep the precached HTML paired with its own assets until a new worker installs.
    return (await (await caches.open(CACHE)).match(page)) || Response.error();
  } finally {
    clearTimeout(timer);
  }
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin) return;
  if (request.mode === "navigate" && Object.hasOwn(PAGES, url.pathname)) {
    event.respondWith(navigation(request, PAGES[url.pathname]));
  } else if (
    SHELL.includes(url.pathname) &&
    !Object.hasOwn(PAGES, url.pathname)
  ) {
    event.respondWith(
      (async () =>
        (await (await caches.open(CACHE)).match(url.pathname)) ||
        fetch(request))(),
    );
  }
  // News data and refresh APIs always use the network. app.js handles its explicit
  // last-successful-data fallback. Other paths are not intercepted.
});
