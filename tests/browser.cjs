// Optional end-to-end checks. Install Playwright outside the legacy Hexo dependencies.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const assert = require("node:assert/strict");
const base = process.env.NEWS_BASE_URL || "http://127.0.0.1:8765";

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ["--no-sandbox"],
  });
  try {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1000 },
    });
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(base, { waitUntil: "networkidle" });
    await page.locator(".article").first().waitFor();
    assert.equal(await page.locator(".article").count(), 12);
    await page.click("#load-more");
    assert.equal(await page.locator(".article").count(), 24);

    await page.click('[data-filter="ai"]');
    assert(
      (await page.locator(".article .category-label").allTextContents()).every(
        (t) => t === "人工智能",
      ),
    );
    await page.fill("#search", "这个关键词绝对不存在_842398");
    assert.equal(await page.locator(".article").count(), 0);
    await page.click("[data-reset]");
    await page.locator(".article").first().waitFor();
    await page.selectOption("#source-filter", "bbc");
    assert(
      (await page.locator(".article-meta").allTextContents()).every((t) =>
        t.includes("BBC 中文"),
      ),
    );
    await page.selectOption("#source-filter", "all");
    await page.click(".save-button >> nth=0");
    const title = await page.locator(".article h3").first().textContent();
    await page.click(".saved-link");
    assert.equal(await page.locator(".article").count(), 1);
    assert.equal(
      await page.locator(".article h3").first().textContent(),
      title,
    );
    await page.reload({ waitUntil: "networkidle" });
    assert.equal(await page.locator(".article").count(), 1);
    await page.click(".save-button");
    assert.equal(await page.locator(".article").count(), 0);
    assert.match(
      await page.locator(".empty-state h3").textContent(),
      /还没有收藏/,
    );

    await page.click('a[data-view="brief"]');
    assert((await page.locator(".article").count()) <= 10);
    const selectedDate = await page.inputValue("#date-filter");
    assert(selectedDate.length === 10);
    await page.fill("#date-filter", "2020-01-01");
    assert.equal(await page.locator(".article").count(), 0);
    await page.click("#clear-date");
    await page.locator(".article").first().waitFor();

    await page.click("#sources-trigger");
    assert.equal(await page.locator(".source-row").count(), 6);
    await page.keyboard.press("Escape");
    assert.equal(await page.locator("dialog").evaluate((e) => e.open), false);
    await page.click("#theme-toggle");
    assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
    await page.reload({ waitUntil: "networkidle" });
    assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
    await page.click("#theme-toggle");
    await page.keyboard.press("Control+k");
    assert.equal(
      await page
        .locator("#search")
        .evaluate((e) => e === document.activeElement),
      true,
    );
    await page.goto(base + "/#all", { waitUntil: "networkidle" });
    for (const width of [360, 390, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      assert.equal(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
        false,
        `overflow at ${width}`,
      );
    }
    await page.screenshot({
      path: "/tmp/zrbac-news-desktop.png",
      fullPage: true,
    });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({
      path: "/tmp/zrbac-news-mobile.png",
      fullPage: true,
    });
    const blog = await page.request.get(base + "/blog/");
    assert.equal(blog.status(), 200);
    assert.match(await blog.text(), /Java-8-HashMap/);
    const article = await page.request.get(
      base + "/2020/09/25/Java-8-HashMap/",
    );
    assert.equal(article.status(), 200);
    assert.match(await article.text(), /href="\/blog\/"/);
    const feed = await page.request.get(base + "/news.xml");
    assert.equal(feed.status(), 200);
    assert.match(await feed.text(), /<rss/);

    // Verify feed HTML is rendered as inert text, and unsafe URLs never become article links.
    const fixture = await (
      await page.request.get(base + "/data/news.json")
    ).json();
    fixture.articles[0].title = '<img src=x onerror="window.injected=true">';
    fixture.articles[0].excerpt = "<script>window.injected=true</script>";
    fixture.articles[1].url = "javascript:window.injected=true";
    await page.route("**/data/news.json", (route) =>
      route.fulfill({ json: fixture }),
    );
    await page.reload({ waitUntil: "networkidle" });
    assert.equal(await page.locator(".article img,.article script").count(), 0);
    assert.equal(await page.locator('a[href^="javascript:"]').count(), 0);
    assert.equal(await page.evaluate(() => window.injected), undefined);

    await page.unroute("**/data/news.json");
    await page.route("**/data/news.json", (route) =>
      route.fulfill({ status: 503, body: "unavailable" }),
    );
    await page.reload({ waitUntil: "networkidle" });
    await page.locator("[data-retry]").waitFor();
    await page.unroute("**/data/news.json");
    await page.click("[data-retry]");
    await page.locator(".article").first().waitFor();
    assert.deepEqual(errors, []);
    console.log(
      "PASS: filters, search, pagination, saved persistence, brief/date, source dialog, theme, keyboard, 4 viewports, blog preservation, RSS, XSS safety, failure/retry.",
    );
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
