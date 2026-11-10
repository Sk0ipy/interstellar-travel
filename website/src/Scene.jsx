import { Suspense, useEffect } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { OrbitControls, Stars, Html, useProgress } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import Planet from './Planet.jsx'

function Loader() {
  const { progress } = useProgress()
  return (
    <Html center>
      <div className="loader">Planeet laden… {Math.round(progress)}%</div>
    </Html>
  )
}

// On wide screens, shift the rendered image to the right so the planet sits next to the
// headline instead of behind it. Orbiting still happens around the planet centre.
function ShiftView() {
  const { camera, size } = useThree()
  useEffect(() => {
    const shift = size.width > 900 ? -size.width * 0.14 : 0
    camera.setViewOffset(size.width, size.height, shift, 0, size.width, size.height)
    camera.updateProjectionMatrix()
    return () => camera.clearViewOffset()
  }, [camera, size])
  return null
}

// Dev-only: expose the three.js state so the hotspot can be tested from the console.
function DevHook() {
  const state = useThree()
  useEffect(() => {
    if (import.meta.env.DEV) window.__three = state
  }, [state])
  return null
}

export default function Scene({ onHotspotClick, onHotspotHover, autoRotate }) {
  return (
    <Canvas
      camera={{ position: [0, 3, 15], fov: 45, near: 0.1, far: 200 }}
      dpr={[1, 2]}
      gl={{ antialias: true }}
    >
      <color attach="background" args={['#02040a']} />
      <ShiftView />
      <DevHook />
      <ambientLight intensity={1.0} color="#8fa8ff" />
      <directionalLight position={[8, 6, 6]} intensity={3.0} color="#ffffff" />
      <directionalLight position={[-8, -2, -6]} intensity={1.2} color="#3a78ff" />
      <Stars radius={90} depth={50} count={5000} factor={4} saturation={0} fade speed={0.6} />
      <Suspense fallback={<Loader />}>
        <Planet onHotspotClick={onHotspotClick} onHotspotHover={onHotspotHover} />
      </Suspense>
      <OrbitControls
        makeDefault
        enablePan={false}
        enableDamping
        dampingFactor={0.06}
        minDistance={6.5}
        maxDistance={20}
        rotateSpeed={0.7}
        autoRotate={autoRotate}
        autoRotateSpeed={0.5}
      />
      <EffectComposer multisampling={0}>
        <Bloom intensity={0.6} luminanceThreshold={0.9} luminanceSmoothing={0.2} mipmapBlur />
      </EffectComposer>
    </Canvas>
  )
}
