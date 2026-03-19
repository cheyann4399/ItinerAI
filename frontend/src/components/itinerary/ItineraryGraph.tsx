import { useEffect, useState } from 'react'
import {
  Alert,
  Button,
  Empty,
  List,
  Skeleton,
  Space,
  Steps,
  Tag,
  Typography,
  message,
} from 'antd'
import type { TabsProps } from 'antd'
import { Tabs } from 'antd'

import { useLayoutStore } from '../../stores/layoutStore'
import { useAuthStore } from '../../stores/authStore'
import { useProfileStore } from '../../stores/profileStore'
import { useItineraryCreationStore } from '../../stores/itineraryCreationStore'
import {
  fetchRecommendedSpots,
  generateItinerary,
  type ItineraryDay,
  type ItineraryPlan,
  type RecommendedSpotDto,
} from '../../api/itinerary'
import { DemandForm } from './DemandForm'
import { SpotCardSelector, type SpotCardDto } from './SpotCardSelector'

export function ItineraryGraph() {
  const { siderMenuKey } = useLayoutStore()
  const { nickname } = useProfileStore()
  const { isAuthenticated } = useAuthStore()
  const { setTravelTaskBook } = useItineraryCreationStore()

  const [plan, setPlan] = useState<ItineraryPlan | null>(null)
  const [activeDayIndex, setActiveDayIndex] = useState<number>(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [step, setStep] = useState<'demand' | 'spots' | 'itinerary'>('demand')
  const [spots, setSpots] = useState<SpotCardDto[]>([])
  const [spotsLoading, setSpotsLoading] = useState(false)
  const [spotsError, setSpotsError] = useState<string | null>(null)

  const isItineraryView = siderMenuKey === 'itinerary'

  type DemandAnalyzeResponse = {
    travel_task_book?: unknown
    recommended_spots?: RecommendedSpotDto[]
  }

  const mapRecommendedSpotToCard = (spot: RecommendedSpotDto): SpotCardDto => ({
    id: spot.id,
    name: spot.name,
    thumbnail: spot.thumbnail,
    description: spot.description,
    crowd: spot.crowd,
    cost: spot.cost,
    risk_tags: spot.risk_tags,
  })

  const handleDemandSubmitted = (response: unknown) => {
    const data = response as DemandAnalyzeResponse

    if (data.travel_task_book && typeof data.travel_task_book === 'object') {
      setTravelTaskBook(data.travel_task_book as never)
      message.success('需求已记录，正在为你推荐景点')
    }

    if (Array.isArray(data.recommended_spots)) {
      setSpots(data.recommended_spots.map(mapRecommendedSpotToCard))
      setStep('spots')
      return
    }

    setSpotsLoading(true)
    setSpotsError(null)
    setStep('spots')

    fetchRecommendedSpots()
      .then((result) => {
        setSpots(result.spots.map(mapRecommendedSpotToCard))
      })
      .catch(() => {
        setSpotsError('暂时无法获取推荐景点，你仍然可以直接生成行程。')
      })
      .finally(() => {
        setSpotsLoading(false)
      })
  }

  const handleSpotsSubmitted = () => {
    message.success('景点已确认，你可以生成行程')
    setStep('itinerary')
  }

  const loadItinerary = async () => {
    if (!isAuthenticated) {
      setError('请先登录后再生成行程。')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const data = await generateItinerary()
      setPlan(data)
      setActiveDayIndex(0)
    } catch (e) {
      setError('暂时无法加载行程，请确认已完成登录与需求提交流程。')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isItineraryView && !plan && !loading && !error) {
      // 初次进入行程视图时不自动请求，保留为空状态，由用户点击按钮触发
    }
  }, [isItineraryView, plan, loading, error])

  const renderWeather = (day: ItineraryDay) => {
    const condition = String(day.weather.condition ?? '未知')
    const high = day.weather.high
    const low = day.weather.low

    if (high == null || low == null) {
      return condition
    }

    return `${condition} · ${low}°C - ${high}°C`
  }

  const items: TabsProps['items'] =
    plan?.days.map((day, index) => ({
      key: String(index),
      label: `Day ${day.day_index}`,
    })) ?? []

  const currentDay: ItineraryDay | null =
    plan && plan.days.length > 0 ? plan.days[activeDayIndex] ?? plan.days[0] : null

  const titlePrefix = nickname ? `${nickname} 的` : ''
  const destination = plan?.destination ?? '旅行'
  const daysText = plan ? `${plan.days.length} 天` : ''

  const renderContent = () => {
    if (!isItineraryView) {
      return (
        <Typography.Paragraph type="secondary">
          此处将展示与 {siderMenuKey === 'todos' ? '待办清单' : '行李清单'} 相关的内容，当前版本仅实现「行程规划」视图。
        </Typography.Paragraph>
      )
    }

    if (step === 'demand') {
      return <DemandForm onSubmitted={handleDemandSubmitted} />
    }

    if (step === 'spots') {
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, flex: 1 }}>
          {spotsError && (
            <Alert type="warning" message={spotsError} showIcon style={{ marginBottom: 4 }} />
          )}
          <Typography.Text type="secondary">
            我们基于你的目的地和偏好推荐了以下景点，至少选择 1 个再继续。
          </Typography.Text>
          <div style={{ flex: 1, minHeight: 200 }}>
            <SpotCardSelector
              spots={spots}
              loading={spotsLoading}
              onSubmitted={handleSpotsSubmitted}
            />
          </div>
        </div>
      )
    }

    // step === 'itinerary'
    return (
      <>
        {plan && (
          <Alert
            type="info"
            message="预算提示"
            description={plan.budget_hint}
            showIcon
          />
        )}

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Typography.Text strong>行程天数</Typography.Text>
            {plan && plan.days.length > 0 && (
              <Tabs
                items={items}
                activeKey={String(activeDayIndex)}
                onChange={(key) => setActiveDayIndex(Number(key))}
                size="small"
              />
            )}
          </Space>
          <Space>
            <Button onClick={() => setStep('demand')}>重新填写需求</Button>
            <Button type="primary" onClick={loadItinerary} loading={loading}>
              {plan ? '重新生成行程' : '生成行程'}
            </Button>
          </Space>
        </div>

        {error && (
          <Alert
            type="error"
            message="行程加载失败"
            description={error}
            showIcon
          />
        )}

        <div style={{ flex: 1, minHeight: 200, overflow: 'auto' }}>
          {loading ? (
            <Skeleton active paragraph={{ rows: 6 }} />
          ) : !plan || !currentDay ? (
            <Empty
              description={
                <span>
                  暂无行程数据，请先完成「旅行需求」和「景点选择」，然后点击「生成行程」。
                </span>
              }
            />
          ) : currentDay.spots.length === 0 ? (
            <Empty
              description={
                <span>
                  第 {currentDay.day_index} 天暂无推荐景点，你可以稍后在行程中手动添加。
                </span>
              }
            />
          ) : (
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Typography.Text type="secondary">
                天气：{renderWeather(currentDay)} · 预估人均花费：¥{currentDay.total_cost}
              </Typography.Text>
              <List
                itemLayout="vertical"
                dataSource={currentDay.spots}
                renderItem={(spot, index) => (
                  <List.Item key={`${spot.spot_name}-${index}`}>
                    <List.Item.Meta
                      title={
                        <Space size="small">
                          <Typography.Text strong>
                            {index + 1}. {spot.spot_name}
                          </Typography.Text>
                          <Tag color="blue">{spot.duration_hours} 小时</Tag>
                          <Tag color="geekblue">¥{spot.cost}</Tag>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size={4}>
                          <Typography.Text type="secondary">
                            交通：{spot.traffic}
                          </Typography.Text>
                          {spot.tip.length > 0 && (
                            <Space size={[4, 4]} wrap>
                              {spot.tip.map((t) => (
                                <Tag key={t} color="red">
                                  {t}
                                </Tag>
                              ))}
                            </Space>
                          )}
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </Space>
          )}
        </div>
      </>
    )
  }

  const currentStepIndex = step === 'demand' ? 0 : step === 'spots' ? 1 : 2

  return (
    <div
      style={{
        height: '100%',
        minHeight: 360,
        borderRadius: 8,
        padding: 24,
        background: 'var(--ant-color-bg-container, #fff)',
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}
    >
      <div>
        <Typography.Title level={5} style={{ marginTop: 0, marginBottom: 8 }}>
          {isItineraryView ? '行程规划' : siderMenuKey === 'todos' ? '待办清单' : '行李清单'}
        </Typography.Title>
        {isItineraryView && (
          <Typography.Text type="secondary">
            {titlePrefix}
            {destination}
            {daysText && ` · ${daysText}`} 旅行图谱
          </Typography.Text>
        )}
      </div>

      {isItineraryView && (
        <Steps
          current={currentStepIndex}
          items={[
            { title: '旅行需求' },
            { title: '景点选择' },
            { title: '行程结果' },
          ]}
          size="small"
        />
      )}

      <div style={{ flex: 1, minHeight: 0 }}>{renderContent()}</div>
    </div>
  )
}
