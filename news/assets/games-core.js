/* Original arcade rules, shared by the browser and deterministic tests. */
(function (root) {
  "use strict";
  const W = 360,
    H = 460;
  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
  const overlaps = (a, b) =>
    a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  function bricks(level) {
    return Array.from({ length: 35 }, (_, i) => ({
      x: 16 + (i % 7) * 47,
      y: 60 + Math.floor(i / 7) * 23,
      w: 43,
      h: 17,
      hp: level >= 3 && i < 14 ? 2 : 1,
      row: Math.floor(i / 7),
    }));
  }
  function resetBall(s) {
    s.ball = { x: s.paddle, y: 375, vx: 95, vy: -(205 + s.level * 15), r: 6 };
    s.wait = 0.8;
  }
  function create(kind) {
    const s = {
      kind,
      score: 0,
      level: 1,
      lives: 3,
      time: 0,
      ended: false,
      won: false,
      event: "",
      particles: [],
    };
    if (kind === "breakout") {
      s.paddle = W / 2;
      s.bricks = bricks(1);
      resetBall(s);
    }
    if (kind === "shooter")
      Object.assign(s, {
        player: { x: 168, y: 380, w: 24, h: 28 },
        bullets: [],
        enemies: [],
        spawn: 0.5,
        fire: 0,
        invincible: 0,
      });
    if (kind === "runner")
      Object.assign(s, {
        player: { x: 65, y: 342, w: 24, h: 28 },
        vy: 0,
        jumps: 0,
        obstacles: [],
        spawn: 1.4,
        distance: 0,
      });
    return s;
  }
  function burst(s, x, y, color) {
    for (let i = 0; i < 8; i++)
      s.particles.push({
        x,
        y,
        vx: Math.cos((i * Math.PI) / 4) * 60,
        vy: Math.sin((i * Math.PI) / 4) * 60,
        life: 0.4,
        color,
      });
  }
  function jump(s) {
    if (s.kind !== "runner" || s.ended || s.jumps >= 2) return false;
    s.vy = -335;
    s.jumps++;
    return true;
  }
  function step(s, dt, input = {}, random = Math.random) {
    if (s.ended) return;
    s.time += dt;
    s.event = "";
    for (const p of s.particles) {
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.life -= dt;
    }
    s.particles = s.particles.filter((p) => p.life > 0);
    if (s.kind === "breakout") {
      s.paddle = clamp(
        input.x ?? s.paddle + (input.dx || 0) * 320 * dt,
        39,
        W - 39,
      );
      if (s.wait > 0) {
        s.wait -= dt;
        s.ball.x = s.paddle;
        return;
      }
      const b = s.ball,
        oldX = b.x,
        oldY = b.y;
      b.x += b.vx * dt;
      b.y += b.vy * dt;
      if (b.x < b.r || b.x > W - b.r) {
        b.x = clamp(b.x, b.r, W - b.r);
        b.vx *= -1;
      }
      if (b.y < 30 + b.r) {
        b.y = 30 + b.r;
        b.vy = Math.abs(b.vy);
      }
      if (
        b.vy > 0 &&
        oldY + b.r <= 399 &&
        b.y + b.r >= 399 &&
        b.x + b.r >= s.paddle - 38 &&
        b.x - b.r <= s.paddle + 38
      ) {
        const angle = clamp((b.x - s.paddle) / 38, -0.95, 0.95) * 1.05;
        const speed = Math.min(370, Math.hypot(b.vx, b.vy) + 2);
        b.vx = Math.sin(angle) * speed;
        b.vy = -Math.cos(angle) * speed;
        b.y = 399 - b.r;
      }
      for (const brick of s.bricks) {
        if (
          brick.hp <= 0 ||
          !overlaps(
            { x: b.x - b.r, y: b.y - b.r, w: b.r * 2, h: b.r * 2 },
            brick,
          )
        )
          continue;
        brick.hp--;
        s.score += 10;
        burst(s, b.x, b.y, "#d58b62");
        if (oldY + b.r <= brick.y || oldY - b.r >= brick.y + brick.h) {
          b.vy *= -1;
          b.y = oldY;
        } else {
          b.vx *= -1;
          b.x = oldX;
        }
        break;
      }
      if (b.y > H + b.r) {
        s.lives--;
        s.event = "漏接一次";
        if (!s.lives) s.ended = true;
        else resetBall(s);
      }
      if (s.bricks.every((b) => b.hp === 0)) {
        if (s.level === 5) {
          s.ended = true;
          s.won = true;
        } else {
          s.level++;
          s.bricks = bricks(s.level);
          resetBall(s);
          s.event = "进入第 " + s.level + " 关";
        }
      }
    } else if (s.kind === "shooter") {
      const p = s.player;
      p.x = clamp(
        input.x === undefined
          ? p.x + (input.dx || 0) * 250 * dt
          : input.x - p.w / 2,
        4,
        W - p.w - 4,
      );
      p.y = clamp(
        input.y === undefined
          ? p.y + (input.dy || 0) * 250 * dt
          : input.y - p.h / 2,
        165,
        H - p.h - 8,
      );
      s.level = 1 + Math.floor(s.score / 200);
      s.invincible = Math.max(0, s.invincible - dt);
      s.fire -= dt;
      s.spawn -= dt;
      if (s.fire <= 0) {
        s.bullets.push({ x: p.x + 10, y: p.y, w: 4, h: 12 });
        s.fire = 0.16;
      }
      if (s.spawn <= 0) {
        s.enemies.push({
          x: 12 + random() * 304,
          y: -32,
          w: 26,
          h: 28,
          speed: Math.min(185, 62 + s.level * 11),
          hp: s.level >= 3 ? 2 : 1,
        });
        s.spawn =
          Math.max(0.25, 0.85 - s.level * 0.04) * (0.8 + random() * 0.4);
      }
      for (const b of s.bullets) b.y -= 390 * dt;
      for (const e of s.enemies) {
        e.y += e.speed * dt;
        for (const b of s.bullets)
          if (!b.dead && e.hp > 0 && overlaps(b, e)) {
            b.dead = true;
            e.hp--;
            if (e.hp === 0) {
              s.score += 20;
              burst(s, e.x + 13, e.y + 14, "#e8b180");
            }
          }
        if (e.hp > 0 && (overlaps(p, e) || e.y > H)) {
          const escaped = e.y > H;
          e.hp = 0;
          if (escaped || s.invincible <= 0) {
            s.lives--;
            s.invincible = 1.3;
            s.event = escaped ? "敌机突破防线" : "被敌机击中";
            burst(s, p.x + 12, p.y, "#9ad9ce");
          }
          if (s.lives <= 0) {
            s.ended = true;
            break;
          }
        }
      }
      s.bullets = s.bullets.filter((b) => !b.dead && b.y > -15);
      s.enemies = s.enemies.filter((e) => e.hp > 0 && e.y <= H);
    } else if (s.kind === "runner") {
      const speed = Math.min(275, 165 + s.distance / 70),
        p = s.player;
      s.distance += speed * dt;
      s.score = Math.floor(s.distance / 10);
      s.level = 1 + Math.floor(s.score / 100);
      s.vy += 950 * dt;
      p.y += s.vy * dt;
      if (p.y >= 342) {
        p.y = 342;
        s.vy = 0;
        s.jumps = 0;
      }
      s.spawn -= dt;
      if (s.spawn <= 0) {
        const height = random() < 0.55 ? 30 : 52;
        s.obstacles.push({
          x: W + 12,
          y: 370 - height,
          w: 22 + random() * 15,
          h: height,
        });
        s.spawn = (260 + random() * 130) / speed;
      }
      for (const o of s.obstacles) {
        o.x -= speed * dt;
        if (overlaps({ x: p.x + 3, y: p.y + 2, w: p.w - 6, h: p.h - 3 }, o)) {
          s.ended = true;
          s.event = "碰到障碍了";
        }
      }
      s.obstacles = s.obstacles.filter((o) => o.x + o.w > 0);
    }
  }
  const api = { W, H, clamp, overlaps, create, step, jump };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.GamesCore = api;
})(globalThis);
