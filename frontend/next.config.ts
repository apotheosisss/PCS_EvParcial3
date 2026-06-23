import path from "node:path"
import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  // Fija la raíz del workspace a esta carpeta (hay otro lockfile en el home del usuario).
  turbopack: {
    root: path.resolve(import.meta.dirname),
  },
}

export default nextConfig
