(() => {
  "use strict";
  const button = document.querySelector("#install-app");
  const standalone = window.matchMedia("(display-mode: standalone)");
  const isInstalled = () => standalone.matches || navigator.standalone === true;
  let installPrompt;
  const updateButton = () => {
    button.hidden = isInstalled();
  };
  updateButton();
  standalone.addEventListener?.("change", updateButton);
  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    installPrompt = event;
    updateButton();
  });
  window.addEventListener("appinstalled", () => {
    installPrompt = null;
    button.hidden = true;
  });
  button.addEventListener("click", async () => {
    if (installPrompt) {
      const prompt = installPrompt;
      installPrompt = null;
      try {
        await prompt.prompt();
        await prompt.userChoice;
        return;
      } catch {
        /* Browser may have withdrawn its installation prompt. */
      }
    }
    document.querySelector("#dialog-title").textContent = "安装到桌面";
    document.querySelector("#dialog-content").innerHTML =
      "<p>安装后可从桌面直接打开资讯，使用独立窗口阅读。</p>" +
      "<h3>电脑 Chrome / Edge</h3><p>点击地址栏的安装图标，或在浏览器菜单中选择“安装资讯”或“将此网站安装为应用”。</p>" +
      "<h3>iPhone / iPad</h3><p>在 Safari 中打开本站，点击分享按钮，选择“添加到主屏幕”。</p>" +
      "<h3>Android</h3><p>在浏览器菜单中选择“安装应用”或“添加到主屏幕”。</p>" +
      "<h3>Mac Safari</h3><p>在支持的版本中，选择“文件 → 添加到程序坞”。</p>" +
      "<p>首次联网准备完成后，可离线阅读已保存的资讯、收藏和游玩小游戏。更新资讯、打开新闻原文需要联网；清除浏览器数据会移除本地缓存。</p>";
    document.querySelector("#info-dialog").showModal();
  });

  const offlineStatus = document.querySelector("#offline-status");
  const offlineText = (ready) => {
    if (!offlineStatus) return;
    offlineStatus.textContent = ready
      ? "已准备好，可离线玩"
      : "离线准备尚未完成，请保持联网；如有新版本，请先更新页面。";
    offlineStatus.classList.toggle("ready", ready);
  };
  if (!("serviceWorker" in navigator) || !window.isSecureContext) {
    if (offlineStatus)
      offlineStatus.textContent =
        "当前浏览器无法保存离线版本，联网时仍可游玩。";
    return;
  }
  const checkOffline = async () => {
    if (!offlineStatus) return;
    const controller = navigator.serviceWorker.controller;
    if (!controller) {
      offlineText(false);
      return;
    }
    const paths = [
      "/games/",
      ...Array.from(
        document.querySelectorAll("script[src], link[rel=stylesheet]"),
        (el) => new URL(el.src || el.href).pathname,
      ),
    ];
    const channel = new MessageChannel();
    const ready = await new Promise((resolve) => {
      const timer = setTimeout(() => resolve(false), 2500);
      channel.port1.onmessage = (event) => {
        clearTimeout(timer);
        resolve(event.data?.ready === true);
      };
      controller.postMessage({ type: "CHECK_OFFLINE", paths }, [channel.port2]);
    });
    channel.port1.close();
    offlineText(ready);
  };
  let registration;
  let applyingUpdate = false;
  const notice = document.querySelector("#pwa-update");
  const showUpdate = () => {
    if (registration?.waiting) notice.hidden = false;
  };
  document.querySelector("#apply-update").addEventListener("click", () => {
    if (!registration?.waiting) return;
    applyingUpdate = true;
    registration.waiting.postMessage({ type: "ACTIVATE_UPDATE" });
  });
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (applyingUpdate) window.location.reload();
    else checkOffline();
  });
  window.addEventListener("load", async () => {
    try {
      registration = await navigator.serviceWorker.register("/sw.js", {
        scope: "/",
        updateViaCache: "none",
      });
      showUpdate();
      checkOffline();
      navigator.serviceWorker.ready.then(checkOffline);
      registration.addEventListener("updatefound", () => {
        const worker = registration.installing;
        worker?.addEventListener("statechange", () => {
          if (
            worker.state === "installed" &&
            navigator.serviceWorker.controller
          )
            showUpdate();
        });
      });
    } catch {
      /* Normal browsing still works when service workers are unavailable. */
      offlineText(false);
    }
  });
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
      checkOffline();
      if (navigator.onLine && registration)
        registration.update().catch(() => {});
    }
  });
})();
