import { create } from 'zustand'

export type SiderMenuKey = 'itinerary' | 'todos' | 'packing'

interface LayoutState {
  siderCollapsed: boolean
  siderMenuKey: SiderMenuKey
  setSiderCollapsed: (collapsed: boolean) => void
  toggleSider: () => void
  setSiderMenuKey: (key: SiderMenuKey) => void
}

export const useLayoutStore = create<LayoutState>((set) => ({
  siderCollapsed: false,
  siderMenuKey: 'itinerary',
  setSiderCollapsed: (collapsed) => set({ siderCollapsed: collapsed }),
  toggleSider: () => set((s) => ({ siderCollapsed: !s.siderCollapsed })),
  setSiderMenuKey: (key) => set({ siderMenuKey: key }),
}))
