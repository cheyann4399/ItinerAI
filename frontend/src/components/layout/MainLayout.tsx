import { Layout, theme as antdTheme, Button, Grid } from 'antd'
import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons'
import { Header } from './Header'
import { SiderMenu } from './SiderMenu'
import { ItineraryGraph } from '../itinerary/ItineraryGraph'
import { RightPanel } from '../itinerary/RightPanel'
import { useThemeStore } from '../../stores/themeStore'
import { useLayoutStore } from '../../stores/layoutStore'

const { Sider, Content } = Layout

export function MainLayout() {
  const { mode } = useThemeStore()
  const { siderCollapsed, toggleSider } = useLayoutStore()
  const breakpoint = Grid.useBreakpoint()
  const isNarrow = !breakpoint.lg
  const {
    token: { colorBgContainer, colorBgLayout },
  } = antdTheme.useToken()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        theme={mode}
        width={240}
        collapsedWidth={80}
        collapsed={siderCollapsed}
        breakpoint="lg"
        onBreakpoint={(broken) => useLayoutStore.getState().setSiderCollapsed(broken)}
        trigger={
          <Button
            type="text"
            icon={siderCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={toggleSider}
            style={{ color: 'rgba(255,255,255,0.65)' }}
            aria-label={siderCollapsed ? '展开侧边栏' : '折叠侧边栏'}
          />
        }
        style={{ overflow: 'auto' }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: siderCollapsed ? 'center' : 'flex-start',
            paddingInline: 16,
            color: '#fff',
            fontWeight: 600,
          }}
        >
          {siderCollapsed ? 'IA' : 'ItinerAI'}
        </div>
        <SiderMenu />
      </Sider>
      <Layout>
        <Header />
        <Content
          style={{
            padding: 24,
            background: colorBgLayout,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'auto',
          }}
        >
          <div
            style={{
              display: 'flex',
              flexDirection: isNarrow ? 'column' : 'row',
              gap: 24,
              flex: 1,
              minHeight: 0,
            }}
          >
            <div
              style={{
                flex: isNarrow ? '0 0 auto' : '0 0 70%',
                minWidth: 0,
                minHeight: isNarrow ? 280 : undefined,
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <ItineraryGraph />
            </div>
            <div
              style={{
                flex: isNarrow ? '1 1 auto' : '0 0 calc(30% - 24px)',
                minWidth: 0,
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <RightPanel />
            </div>
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}
