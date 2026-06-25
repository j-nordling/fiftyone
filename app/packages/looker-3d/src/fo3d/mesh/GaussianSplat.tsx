import { getSampleSrc } from "@fiftyone/state";
import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef, useState } from "react";
import { Group, type Quaternion, type Vector3, type WebGLRenderer, type Scene } from "three";
import type { GaussianSplatAsset } from "../render-types";
import { getResolvedUrlForFo3dAsset } from "../utils";
import { useFo3dContext } from "../context";

// Lazy-load Spark runtime once per page.
let _sparkPromise: Promise<unknown> | null = null;
const ensureSparkRuntime = () => {
  if (!_sparkPromise) {
    _sparkPromise = import("@sparkjsdev/spark").catch((err) => {
      _sparkPromise = null;
      throw err;
    });
  }
  return _sparkPromise as Promise<{ SparkRenderer: any; SplatMesh: any }>;
};

// One SparkRenderer per WebGL context.
const _sparkRenderers = new WeakMap<WebGLRenderer, any>();

const getOrCreateSparkRenderer = (
  gl: WebGLRenderer,
  scene: Scene,
  SparkRenderer: any
): any => {
  if (!_sparkRenderers.has(gl)) {
    const spark = new SparkRenderer({ renderer: gl });
    spark.frustumCulled = false;
    scene.add(spark);
    _sparkRenderers.set(gl, spark);
  }
  return _sparkRenderers.get(gl);
};

export const GaussianSplat = ({
  name,
  asset,
  position,
  quaternion,
  scale,
  children,
}: {
  name: string;
  asset: GaussianSplatAsset;
  position: Vector3;
  quaternion: Quaternion;
  scale: Vector3;
  children?: React.ReactNode;
}) => {
  const { fo3dRoot } = useFo3dContext();
  const { gl, scene, camera } = useThree();

  const resolvedUrl = useMemo(
    () => getSampleSrc(getResolvedUrlForFo3dAsset(asset.plyPath, fo3dRoot)),
    [asset.plyPath, fo3dRoot]
  );

  // container holds the SplatMesh and carries the node's transforms
  const [container, setContainer] = useState<Group | null>(null);
  const sparkRef = useRef<any>(null);

  useEffect(() => {
    let group: Group | null = null;
    let cancelled = false;

    (async () => {
      try {
        const { SparkRenderer, SplatMesh } = await ensureSparkRuntime();
        if (cancelled) return;

        const spark = getOrCreateSparkRenderer(gl, scene, SparkRenderer);
        sparkRef.current = spark;

        const mesh = new SplatMesh({ url: resolvedUrl });
        mesh.name = name;

        group = new Group();
        group.position.copy(position);
        group.quaternion.copy(quaternion);
        group.scale.copy(scale);
        group.add(mesh);
        scene.add(group);

        if (!cancelled) {
          setContainer(group);
        }
      } catch (err) {
        console.error("[GaussianSplat] Failed to load splat:", err);
      }
    })();

    return () => {
      cancelled = true;
      if (group) {
        scene.remove(group);
      }
      setContainer(null);
    };
  }, [resolvedUrl, name, gl, scene, position, quaternion, scale]);

  // Drive SparkRenderer's update each frame.
  useFrame(() => {
    if (sparkRef.current) {
      sparkRef.current.update({ scene, camera });
    }
  });

  if (!container) {
    return null;
  }

  // Render children (nested scene nodes) in a group at the same transform.
  if (!children) {
    return null;
  }

  return (
    <group position={position} quaternion={quaternion} scale={scale}>
      {children}
    </group>
  );
};
