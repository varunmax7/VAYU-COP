/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** auto | online | offline — mirrors the backend's MAP_TILES (§13.4); the map fetches
   * tiles directly from CARTO in the browser, so it needs its own copy of this setting. */
  readonly VITE_MAP_TILES?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
