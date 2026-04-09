import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import fs from 'node:fs'
import path from 'node:path'

const DATASET_GEOJSON_ROUTE = '/dataset-geojson'
const DATASET_GEOJSON_DIR = path.resolve(__dirname, '../dataset/GeoJson')

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'serve-dataset-geojson',
      configureServer(server) {
        server.middlewares.use(DATASET_GEOJSON_ROUTE, (req, res, next) => {
          const rawPath = req.url || '/'
          const decodedPath = decodeURIComponent(rawPath).replace(/^\/+/, '')

          // Reject path traversal and nested segments.
          if (!decodedPath || decodedPath.includes('..') || decodedPath.includes('/')) {
            res.statusCode = 404
            res.end('Not Found')
            return
          }

          const fullPath = path.join(DATASET_GEOJSON_DIR, decodedPath)
          if (!fullPath.startsWith(DATASET_GEOJSON_DIR) || !fs.existsSync(fullPath) || !fs.statSync(fullPath).isFile()) {
            res.statusCode = 404
            res.end('Not Found')
            return
          }

          res.setHeader('Content-Type', 'application/geo+json; charset=utf-8')
          fs.createReadStream(fullPath).pipe(res)
        })
      }
    }
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0', // 允许局域网访问
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  },
  define: {
    __DATASET_GEOJSON_ROUTE__: JSON.stringify(DATASET_GEOJSON_ROUTE)
  }
})
