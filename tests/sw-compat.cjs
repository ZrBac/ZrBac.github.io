const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");
const source = fs
  .readFileSync(require.resolve("../news/sw.js"), "utf8")
  .replace(
    "__SHELL_FILES__",
    JSON.stringify(["/", "/games/", "/assets/news/compat.test.js"]),
  );
function worker() {
  const handlers = {},
    matches = [];
  const scope = vm.createContext({
    URL,
    Response,
    AbortController,
    setTimeout,
    clearTimeout,
    self: {
      location: { origin: "https://news.test" },
      addEventListener: (type, handler) => (handlers[type] = handler),
    },
    caches: {
      open: async () => ({
        match: async (path) => {
          matches.push(path);
          return new Response("cached " + path);
        },
      }),
    },
    fetch: async () => {
      throw new TypeError("offline");
    },
  });
  vm.runInContext("Object.hasOwn = undefined;", scope);
  vm.runInContext(source, scope);
  function request(path, mode = "navigate", method = "GET") {
    let response;
    handlers.fetch({
      request: { url: new URL(path, "https://news.test").href, mode, method },
      respondWith: (value) => (response = value),
    });
    return response;
  }
  return { request, matches };
}
test("Offline navigation aliases return their matching HTML without Object.hasOwn", async () => {
  const { request } = worker();
  for (const [path, expected] of [
    ["/", "/"],
    ["/index.html", "/"],
    ["/games", "/games/"],
    ["/games/", "/games/"],
    ["/games/index.html", "/games/"],
    ["/games/?v=2", "/games/"],
  ]) {
    assert.equal(await (await request(path)).text(), "cached " + expected);
  }
});
test("Offline shell assets load and unrelated routes still bypass the worker", async () => {
  const { request, matches } = worker();
  assert.equal(
    await (await request("/assets/news/compat.test.js", "cors")).text(),
    "cached /assets/news/compat.test.js",
  );
  for (const path of [
    "/data/news.json",
    "/api/news-refresh",
    "/missing",
    "/toString",
    "https://elsewhere.test/games/",
  ])
    assert.equal(request(path), undefined);
  assert.equal(request("/games/", "navigate", "POST"), undefined);
  assert.deepEqual(matches, ["/assets/news/compat.test.js"]);
});
