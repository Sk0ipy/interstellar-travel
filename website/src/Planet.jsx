import { useEffect, useMemo } from 'react'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'

const PLANET_RADIUS = 4.5
const HOTSPOT_HITBOX = 'SECRET_HOTSPOT_HITBOX'

// Soft blue glow around the planet (replaces the render-only Blender atmosphere).
function Atmosphere() {
  const material = useMemo(
    () =>
      new THREE.ShaderMaterial({
        transparent: true,
        side: THREE.BackSide,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        vertexShader: `
          varying vec3 vNormal;
          void main() {
            vNormal = normalize(normalMatrix * normal);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }`,
        fragmentShader: `
          varying vec3 vNormal;
          void main() {
            float intensity = pow(clamp(0.55 + dot(vNormal, vec3(0.0, 0.0, 1.0)), 0.0, 1.0), 4.0);
            gl_FragColor = vec4(0.12, 0.45, 1.0, 1.0) * intensity * 0.55;
          }`,
      }),
    [],
  )
  return (
    <mesh scale={PLANET_RADIUS * 1.14} material={material}>
      <sphereGeometry args={[1, 64, 64]} />
    </mesh>
  )
}

export default function Planet({ onHotspotClick, onHotspotHover }) {
  const { scene } = useGLTF('/planet.glb')

  useEffect(() => {
    scene.traverse((obj) => {
      if (obj.isMesh && obj.name === 'Planet_Surface') {
        // The Blender material carries a flat emissive tint that washes out the
        // terrain colours; the biome colours live in the vertex colours.
        obj.material.emissive.set(0x000000)
        obj.material.vertexColors = true
        obj.material.needsUpdate = true
      }
      if (obj.isMesh && obj.name === HOTSPOT_HITBOX) {
        // Invisible but clickable: stays raycastable, draws nothing.
        obj.material = new THREE.MeshBasicMaterial({
          transparent: true,
          opacity: 0,
          depthWrite: false,
          colorWrite: false,
        })
      }
    })
  }, [scene])

  return (
    <group>
      <primitive
        object={scene}
        onClick={(e) => {
          if (e.object.name === HOTSPOT_HITBOX) {
            e.stopPropagation()
            onHotspotClick?.()
          }
        }}
        onPointerOver={(e) => {
          if (e.object.name === HOTSPOT_HITBOX) onHotspotHover?.(true)
        }}
        onPointerOut={(e) => {
          if (e.object.name === HOTSPOT_HITBOX) onHotspotHover?.(false)
        }}
      />
      <Atmosphere />
    </group>
  )
}

useGLTF.preload('/planet.glb')
