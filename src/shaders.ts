/** Clear glass plate: single sharp cover sample + edge fresnel/rim (no refractive ghosting). */
export const glassVertex = /* glsl */ `
varying vec2 vUv;
varying vec3 vViewDir;

void main() {
  vUv = uv;
  vec4 world = modelMatrix * vec4(position, 1.0);
  vViewDir = normalize(cameraPosition - world.xyz);
  gl_Position = projectionMatrix * viewMatrix * world;
}
`

export const glassFragment = /* glsl */ `
precision highp float;

uniform sampler2D uMap;
uniform vec3 uTint;
uniform vec3 uRimColor;
uniform vec3 uRimColorTop;
uniform float uCornerRadius;
uniform float uBevelWidth;
uniform float uBevelPower;
uniform float uThickness;
uniform float uFresnelF0;
uniform float uEnvIntensity;
uniform float uRimWidth;
uniform float uRimIntensity;
uniform float uExposure;
uniform float uTime;
uniform vec2 uPlaneSize;

varying vec2 vUv;
varying vec3 vViewDir;

float roundedBoxSDF(vec2 p, vec2 halfSize, float radius) {
  radius = min(radius, min(halfSize.x, halfSize.y));
  vec2 q = abs(p) - halfSize + radius;
  return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - radius;
}

float bevelHeight(float dist) {
  float edge = clamp(1.0 + dist / max(uBevelWidth, 0.001), 0.0, 1.0);
  float power = max(uBevelPower, 1.0);
  float profile = pow(max(1.0 - pow(edge, power), 0.0), 1.0 / power);
  return profile * uThickness;
}

void main() {
  vec2 halfSize = uPlaneSize * 0.5;
  vec2 local = (vUv - 0.5) * uPlaneSize;
  float dist = roundedBoxSDF(local, halfSize, uCornerRadius);
  if (dist > 0.002) discard;

  // Sharp cover ? one sample only (no chromatic / refract offset)
  vec3 cover = texture2D(uMap, vUv).rgb * uTint * uExposure;

  // Fake bevel normal only for rim/fresnel lighting, NOT for sampling the map
  float eps = 0.0015 * max(uPlaneSize.x, uPlaneSize.y);
  float hC = bevelHeight(dist);
  float hX = bevelHeight(roundedBoxSDF(local + vec2(eps, 0.0), halfSize, uCornerRadius));
  float hY = bevelHeight(roundedBoxSDF(local + vec2(0.0, eps), halfSize, uCornerRadius));
  vec3 normal = normalize(vec3((hC - hX) / eps, (hC - hY) / eps, 1.0));
  vec3 viewDir = normalize(vViewDir);

  float NdV = clamp(dot(normal, viewDir), 0.0, 1.0);
  float fresnel = uFresnelF0 + (1.0 - uFresnelF0) * pow(1.0 - NdV, 5.0);

  float rim = smoothstep(-uRimWidth, 0.0, dist) * uRimIntensity;
  float rimGrad = clamp((local.y / max(halfSize.y, 0.001)) * 0.5 + 0.5, 0.0, 1.0);
  vec3 rimColor = mix(uRimColor, uRimColorTop, rimGrad);

  // Light glass wash on edges only ? keep artwork crisp in the center
  float edgeGlass = clamp(fresnel * uEnvIntensity, 0.0, 0.22);
  vec3 glassWash = vec3(0.78, 0.86, 0.98);
  vec3 finished = mix(cover, cover * 0.92 + glassWash * 0.08, edgeGlass);
  finished += rimColor * rim;

  float alpha = 1.0 - smoothstep(0.0, 0.0018, dist);
  gl_FragColor = vec4(finished, alpha);
}
`
