import { create } from 'zustand'

export type ThemeMode = 'auto' | 'day' | 'night'
export type WsStatus = 'connecting' | 'connected' | 'disconnected'

const THEME_KEY = 'vayu.themeMode'

function loadThemeMode(): ThemeMode {
  try {
    const stored = localStorage.getItem(THEME_KEY)
    if (stored === 'auto' || stored === 'day' || stored === 'night') return stored
  } catch {
    // ignore — default to auto
  }
  return 'auto'
}

function persistThemeMode(mode: ThemeMode): void {
  try {
    localStorage.setItem(THEME_KEY, mode)
  } catch {
    // ignore
  }
}

interface UiState {
  themeMode: ThemeMode
  sidebarCollapsed: boolean
  wsStatus: WsStatus
  setThemeMode: (mode: ThemeMode) => void
  toggleSidebar: () => void
  setWsStatus: (status: WsStatus) => void
}

export const useUiStore = create<UiState>((set) => ({
  themeMode: loadThemeMode(),
  sidebarCollapsed: false,
  wsStatus: 'connecting',
  setThemeMode: (mode) => {
    persistThemeMode(mode)
    set({ themeMode: mode })
  },
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setWsStatus: (status) => set({ wsStatus: status }),
}))
