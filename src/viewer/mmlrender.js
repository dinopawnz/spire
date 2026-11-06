// Draws the live MML DOM of spire.html (after LIVE BUILD) with three.js.
// m-group / m-model / m-image / m-cube / m-sphere / m-label, honouring x y z rx ry rz sx sy sz, visible, visible-to, emissive, opacity.
// Otherside has no m-light here: light = soft sky light + emissive materials + bloom.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const DEG = Math.PI / 180;
const num = (n, a, d) => { const v = n.getAttribute(a); if (v === null || v === '') return d; const f = parseFloat(v); return isNaN(f) ? d : f; };

export async function setup(opt) {
  const MAP = opt.map, VIEWER = String(opt.viewer);
  const W = opt.w || 1280, H = opt.h || 720;
  const r = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  r.setSize(W, H); r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = opt.exposure || 1.0;
  r.outputColorSpace = THREE.SRGBColorSpace;
  r.domElement.style.cssText = 'position:fixed;left:0;top:0;z-index:99999';
  document.body.appendChild(r.domElement);
  const scene = new THREE.Scene();
  const sky = new THREE.Color(opt.sky || 0x0d1218); scene.background = sky; scene.fog = new THREE.Fog(sky, opt.fogNear || 150, opt.fogFar || 700);
  const pm = new THREE.PMREMGenerator(r); scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; scene.environmentIntensity = opt.env ?? 0.35;
  scene.add(new THREE.HemisphereLight(0x8090a8, 0x2a2216, opt.hemi ?? 0.7));
  const sun = new THREE.DirectionalLight(0x9aa8c8, opt.sun ?? 0.5); sun.position.set(60, 120, 80); scene.add(sun);

  const resolve = (src) => {
    const u = String(src || '').split('?')[0];
    const m = u.match(/raw\.githubusercontent\.com\/dinopawnz\/([^/]+)\/[^/]+\/(.*)$/);
    if (!m) return u;
    const key = m[1] + '/' + m[2];
    return MAP[key] || null;
  };
  const loader = new GLTFLoader(); const gcache = new Map(); const tcache = new Map();
  const loadG = (url) => { if (!gcache.has(url)) gcache.set(url, new Promise((res) => loader.load(url, (g) => res(g), undefined, (e) => { console.log('ERR ' + url + ' ' + e); res(null); }))); return gcache.get(url); };
  const texL = new THREE.TextureLoader();
  const loadT = (url) => { if (!tcache.has(url)) tcache.set(url, new Promise((res) => texL.load(url, (t) => { t.colorSpace = THREE.SRGBColorSpace; res(t); }, undefined, () => { console.log('ERR tex ' + url); res(null); }))); return tcache.get(url); };

  const visibleTo = (n) => { const v = n.getAttribute('visible-to'); if (v === null) return true; return v.split(/\s+/).includes(VIEWER); };
  const pending = []; let tris = 0, count = 0, missing = new Set();
  function xform(o, n) {
    o.position.set(num(n, 'x', 0), num(n, 'y', 0), num(n, 'z', 0));
    o.rotation.set(num(n, 'rx', 0) * DEG, num(n, 'ry', 0) * DEG, num(n, 'rz', 0) * DEG);
    o.scale.set(num(n, 'sx', 1), num(n, 'sy', 1), num(n, 'sz', 1));
  }
  function colorMat(n, def) {
    const c = new THREE.Color(n.getAttribute('color') || def || '#ffffff');
    const op = num(n, 'opacity', 1), em = num(n, 'emissive', 0);
    return new THREE.MeshStandardMaterial({ color: c, emissive: em > 0 ? c : 0x000000, emissiveIntensity: em, transparent: op < 1, opacity: op, roughness: 0.8 });
  }
  function walk(n, parent) {
    const tag = n.tagName.toLowerCase();
    if (!tag.startsWith('m-')) { for (const c of n.children) walk(c, parent); return; }
    if (n.getAttribute('visible') === 'false' || !visibleTo(n)) return;
    if (opt.skip && opt.skip.some((s) => (n.getAttribute('src') || '').includes(s))) return;
    const o = new THREE.Group(); xform(o, n); parent.add(o);
    if (tag === 'm-model') {
      const url = resolve(n.getAttribute('src'));
      if (!url) missing.add(n.getAttribute('src'));
      else pending.push(loadG(url).then((g) => {
        if (!g) return; const animd = n.getAttribute('anim') && g.animations && g.animations.length;
        const c = animd ? SkeletonUtils.clone(g.scene) : g.scene.clone(true);
        if (animd) { const mx = new THREE.AnimationMixer(c); mx.clipAction(g.animations[0]).play(); mx.update(opt.animT ?? 6.8); c.updateMatrixWorld(true); }
        c.traverse((m) => { if (m.isMesh) { m.frustumCulled = false; if (m.material && m.material.name === 'col') m.visible = false; else tris += m.geometry.index ? m.geometry.index.count / 3 : m.geometry.attributes.position.count / 3; } });
        o.add(c); count++;
      }));
    } else if (tag === 'm-image') {
      const url = resolve(n.getAttribute('src'));
      if (!url) missing.add(n.getAttribute('src'));
      else pending.push(loadT(url).then((t) => {
        if (!t) return; const iw = t.image.width, ih = t.image.height;
        let w = num(n, 'width', NaN), h = num(n, 'height', NaN);
        if (isNaN(w) && isNaN(h)) { w = 1; h = ih / iw; } else if (isNaN(w)) w = h * iw / ih; else if (isNaN(h)) h = w * ih / iw;
        const em = num(n, 'emissive', 0), op = num(n, 'opacity', 1);
        const mat = new THREE.MeshStandardMaterial({ map: t, transparent: true, opacity: op, side: THREE.DoubleSide, emissive: 0xffffff, emissiveMap: t, emissiveIntensity: em, depthWrite: op >= 0.99, alphaTest: 0.02, roughness: 0.9 });
        o.add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat)); count++;
      }));
    } else if (tag === 'm-cube') {
      o.add(new THREE.Mesh(new THREE.BoxGeometry(num(n, 'width', 1), num(n, 'height', 1), num(n, 'depth', 1)), colorMat(n)));
    } else if (tag === 'm-sphere') {
      const rad = num(n, 'radius', 0.5); o.add(new THREE.Mesh(new THREE.SphereGeometry(rad, 16, 12), colorMat(n)));
    } else if (tag === 'm-plane') {
      o.add(new THREE.Mesh(new THREE.PlaneGeometry(num(n, 'width', 1), num(n, 'height', 1)), colorMat(n)));
    } else if (tag === 'm-cylinder') {
      const rad = num(n, 'radius', 0.5); o.add(new THREE.Mesh(new THREE.CylinderGeometry(rad, rad, num(n, 'height', 1), 20), colorMat(n)));
    } else if (tag === 'm-label') {
      const w = num(n, 'width', 1), h = num(n, 'height', 1);
      const cv = document.createElement('canvas'); cv.width = Math.round(w * 128); cv.height = Math.round(h * 128);
      const g = cv.getContext('2d'); g.fillStyle = n.getAttribute('color') || '#fff'; g.fillRect(0, 0, cv.width, cv.height);
      g.fillStyle = n.getAttribute('font-color') || '#000'; g.font = (num(n, 'font-size', 24) * 2) + 'px sans-serif'; g.textAlign = 'center';
      String(n.getAttribute('content') || '').split('\n').forEach((l, i) => g.fillText(l, cv.width / 2, 60 + i * num(n, 'font-size', 24) * 2.4));
      const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
      o.add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ map: t, emissive: 0xffffff, emissiveMap: t, emissiveIntensity: num(n, 'emissive', 0) })));
    }
    for (const c of n.children) walk(c, o);
  }
  const root = document.getElementById('root');
  const top = new THREE.Group(); scene.add(top); walk(root, top);
  await Promise.all(pending);

  const cam = new THREE.PerspectiveCamera(50, W / H, 0.05, 3000);
  const composer = new EffectComposer(r);
  composer.addPass(new RenderPass(scene, cam));
  const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), opt.bloom ?? 0.55, 0.5, opt.bloomThreshold ?? 0.85);
  composer.addPass(bloom); composer.addPass(new OutputPass());
  window.__shoot = (c) => {
    // c.cam / c.at are in BUILDING coordinates (as in the layouts); the world group sits at z = -FRONT
    const off = opt.worldZ || 0;
    cam.fov = c.fov || 60; cam.updateProjectionMatrix();
    cam.position.set(c.cam[0], c.cam[1], c.cam[2] + off); cam.lookAt(c.at[0], c.at[1], c.at[2] + off);
    if (c.exposure) r.toneMappingExposure = c.exposure;
    composer.render();
    return true;
  };
  window.__stats = { tris: Math.round(tris), count, missing: Array.from(missing).slice(0, 20), nmissing: missing.size };
  window.__ready = true;
}
