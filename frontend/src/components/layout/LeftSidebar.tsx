import { Menu } from 'antd'
import type { MenuProps } from 'antd'

const items: MenuProps['items'] = [
  {
    key: 'itinerary',
    label: '行程规划',
  },
  {
    key: 'todos',
    label: '待办清单',
  },
  {
    key: 'packing',
    label: '行李清单',
  },
]

export function LeftSidebar() {
  return (
    <Menu
      mode="inline"
      selectable
      defaultSelectedKeys={['itinerary']}
      items={items}
      style={{ height: '100%', borderInlineEnd: 0 }}
    />
  )
}

