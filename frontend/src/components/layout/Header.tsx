import { useState } from 'react'
import { Button, Dropdown, Layout, Menu, Switch, Typography, theme } from 'antd'
import type { MenuProps } from 'antd'
import { useThemeStore } from '../../stores/themeStore'
import { useProfileStore } from '../../stores/profileStore'
import { useAuthStore } from '../../stores/authStore'
import { AuthModal } from '../auth/AuthModal'

export function Header() {
  const { mode, toggleMode } = useThemeStore()
  const { token } = theme.useToken()
  const colorBgContainer = token.colorBgContainer ?? '#fff'
  const { nickname } = useProfileStore()
  const { isAuthenticated, clearAuth } = useAuthStore()
  const [authModalOpen, setAuthModalOpen] = useState(false)

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'logout',
      label: '退出登录',
      onClick: () => clearAuth(),
    },
  ]

  return (
    <>
      <Layout.Header
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingInline: 24,
          background: colorBgContainer,
          borderBottom: '1px solid var(--ant-color-border, rgba(5,5,5,0.06))',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}
        >
          <Typography.Title
            level={4}
            style={{
              margin: 0,
              letterSpacing: 0.5,
            }}
          >
            ItinerAI
          </Typography.Title>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            {nickname ? `${nickname} 的智能旅行规划助手` : '智能旅行规划助手'}
          </Typography.Text>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Button type="text" size="small" disabled>
            历史旅行规划
          </Button>
          <Button type="link" size="small">
            API 配置
          </Button>
          <Button type="default" size="small" disabled>
            导出规划
          </Button>
          <span style={{ fontSize: 12, color: '#666' }}>暗色</span>
          <Switch checked={mode === 'dark'} onChange={toggleMode} size="small" />
          {isAuthenticated ? (
            <Dropdown overlay={<Menu items={userMenuItems} />}>
              <Button size="small" type="default">
                {nickname || '已登录'}
              </Button>
            </Dropdown>
          ) : (
            <Button size="small" type="primary" onClick={() => setAuthModalOpen(true)}>
              登录 / 注册
            </Button>
          )}
        </div>
      </Layout.Header>
      <AuthModal open={authModalOpen} onClose={() => setAuthModalOpen(false)} />
    </>
  )
}
