import './style.css'
import * as THREE from 'three'
import { glassFragment, glassVertex } from './shaders'
import { COVERS, coverUrl, type CoverMeta } from './cardTexture'

const COLS = 16
const ROWS = 12
const CELL_W = 0.78
const CELL_H = 1.12
const GAP = 0.07
const PLANE_W = 0.72
const PLANE_H = 1.08
const SPHERE_R = 20
// Fractional half so slot 0..N-1 maps to a symmetric span (e.g. COLS=14 → -6.5..+6.5).
// Math.floor(N/2) left an extra column on the left and a gap on the right.
const HALF_COLS = (COLS - 1) / 2
const HALF_ROWS = (ROWS - 1) / 2

type Card = {
  mesh: THREE.Mesh
  material: THREE.ShaderMaterial
  slotX: number
  slotY: number
  coverIndex: number
}

function placeOnShallowSphere(out: THREE.Object3D, x: number, y: number) {
  const theta = x / SPHERE_R
  const phi = y / SPHERE_R
  const px = Math.sin(theta) * SPHERE_R
  const pz = Math.cos(theta) * Math.cos(phi) * SPHERE_R - SPHERE_R
  const py = Math.sin(phi) * SPHERE_R
  out.position.set(px, py, pz)
  out.lookAt(px * 2, py * 2, pz * 2 + SPHERE_R)
}

function createGlassMaterial(map: THREE.Texture): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      uMap: { value: map },
      uTint: { value: new THREE.Color('#ffffff') },
      uRimColor: { value: new THREE.Color('#a5e4ff') },
      uRimColorTop: { value: new THREE.Color('#ffffff') },
      uCornerRadius: { value: 0.08 },
      uBevelWidth: { value: 0.1 },
      uBevelPower: { value: 2.2 },
      uThickness: { value: 0.12 },
      uFresnelF0: { value: 0.04 },
      uEnvIntensity: { value: 0.28 },
      uRimWidth: { value: 0.02 },
      uRimIntensity: { value: 0.18 },
      uExposure: { value: 1.12 },
      uTime: { value: 0 },
      uPlaneSize: { value: new THREE.Vector2(PLANE_W, PLANE_H) },
    },
    vertexShader: glassVertex,
    fragmentShader: glassFragment,
    transparent: true,
    depthWrite: false,
    side: THREE.FrontSide,
  })
}

async function loadCoverTextures(renderer: THREE.WebGLRenderer): Promise<THREE.Texture[]> {
  const loader = new THREE.TextureLoader()
  const maxAniso = Math.min(8, renderer.capabilities.getMaxAnisotropy())
  return Promise.all(
    COVERS.map(
      (c) =>
        new Promise<THREE.Texture>((resolve, reject) => {
          loader.load(
            coverUrl(c.file),
            (tex) => {
              tex.colorSpace = THREE.SRGBColorSpace
              tex.anisotropy = maxAniso
              tex.minFilter = THREE.LinearMipmapLinearFilter
              tex.magFilter = THREE.LinearFilter
              tex.generateMipmaps = true
              tex.needsUpdate = true
              resolve(tex)
            },
            undefined,
            reject,
          )
        }),
    ),
  )
}

function wrapIndex(i: number, n: number): number {
  return ((i % n) + n) % n
}

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3)
}

function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2
}

async function main() {
  const canvas = document.querySelector<HTMLCanvasElement>('#c')!
  const fallback = document.querySelector<HTMLDivElement>('#fallback')!
  const backendEl = document.querySelector<HTMLElement>('#backend')!
  const hudTitle = document.querySelector<HTMLElement>('#hud h1')!
  const hudTip = document.querySelector<HTMLElement>('#hud p')!
  const focusEl = document.querySelector<HTMLDivElement>('#focus')!
  const focusTitle = document.querySelector<HTMLElement>('#focus-title')!
  const focusEn = document.querySelector<HTMLElement>('#focus-en')!
  const focusTags = document.querySelector<HTMLElement>('#focus-tags')!
  const focusMeta = document.querySelector<HTMLElement>('#focus-meta')!
  const focusReview = document.querySelector<HTMLElement>('#focus-review')!
  const focusYear = document.querySelector<HTMLElement>('#focus-year')!
  const focusBlurb = document.querySelector<HTMLElement>('#focus-blurb')!
  const focusClose = document.querySelector<HTMLButtonElement>('#focus-close')!

  let renderer: THREE.WebGLRenderer
  try {
    renderer = new THREE.WebGLRenderer({
      canvas, antialias: true, alpha: false,
      powerPreference: 'high-performance', preserveDrawingBuffer: true,
    })
  } catch { fallback.hidden = false; return }
  if (!renderer.getContext()) { fallback.hidden = false; return }

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
  renderer.setSize(window.innerWidth, window.innerHeight, false)
  renderer.setClearColor(0x1a2030, 1)
  renderer.outputColorSpace = THREE.SRGBColorSpace

  hudTitle.textContent = '游戏封面球'
  hudTip.textContent = '拖动无限浏览 · 点击飞出'
  backendEl.textContent = 'WebGL · 一百五十款 · 浅弧墙'

  let coverTextures: THREE.Texture[]
  try { coverTextures = await loadCoverTextures(renderer) }
  catch (err) { console.error(err); backendEl.textContent = '封面加载失败'; return }
  ;(window as unknown as { __coverReady?: boolean }).__coverReady = true

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 200)
  camera.position.set(0, 0.05, 6.8)

  const geometry = new THREE.PlaneGeometry(PLANE_W, PLANE_H, 1, 1)
  const cards: Card[] = []
  const strideX = CELL_W + GAP
  const strideY = CELL_H + GAP
  const nCovers = coverTextures.length

  for (let slotY = 0; slotY < ROWS; slotY++) {
    for (let slotX = 0; slotX < COLS; slotX++) {
      const idx = slotY * COLS + slotX
      const coverIndex = idx % nCovers
      const material = createGlassMaterial(coverTextures[coverIndex])
      const mesh = new THREE.Mesh(geometry, material)
      mesh.renderOrder = 1
      mesh.userData.cardIndex = idx
      scene.add(mesh)
      cards.push({ mesh, material, slotX, slotY, coverIndex })
    }
  }

  const bgMat = new THREE.ShaderMaterial({
    depthWrite: false,
    uniforms: { uTime: { value: 0 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }',
    fragmentShader: 'varying vec2 vUv; uniform float uTime; void main(){ vec2 p=vUv*2.0-1.0; float d=length(p); vec3 c=mix(vec3(0.24,0.28,0.38), vec3(0.12,0.14,0.20), smoothstep(0.1,1.2,d)); gl_FragColor=vec4(c,1.0); }',
  })
  const bg = new THREE.Mesh(new THREE.PlaneGeometry(60, 36), bgMat)
  bg.position.z = -6
  scene.add(bg)

  const offset = new THREE.Vector2(0, 0)
  const velocity = new THREE.Vector2(0, 0)
  const pointer = new THREE.Vector2()
  const ndc = new THREE.Vector2()
  const raycaster = new THREE.Raycaster()
  let dragging = false
  let moved = false
  let lastX = 0
  let lastY = 0
  let lastT = performance.now()

  type FocusState = {
    card: Card
    cover: CoverMeta
    fromPos: THREE.Vector3
    fromQuat: THREE.Quaternion
    fromScale: THREE.Vector3
    homeCellX: number
    homeCellY: number
  }
  let focused: FocusState | null = null
  let focusT = 0
  let focusDir = 0 // 1 = fly out, -1 = fly back
  const focusPos = new THREE.Vector3(-0.95, 0.12, 3.55)
  const focusScale = new THREE.Vector3(1.82, 1.82, 1.82)
  const focusQuat = new THREE.Quaternion()
  const tmpPos = new THREE.Vector3()
  const tmpScale = new THREE.Vector3()
  const tmpQuat = new THREE.Quaternion()
  const homeScale = new THREE.Vector3(1, 1, 1)

  const focusCardEl = document.querySelector<HTMLElement>('.focus-card')!
  const proj = new THREE.Vector3()
  const GAP_PX = 14

  function hideDuplicateCovers(active: Card | null) {
    const keepIdx = active ? active.coverIndex : -1
    for (const c of cards) {
      if (active && c === active) {
        c.mesh.visible = true
        continue
      }
      if (active && c.coverIndex === keepIdx) {
        c.mesh.visible = false
      } else {
        c.mesh.visible = true
      }
    }
  }

  function positionInfoBesideCover(mesh: THREE.Mesh) {
    if (!focusCardEl) return
    mesh.updateMatrixWorld(true)
    const halfW = PLANE_W / 2
    const halfH = PLANE_H / 2
    // Right-middle and bottom-middle in local plane space
    const rightMid = new THREE.Vector3(halfW, 0, 0).applyMatrix4(mesh.matrixWorld)
    const bottomMid = new THREE.Vector3(0, -halfH, 0).applyMatrix4(mesh.matrixWorld)
    const topMid = new THREE.Vector3(0, halfH, 0).applyMatrix4(mesh.matrixWorld)
    const leftMid = new THREE.Vector3(-halfW, 0, 0).applyMatrix4(mesh.matrixWorld)

    const toScreen = (v: THREE.Vector3) => {
      proj.copy(v).project(camera)
      return {
        x: (proj.x * 0.5 + 0.5) * window.innerWidth,
        y: (-proj.y * 0.5 + 0.5) * window.innerHeight,
      }
    }
    const R = toScreen(rightMid)
    const B = toScreen(bottomMid)
    const T = toScreen(topMid)
    const L = toScreen(leftMid)
    const panel = focusCardEl
    const narrow = window.innerWidth < 800
    const coverTop = Math.min(T.y, B.y)
    const coverBot = Math.max(T.y, B.y)
    const coverH = Math.max(0, Math.round(coverBot) - Math.round(coverTop))

    const releaseHeight = () => {
      panel.style.height = ''
      panel.style.minHeight = ''
    }

    let left: number
    let top: number
    let pw = panel.offsetWidth || 360
    let ph = panel.offsetHeight || 200

    if (narrow) {
      releaseHeight()
      ph = panel.offsetHeight || 200
      pw = panel.offsetWidth || 360
      left = (L.x + R.x) / 2 - pw / 2
      top = B.y + GAP_PX
    } else {
      left = R.x + GAP_PX
      // If would overflow right, flip below and size to content
      if (left + pw > window.innerWidth - 16) {
        releaseHeight()
        ph = panel.offsetHeight || 200
        pw = panel.offsetWidth || 360
        left = (L.x + R.x) / 2 - pw / 2
        top = B.y + GAP_PX
      } else if (coverH > 0) {
        panel.style.height = `${coverH}px`
        panel.style.minHeight = `${coverH}px`
        pw = panel.offsetWidth || pw
        ph = coverH
        left = R.x + GAP_PX
        top = Math.round(coverTop)
      } else {
        top = (T.y + B.y) / 2 - ph / 2
      }
    }
    left = Math.max(12, Math.min(left, window.innerWidth - pw - 12))
    const heightLocked = panel.style.height !== ''
    if (!heightLocked) {
      top = Math.max(12, Math.min(top, window.innerHeight - ph - 12))
    }
    panel.style.left = `${Math.round(left)}px`
    panel.style.top = `${Math.round(top)}px`
  }

  function cellForCard(card: Card) {
    const centerIx = Math.round(-offset.x / strideX)
    const centerIy = Math.round(-offset.y / strideY)
    return {
      cellX: centerIx + card.slotX - HALF_COLS,
      cellY: centerIy + card.slotY - HALF_ROWS,
    }
  }

  function updateWall() {
    const centerIx = Math.round(-offset.x / strideX)
    const centerIy = Math.round(-offset.y / strideY)
    for (const card of cards) {
      if (focused && focused.card === card) continue
      const cellX = centerIx + card.slotX - HALF_COLS
      const cellY = centerIy + card.slotY - HALF_ROWS
      placeOnShallowSphere(card.mesh, cellX * strideX + offset.x, cellY * strideY + offset.y)
      const coverIndex = wrapIndex(cellX + cellY * 17, nCovers)
      if (card.coverIndex !== coverIndex) {
        card.coverIndex = coverIndex
        card.material.uniforms.uMap.value = coverTextures[coverIndex]
      }
      card.mesh.scale.copy(homeScale)
      card.mesh.renderOrder = 1
    }
  }

  function fillSteam(cover: CoverMeta) {
    const tags = (cover.tags ?? []).slice(0, 4)
    focusTags.replaceChildren()
    if (tags.length) {
      for (const tag of tags) {
        const chip = document.createElement('span')
        chip.textContent = tag
        focusTags.appendChild(chip)
      }
      focusTags.hidden = false
    } else {
      focusTags.hidden = true
    }

    if (cover.review && cover.reviewCount) {
      const count = cover.reviewCount.toLocaleString('zh-CN')
      focusReview.textContent = `${cover.review} · ${count} 篇`
      focusReview.hidden = false
    } else {
      focusReview.textContent = ''
      focusReview.hidden = true
    }

    if (cover.year) {
      focusYear.textContent = String(cover.year)
      focusYear.hidden = false
    } else {
      focusYear.textContent = ''
      focusYear.hidden = true
    }
    focusMeta.hidden = focusReview.hidden && focusYear.hidden
  }

  function openFocus(card: Card) {
    if (focused) return
    const cover = COVERS[card.coverIndex]
    const { cellX, cellY } = cellForCard(card)
    // Snapshot current wall pose ? single 3D cover flies forward (no DOM image)
    focused = {
      card,
      cover,
      fromPos: card.mesh.position.clone(),
      fromQuat: card.mesh.quaternion.clone(),
      fromScale: card.mesh.scale.clone(),
      homeCellX: cellX,
      homeCellY: cellY,
    }
    focusDir = 1
    focusT = 0
    card.mesh.renderOrder = 30
    card.mesh.visible = true
    card.material.depthWrite = true
    hideDuplicateCovers(card)
    focusTitle.textContent = cover.titleZh
    if (focusEn) focusEn.textContent = cover.titleEn
    focusBlurb.textContent = cover.blurb
    fillSteam(cover)
    // retrigger unified entrance
    const cardEl = document.querySelector<HTMLElement>('.focus-card')
    if (cardEl) {
      cardEl.style.animation = 'none'
      void cardEl.offsetWidth
      cardEl.style.animation = ''
    }
    focusEl.hidden = false
    focusEl.classList.add('show')
    document.body.classList.add('focus-open')
  }

  function closeFocus() {
    if (!focused || focusDir < 0) return
    // Recapture start as current (may be mid-flight)
    focused.fromPos.copy(focused.card.mesh.position)
    focused.fromQuat.copy(focused.card.mesh.quaternion)
    focused.fromScale.copy(focused.card.mesh.scale)
    // Target home on wall for current offset
    const x = focused.homeCellX * strideX + offset.x
    const y = focused.homeCellY * strideY + offset.y
    const home = new THREE.Object3D()
    placeOnShallowSphere(home, x, y)
    // Store home into from* as destination via swapping in frame using focusDir -1
    // Reuse focusPos/scale/quat as 'to' when flying out; when flying back, lerp to home
    ;(focused as FocusState & { backPos?: THREE.Vector3; backQuat?: THREE.Quaternion }).backPos = home.position.clone()
    ;(focused as FocusState & { backQuat?: THREE.Quaternion }).backQuat = home.quaternion.clone()
    focusDir = -1
    focusT = 0
    focusEl.classList.remove('show')
    document.body.classList.remove('focus-open')
  }

  function pickCard(clientX: number, clientY: number): Card | null {
    ndc.x = (clientX / window.innerWidth) * 2 - 1
    ndc.y = -(clientY / window.innerHeight) * 2 + 1
    raycaster.setFromCamera(ndc, camera)
    const hits = raycaster.intersectObjects(
      cards.filter((c) => c.mesh.visible).map((c) => c.mesh),
      false,
    )
    if (!hits.length) return null
    const idx = hits[0].object.userData.cardIndex as number
    return cards[idx] ?? null
  }

  function onPointerDown(e: PointerEvent) {
    dragging = true
    moved = false
    lastX = e.clientX
    lastY = e.clientY
    lastT = performance.now()
    velocity.set(0, 0)
    canvas.setPointerCapture(e.pointerId)
  }

  function onPointerMove(e: PointerEvent) {
    pointer.x = (e.clientX / window.innerWidth) * 2 - 1
    pointer.y = -(e.clientY / window.innerHeight) * 2 + 1
    if (!dragging || focused) return
    const now = performance.now()
    const dt = Math.max((now - lastT) / 1000, 1 / 120)
    const dx = (e.clientX - lastX) / window.innerWidth
    const dy = (e.clientY - lastY) / window.innerHeight
    if (Math.abs(dx) + Math.abs(dy) > 0.003) moved = true
    offset.x += dx * 7.0
    offset.y -= dy * 7.0
    velocity.x = (dx * 7.0) / dt
    velocity.y = (-dy * 7.0) / dt
    lastX = e.clientX
    lastY = e.clientY
    lastT = now
  }

  function onPointerUp(e: PointerEvent) {
    dragging = false
    try { canvas.releasePointerCapture(e.pointerId) } catch { /* ignore */ }
    if (moved) return
    if (focused) {
      // Click empty / other ? fly back (panel also closes)
      closeFocus()
      return
    }
    const hit = pickCard(e.clientX, e.clientY)
    if (hit) openFocus(hit)
  }

  canvas.addEventListener('pointerdown', onPointerDown)
  canvas.addEventListener('pointermove', onPointerMove)
  canvas.addEventListener('pointerup', onPointerUp)
  canvas.addEventListener('pointercancel', onPointerUp)
  canvas.addEventListener('wheel', (e) => {
    if (focused) return
    e.preventDefault()
    offset.x -= e.deltaX * 0.004
    offset.y += e.deltaY * 0.004
    velocity.multiplyScalar(0.4)
  }, { passive: false })

  focusClose.addEventListener('click', (e) => { e.stopPropagation(); closeFocus() })
  focusEl.addEventListener('click', (e) => { if (e.target === focusEl) closeFocus() })
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeFocus() })

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
    renderer.setSize(window.innerWidth, window.innerHeight, false)
  })

  ;(window as unknown as { __openCoverById?: (id: string) => void }).__openCoverById = (id: string) => {
    const hit = cards.find((c) => COVERS[c.coverIndex]?.id === id)
    if (hit) openFocus(hit)
  }

  const clock = new THREE.Clock()
  let idlePhase = 0

  function frame() {
    const dt = Math.min(clock.getDelta(), 0.05)
    const t = clock.elapsedTime

    if (!focused && !dragging) {
      velocity.multiplyScalar(Math.exp(-2.8 * dt))
      offset.x += velocity.x * dt
      offset.y += velocity.y * dt
      idlePhase += dt
      offset.x += Math.sin(idlePhase * 0.14) * 0.002
    }

    updateWall()

    if (focused) {
      focusT = Math.min(1, focusT + dt * 2.8)
      const k = focusDir > 0 ? easeOutCubic(focusT) : easeInOutCubic(focusT)
      const card = focused.card
      const ext = focused as FocusState & { backPos?: THREE.Vector3; backQuat?: THREE.Quaternion }
      if (focusDir > 0) {
        tmpPos.copy(focused.fromPos).lerp(focusPos, k)
        tmpScale.copy(focused.fromScale).lerp(focusScale, k)
        tmpQuat.copy(focused.fromQuat).slerp(focusQuat, k)
      } else {
        const backPos = ext.backPos ?? focused.fromPos
        const backQuat = ext.backQuat ?? focused.fromQuat
        tmpPos.copy(focused.fromPos).lerp(backPos, k)
        tmpScale.copy(focused.fromScale).lerp(homeScale, k)
        tmpQuat.copy(focused.fromQuat).slerp(backQuat, k)
      }
      card.mesh.position.copy(tmpPos)
      card.mesh.scale.copy(tmpScale)
      card.mesh.quaternion.copy(tmpQuat)
      card.mesh.renderOrder = 30
      card.mesh.visible = true
      card.material.depthWrite = true
      card.material.uniforms.uExposure.value = 1.18
      hideDuplicateCovers(card)
      positionInfoBesideCover(card.mesh)

      // Dim + slight shrink others (duplicates already invisible)
      const wallDim = focusDir > 0 ? 0.48 + 0.52 * (1 - k) : 0.48 + 0.52 * k
      for (const c of cards) {
        if (c === card) continue
        c.material.uniforms.uExposure.value = 1.12 * wallDim
        const s = focusDir > 0 ? 1 - 0.05 * k : 0.95 + 0.05 * k
        if (c.mesh.visible) c.mesh.scale.setScalar(s)
      }

      if (focusDir < 0 && focusT >= 1) {
        card.mesh.renderOrder = 1
        card.mesh.scale.copy(homeScale)
        card.material.depthWrite = false
        for (const c of cards) {
          c.material.uniforms.uExposure.value = 1.12
          c.mesh.scale.copy(homeScale)
          c.mesh.visible = true
        }
        focused = null
        focusDir = 0
        focusCardEl.style.height = ''
        focusCardEl.style.minHeight = ''
        focusEl.hidden = true
        hideDuplicateCovers(null)
        updateWall()
      }
    }

    for (const card of cards) card.material.uniforms.uTime.value = t

    if (!focused) {
      camera.position.x += (pointer.x * 0.3 - camera.position.x) * 0.06
      camera.position.y += (0.05 + pointer.y * 0.18 - camera.position.y) * 0.06
    } else {
      camera.position.x += (0 - camera.position.x) * 0.08
      camera.position.y += (0.05 - camera.position.y) * 0.08
    }
    camera.lookAt(0, 0, -0.5)

    bgMat.uniforms.uTime.value = t
    renderer.render(scene, camera)
    requestAnimationFrame(frame)
  }

  updateWall()
  requestAnimationFrame(frame)
}

main()
