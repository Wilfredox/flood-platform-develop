/// <reference types="vite/client" />

declare const __DATASET_GEOJSON_ROUTE__: string

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
