import { useEffect } from 'react'
import { Menu } from 'antd'
import type { MenuProps } from 'antd'
import { useLayoutStore, type SiderMenuKey } from '../../stores/layoutStore'
import { useNavigate, useLocation } from 'react-router-dom'

const items: MenuProps['items'] = [
  { key: 'itinerary', label: '行程规划' },
  { key: 'todos', label: '待办清单' },
  { key: 'packing', label: '行李清单' },
]

const keyToPath: Record<SiderMenuKey, string> = {
  itinerary: '/',
  todos: '/todos',
  packing: '/packing',
}

const pathToKey = (path: string): SiderMenuKey => {
  if (path === '/todos') return 'todos'
  if (path === '/packing') return 'packing'
  return 'itinerary'
}

export function SiderMenu() {
  const { setSiderMenuKey } = useLayoutStore()
  const navigate = useNavigate()
  const location = useLocation()
  const selectedKey = pathToKey(location.pathname)

  useEffect(() => {
    setSiderMenuKey(selectedKey)
  }, [location.pathname, selectedKey, setSiderMenuKey])

  const onClick: MenuProps['onClick'] = ({ key }) => {
    const k = key as SiderMenuKey
    setSiderMenuKey(k)
    navigate(keyToPath[k])
  }

  return (
    <Menu
      mode="inline"
      selectedKeys={[selectedKey]}
      items={items}
      onClick={onClick}
      style={{ height: '100%', borderInlineEnd: 0 }}
    />
  )
}
