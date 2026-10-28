(() => {
  window.AlbusCatWorld = true;

  const cat = document.getElementById('cat');
  const track = document.getElementById('catTrack');
  const hint = document.getElementById('catHint');
  const portrait = document.getElementById('portrait');
  const portraitWrap = document.getElementById('portraitWrap');
  if (!cat || !track || !portrait || !portraitWrap) return;

  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const CAT_WIDTH = 72;
  const CAT_HEIGHT = 56;
  const HOME_X = 34;
  const MAX_JUMP_Y = 178;
  const MAX_JUMP_GAP = 150;
  const textPlatformSelector = '.brand, .eyebrow, #hero-title, .hero-note, .section-label, .statement, .project h3';
  const rulePlatformSelector = '.site-header, .cat-divider, .section-row, .project, footer';

  let state = 'sleeping';
  let drag = null;
  let activeAnimation = null;
  let actionToken = 0;
  let fusionTimer = null;
  let fusionReady = false;
  let delayedAction = null;

  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const pageRect = element => {
    const rect = element.getBoundingClientRect();
    return {
      left: rect.left + scrollX,
      right: rect.right + scrollX,
      top: rect.top + scrollY,
      bottom: rect.bottom + scrollY,
      width: rect.width,
      height: rect.height
    };
  };

  function dismissHint() {
    hint.classList.add('dismissed');
  }

  function cancelCurrentAction() {
    actionToken += 1;
    clearTimeout(delayedAction);
    delayedAction = null;
    if (activeAnimation) {
      activeAnimation.onfinish = null;
      activeAnimation.oncancel = null;
      activeAnimation.cancel();
      activeAnimation = null;
    }
  }

  function clearFusionTarget() {
    clearTimeout(fusionTimer);
    fusionTimer = null;
    fusionReady = false;
    portraitWrap.classList.remove('cat-target', 'cat-ready');
  }

  function updateFusionTarget(inside) {
    if (!inside) {
      clearFusionTarget();
      return;
    }
    if (portraitWrap.classList.contains('cat-target')) return;
    portraitWrap.classList.add('cat-target');
    fusionTimer = setTimeout(() => {
      fusionReady = true;
      portraitWrap.classList.add('cat-ready');
    }, reducedMotion.matches ? 0 : 1600);
  }

  function setDirection(deltaX) {
    if (Math.abs(deltaX) > 2) cat.style.setProperty('--cat-direction', deltaX < 0 ? '-1' : '1');
  }

  function setDetachedPosition(left, top) {
    cat.style.position = 'absolute';
    cat.style.left = `${left}px`;
    cat.style.top = `${top}px`;
    cat.style.transform = 'none';
  }

  function detachAtCurrentPosition() {
    const rect = cat.getBoundingClientRect();
    document.body.appendChild(cat);
    setDetachedPosition(rect.left + scrollX, rect.top + scrollY);
    return { left: rect.left + scrollX, top: rect.top + scrollY };
  }

  function homePlatform() {
    const rect = pageRect(track);
    return {
      id: 'home',
      kind: 'home',
      left: rect.left,
      right: rect.right,
      y: rect.top,
      targetX: rect.left + HOME_X
    };
  }

  function textRuns(element, prefix) {
    const runs = [];
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let textNode;
    let runIndex = 0;
    while ((textNode = walker.nextNode())) {
      const text = textNode.textContent || '';
      for (let index = 0; index < text.length; index += 1) {
        if (/\s/.test(text[index])) continue;
        const range = document.createRange();
        range.setStart(textNode, index);
        range.setEnd(textNode, index + 1);
        const rect = range.getBoundingClientRect();
        if (rect.width < 1 || rect.height < 1) continue;
        runs.push({
          id: `${prefix}-glyph-${runIndex++}`,
          kind: 'text',
          left: rect.left + scrollX,
          right: rect.right + scrollX,
          y: rect.top + scrollY + Math.max(1, rect.height * .08)
        });
      }
    }
    return runs;
  }

  function collectPlatforms() {
    const platforms = [];
    document.querySelectorAll(rulePlatformSelector).forEach((element, index) => {
      const rect = pageRect(element);
      const isDivider = element.classList.contains('cat-divider');
      const isFooter = element.tagName === 'FOOTER';
      platforms.push({
        id: `rule-${index}-top`,
        kind: isDivider ? 'home-rule' : 'rule',
        left: rect.left,
        right: rect.right,
        y: isFooter ? rect.top : rect.top
      });
      if (!isDivider && rect.height > 40) {
        platforms.push({
          id: `rule-${index}-bottom`,
          kind: 'rule',
          left: rect.left,
          right: rect.right,
          y: rect.bottom
        });
      }
    });
    document.querySelectorAll(textPlatformSelector).forEach((element, index) => {
      platforms.push(...textRuns(element, `text-${index}`));
    });
    const home = homePlatform();
    platforms.push(home);
    return { platforms, home };
  }

  function horizontalGap(a, b) {
    if (a.right >= b.left && b.right >= a.left) return 0;
    return a.right < b.left ? b.left - a.right : a.left - b.right;
  }

  function firstLanding(catBox, platforms) {
    const pawLeft = catBox.left + CAT_WIDTH * .3;
    const pawRight = catBox.left + CAT_WIDTH * .76;
    const foot = catBox.top + CAT_HEIGHT - 5;
    return platforms
      .filter(platform => platform.y >= foot - 7 && platform.y <= foot + innerHeight * .82)
      .filter(platform => pawRight >= platform.left - 12 && pawLeft <= platform.right + 12)
      .sort((a, b) => a.y - b.y)[0] || null;
  }

  function routeBetween(start, home, platforms) {
    const nodes = [start, ...platforms.filter(platform => platform.id !== start.id && platform.id !== home.id), home];
    const destination = nodes.length - 1;
    const distance = Array(nodes.length).fill(Infinity);
    const previous = Array(nodes.length).fill(-1);
    const visited = Array(nodes.length).fill(false);
    distance[0] = 0;

    for (let step = 0; step < nodes.length; step += 1) {
      let current = -1;
      for (let index = 0; index < nodes.length; index += 1) {
        if (!visited[index] && (current < 0 || distance[index] < distance[current])) current = index;
      }
      if (current < 0 || !Number.isFinite(distance[current])) break;
      if (current === destination) break;
      visited[current] = true;
      for (let next = 0; next < nodes.length; next += 1) {
        if (visited[next] || next === current) continue;
        const dy = Math.abs(nodes[next].y - nodes[current].y);
        const gap = horizontalGap(nodes[current], nodes[next]);
        if (dy > MAX_JUMP_Y || gap > MAX_JUMP_GAP) continue;
        if (dy < 4 && gap < 4) continue;
        const upwardCost = nodes[next].y < nodes[current].y ? 24 : 0;
        const weight = Math.hypot(dy, gap) + upwardCost + (nodes[next].kind === 'text' ? 16 : 0);
        if (distance[current] + weight < distance[next]) {
          distance[next] = distance[current] + weight;
          previous[next] = current;
        }
      }
    }

    if (!Number.isFinite(distance[destination])) return [];
    const route = [];
    let cursor = destination;
    while (cursor > 0) {
      route.unshift(nodes[cursor]);
      cursor = previous[cursor];
      if (cursor < 0) return [];
    }
    return route;
  }

  function animateTransform(keyframes, options, token) {
    return new Promise(resolve => {
      if (token !== actionToken) return resolve(false);
      const animation = cat.animate(keyframes, options);
      activeAnimation = animation;
      animation.onfinish = () => {
        if (activeAnimation === animation) activeAnimation = null;
        animation.oncancel = null;
        animation.cancel();
        resolve(token === actionToken);
      };
      animation.oncancel = () => {
        if (activeAnimation === animation) activeAnimation = null;
        resolve(false);
      };
    });
  }

  async function fallTo(platform, token) {
    const current = pageRect(cat);
    const targetLeft = clamp(current.left, platform.left - 10, Math.max(platform.left - 10, platform.right - CAT_WIDTH + 10));
    const targetTop = platform.y - CAT_HEIGHT + 7;
    const dx = targetLeft - current.left;
    const dy = Math.max(0, targetTop - current.top);
    cat.classList.remove('sleeping', 'looking', 'dragging');
    const ok = await animateTransform([
      { transform: 'translate(0,0) rotate(0deg)' },
      { transform: `translate(${dx * .22}px, ${Math.min(-20, dy * .08 - 24)}px) rotate(${dx < 0 ? -5 : 5}deg)`, offset: .25 },
      { transform: `translate(${dx}px, ${dy}px) rotate(0deg)` }
    ], {
      duration: reducedMotion.matches ? 1 : clamp(340 + dy * 1.2, 380, 920),
      easing: 'cubic-bezier(.22,.28,.25,1)',
      fill: 'forwards'
    }, token);
    if (!ok) return false;
    setDetachedPosition(targetLeft, targetTop);
    cat.classList.add('looking');
    return true;
  }

  async function hopTo(platform, isHome, token) {
    const current = pageRect(cat);
    const currentCenter = current.left + CAT_WIDTH / 2;
    let targetLeft;
    if (isHome) {
      targetLeft = platform.targetX;
    } else {
      const preferredCenter = clamp(currentCenter, platform.left + CAT_WIDTH * .35, platform.right - CAT_WIDTH * .35);
      targetLeft = preferredCenter - CAT_WIDTH / 2;
    }
    const targetTop = platform.y - CAT_HEIGHT + 7;
    const dx = targetLeft - current.left;
    const dy = targetTop - current.top;
    const sameLevel = Math.abs(dy) < 10;
    setDirection(dx);
    cat.classList.remove('looking', 'sleeping');
    cat.classList.add('running');
    const height = sameLevel ? 0 : clamp(52 + Math.max(0, -dy) * .24, 56, 112);
    const frames = sameLevel ? [
      { transform: 'translate(0,0)' },
      { transform: `translate(${dx}px, ${dy}px)` }
    ] : [
      { transform: 'translate(0,0) rotate(0deg)' },
      { transform: `translate(${dx * .5}px, ${dy * .5 - height}px) rotate(${dx < 0 ? -6 : 6}deg)`, offset: .5 },
      { transform: `translate(${dx}px, ${dy}px) rotate(0deg)` }
    ];
    const ok = await animateTransform(frames, {
      duration: reducedMotion.matches ? 1 : sameLevel ? clamp(Math.abs(dx) * 2.1, 280, 1100) : clamp(520 + Math.hypot(dx, dy) * .65, 560, 1050),
      easing: sameLevel ? 'linear' : 'cubic-bezier(.35,.05,.25,1)',
      fill: 'forwards'
    }, token);
    if (!ok) return false;
    setDetachedPosition(targetLeft, targetTop);
    cat.classList.remove('running');
    return true;
  }

  function finishHome() {
    clearFusionTarget();
    cat.hidden = false;
    cat.removeAttribute('style');
    cat.removeAttribute('data-grab');
    track.appendChild(cat);
    cat.style.setProperty('--cat-x', `${HOME_X}px`);
    cat.classList.remove('running', 'dragging', 'looking');
    cat.classList.add('sleeping');
    state = 'sleeping';
  }

  async function returnHomeFrom(startPlatform, token) {
    if (token !== actionToken) return;
    const world = collectPlatforms();
    const route = routeBetween(startPlatform, world.home, world.platforms);
    state = 'returning';
    cat.classList.remove('looking');
    const steps = route.length ? route : [world.home];
    for (const platform of steps) {
      const ok = await hopTo(platform, platform.id === 'home', token);
      if (!ok) return;
    }
    if (token === actionToken) finishHome();
  }

  async function dropIntoWorld(token) {
    const world = collectPlatforms();
    const catBox = pageRect(cat);
    const landing = firstLanding(catBox, world.platforms);
    if (!landing) {
      await returnHomeFrom({ id: 'air', kind: 'air', left: catBox.left, right: catBox.right, y: catBox.bottom }, token);
      return;
    }
    state = 'falling';
    const landed = await fallTo(landing, token);
    if (!landed || token !== actionToken) return;
    state = 'perched';
    delayedAction = setTimeout(() => returnHomeFrom(landing, token), reducedMotion.matches ? 0 : 900);
  }

  async function perchAndFuse(token) {
    const current = pageRect(cat);
    const face = pageRect(portrait);
    const targetLeft = face.left + face.width * .5 - CAT_WIDTH / 2;
    const targetTop = face.top + face.height * .13;
    const dx = targetLeft - current.left;
    const dy = targetTop - current.top;
    cat.classList.remove('dragging', 'sleeping');
    cat.removeAttribute('data-grab');
    state = 'fusing';
    const ok = await animateTransform([
      { transform: 'translate(0,0) scale(1)' },
      { transform: `translate(${dx * .52}px, ${dy - 46}px) scale(.9)`, offset: .52 },
      { transform: `translate(${dx}px, ${dy}px) scale(.72)` }
    ], {
      duration: reducedMotion.matches ? 1 : 620,
      easing: 'cubic-bezier(.2,.75,.2,1)',
      fill: 'forwards'
    }, token);
    if (!ok || token !== actionToken) return;
    setDetachedPosition(targetLeft, targetTop);
    cat.style.transform = 'scale(.72)';
    cat.classList.add('looking');
    delayedAction = setTimeout(() => fuse(token), reducedMotion.matches ? 0 : 760);
  }

  function fuse(token = actionToken) {
    if (token !== actionToken) return;
    clearFusionTarget();
    cat.classList.remove('dragging', 'running', 'looking');
    cat.removeAttribute('data-grab');
    cat.hidden = true;
    portraitWrap.classList.add('fused');
    portrait.setAttribute('aria-label', 'Albus 猫猫形态；点击释放小猫');
    document.body.classList.remove('cat-dragging');
    state = 'fused';
  }

  function pointInsidePortrait(clientX, clientY) {
    const rect = portrait.getBoundingClientRect();
    const nx = (clientX - (rect.left + rect.width / 2)) / (rect.width * .46);
    const ny = (clientY - (rect.top + rect.height * .5)) / (rect.height * .46);
    return nx * nx + ny * ny <= 1;
  }

  function runOnHomeLine() {
    if (state !== 'sleeping' && state !== 'home') return;
    cancelCurrentAction();
    dismissHint();
    state = 'running';
    cat.classList.remove('sleeping', 'looking');
    cat.classList.add('running');
    const from = HOME_X;
    const target = clamp(track.clientWidth * .72, HOME_X + 120, track.clientWidth - CAT_WIDTH - 8);
    setDirection(target - from);
    const token = actionToken;
    animateTransform([
      { transform: `translateX(${from}px)` },
      { transform: `translateX(${target}px)` }
    ], {
      duration: reducedMotion.matches ? 1 : clamp((target - from) * 2.1, 520, 1350),
      easing: 'cubic-bezier(.28,.08,.18,1)',
      fill: 'forwards'
    }, token).then(ok => {
      if (!ok || token !== actionToken) return;
      cat.style.setProperty('--cat-x', `${target}px`);
      delayedAction = setTimeout(() => {
        if (token !== actionToken) return;
        setDirection(from - target);
        animateTransform([
          { transform: `translateX(${target}px)` },
          { transform: `translateX(${from}px)` }
        ], {
          duration: reducedMotion.matches ? 1 : clamp((target - from) * 2.1, 520, 1350),
          easing: 'cubic-bezier(.28,.08,.18,1)',
          fill: 'forwards'
        }, token).then(returned => {
          if (returned && token === actionToken) finishHome();
        });
      }, reducedMotion.matches ? 0 : 520);
    });
  }

  function beginPointer(event) {
    if (state === 'fused') return;
    const rect = cat.getBoundingClientRect();
    cancelCurrentAction();
    clearFusionTarget();
    const localX = event.clientX - rect.left;
    drag = {
      id: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      offsetX: event.clientX - rect.left,
      offsetY: event.clientY - rect.top,
      moved: false,
      grab: localX < rect.width * .28 ? 'tail' : localX > rect.width * .69 ? 'head' : 'body'
    };
    cat.classList.remove('sleeping', 'looking', 'running');
    cat.setPointerCapture?.(event.pointerId);
  }

  cat.addEventListener('pointerdown', event => {
    event.preventDefault();
    beginPointer(event);
  });

  cat.addEventListener('pointermove', event => {
    if (!drag || drag.id !== event.pointerId) return;
    if (!drag.moved && Math.hypot(event.clientX - drag.startX, event.clientY - drag.startY) < 6) return;
    if (!drag.moved) {
      drag.moved = true;
      detachAtCurrentPosition();
      cat.setPointerCapture?.(event.pointerId);
      state = 'dragging';
      dismissHint();
      cat.classList.add('dragging');
      cat.dataset.grab = drag.grab;
      document.body.classList.add('cat-dragging');
    }
    setDetachedPosition(event.clientX + scrollX - drag.offsetX, event.clientY + scrollY - drag.offsetY);
    cat.dataset.grab = drag.grab;
    updateFusionTarget(pointInsidePortrait(event.clientX, event.clientY));
  });

  cat.addEventListener('pointerup', event => {
    if (!drag || drag.id !== event.pointerId) return;
    const didMove = drag.moved;
    drag = null;
    document.body.classList.remove('cat-dragging');
    if (!didMove) {
      finishHome();
      runOnHomeLine();
      return;
    }
    cat.classList.remove('dragging');
    cat.removeAttribute('data-grab');
    const token = actionToken;
    const overPortrait = pointInsidePortrait(event.clientX, event.clientY);
    if (overPortrait && fusionReady) fuse(token);
    else if (overPortrait) {
      clearFusionTarget();
      perchAndFuse(token);
    } else {
      clearFusionTarget();
      dropIntoWorld(token);
    }
  });

  cat.addEventListener('pointercancel', () => {
    if (!drag) return;
    const moved = drag.moved;
    drag = null;
    clearFusionTarget();
    document.body.classList.remove('cat-dragging');
    cat.classList.remove('dragging');
    cat.removeAttribute('data-grab');
    if (moved) dropIntoWorld(actionToken);
    else finishHome();
  });

  cat.addEventListener('click', event => {
    if (event.detail === 0) runOnHomeLine();
  });

  function releaseCat() {
    if (state !== 'fused') return;
    cancelCurrentAction();
    portraitWrap.classList.remove('fused');
    portrait.setAttribute('aria-label', 'Albus 角色；把小猫拖到这里会触发隐藏互动');
    cat.hidden = false;
    document.body.appendChild(cat);
    const face = pageRect(portrait);
    setDetachedPosition(face.right - CAT_WIDTH * .82, face.top + face.height * .24);
    cat.classList.remove('sleeping');
    cat.classList.add('looking');
    state = 'perched';
    const token = actionToken;
    delayedAction = setTimeout(() => {
      const start = {
        id: 'portrait-release',
        kind: 'portrait',
        left: face.left,
        right: face.right,
        y: face.top + face.height * .43
      };
      returnHomeFrom(start, token);
    }, reducedMotion.matches ? 0 : 420);
  }

  portrait.addEventListener('click', releaseCat);
  portrait.addEventListener('keydown', event => {
    if ((event.key === 'Enter' || event.key === ' ') && state === 'fused') {
      event.preventDefault();
      releaseCat();
    }
  });

  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || state === 'sleeping') return;
    cancelCurrentAction();
    clearFusionTarget();
    portraitWrap.classList.remove('fused');
    cat.hidden = false;
    finishHome();
    cat.focus({ preventScroll: true });
  });

  window.addEventListener('resize', () => {
    if (state === 'sleeping') finishHome();
  }, { passive: true });

  cat.classList.add('sleeping');
  cat.style.setProperty('--cat-x', `${HOME_X}px`);
})();
