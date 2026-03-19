import { useMemo, useState } from 'react'
import { Button, Card, Col, Empty, Row, Space, Tag, Typography, message } from 'antd'

import { apiClient } from '../../api/client'

const { Meta } = Card

export interface SpotCardDto {
  id: string
  name: string
  thumbnail: string
  description: string
  crowd: string
  cost: {
    ticket: number | string
    avg_spend: number | string
    [key: string]: unknown
  }
  risk_tags: string[]
}

export interface SpotCardSelectorProps {
  spots: SpotCardDto[]
  loading?: boolean
  onSubmitted?: (selected: SpotCardDto[]) => void
  onError?: (error: unknown) => void
}

export function SpotCardSelector({
  spots,
  loading,
  onSubmitted,
  onError,
}: SpotCardSelectorProps) {
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)

  const isSubmittingDisabled = useMemo(
    () => submitting || selectedIds.length === 0,
    [submitting, selectedIds.length],
  )

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    )
  }

  const handleSubmit = async () => {
    if (selectedIds.length === 0) return
    setSubmitting(true)
    try {
      const selected = spots.filter((s) => selectedIds.includes(s.id))
      // 将选中景点提交到后端（预留真实接口路径）
      await apiClient.post('/itinerary/confirm-spots', selected)
      onSubmitted?.(selected)
      message.success('已保存选中的景点')
    } catch (error) {
      onError?.(error)
      message.error('提交景点选择失败，请稍后重试')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading && !spots.length) {
    return (
      <div
        style={{
          borderRadius: 8,
          padding: 24,
          background: 'var(--ant-color-bg-container, #fff)',
        }}
      >
        <Typography.Title level={5} style={{ marginTop: 0 }}>
          为你推荐的景点 / 体验
        </Typography.Title>
        <Typography.Paragraph type="secondary" style={{ marginBottom: 12 }}>
          正在为你加载推荐景点，请稍候...
        </Typography.Paragraph>
        <Row gutter={[16, 16]}>
          {Array.from({ length: 3 }).map((_, idx) => (
            <Col key={idx} xs={24} sm={12}>
              <Card loading />
            </Col>
          ))}
        </Row>
      </div>
    )
  }

  if (!spots.length && !loading) {
    return (
      <div
        style={{
          borderRadius: 8,
          padding: 24,
          background: 'var(--ant-color-bg-container, #fff)',
        }}
      >
        <Empty
          description={
            <span>
              暂无可推荐景点，你可以稍后重试，或直接生成空白行程后在《旅行图谱》中手动添加。
            </span>
          }
        />
      </div>
    )
  }

  return (
    <div
      style={{
        borderRadius: 8,
        padding: 24,
        background: 'var(--ant-color-bg-container, #fff)',
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}
    >
      <Typography.Title level={5} style={{ marginTop: 0 }}>
        为你推荐的景点 / 体验
      </Typography.Title>
      <Typography.Paragraph type="secondary">
        点击卡片选择你感兴趣的景点，至少选择 1 个后可继续生成行程。
      </Typography.Paragraph>

      <Row gutter={[16, 16]}>
        {spots.map((spot) => {
          const checked = selectedIds.includes(spot.id)
          const hasTicket =
            spot.cost && spot.cost.ticket !== null && spot.cost.ticket !== undefined
          const ticketLabel =
            !hasTicket || Number(spot.cost.ticket) === 0
              ? '免费'
              : `门票约 ¥${spot.cost.ticket}`
          const avgSpendLabel =
            spot.cost?.avg_spend !== undefined && spot.cost?.avg_spend !== null
              ? `人均约 ¥${spot.cost.avg_spend}`
              : undefined

          return (
            <Col key={spot.id} xs={24} sm={12}>
              <Card
                hoverable
                loading={loading}
                cover={
                  <div
                    style={{
                      height: 140,
                      overflow: 'hidden',
                      position: 'relative',
                    }}
                  >
                    <img
                      src={spot.thumbnail}
                      alt={spot.name}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                      }}
                    />
                    {checked && (
                      <div
                        style={{
                          position: 'absolute',
                          inset: 0,
                          border: '2px solid var(--ant-color-primary)',
                          boxSizing: 'border-box',
                        }}
                      />
                    )}
                  </div>
                }
                onClick={() => toggleSelect(spot.id)}
                bodyStyle={{ minHeight: 140 }}
                style={{
                  borderColor: checked
                    ? 'var(--ant-color-primary)'
                    : 'var(--ant-color-border)',
                }}
              >
                <Meta
                  title={
                    <Space>
                      <span>{spot.name}</span>
                      {checked && <Tag color="blue">已选</Tag>}
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size={8} style={{ width: '100%' }}>
                      <Typography.Text type="secondary" ellipsis={{ rows: 3 }}>
                        {spot.description}
                      </Typography.Text>
                      <Space size="small" wrap>
                        <Tag>{spot.crowd}</Tag>
                        <Tag color="gold">{ticketLabel}</Tag>
                        {avgSpendLabel && <Tag color="purple">{avgSpendLabel}</Tag>}
                      </Space>
                      <Space size="small" wrap>
                        {spot.risk_tags?.map((tag) => (
                          <Tag key={tag} color="red">
                            {tag}
                          </Tag>
                        ))}
                      </Space>
                    </Space>
                  }
                />
              </Card>
            </Col>
          )
        })}
      </Row>

      <div style={{ marginTop: 8 }}>
        <Button
          type="primary"
          block
          disabled={isSubmittingDisabled}
          loading={submitting}
          onClick={handleSubmit}
        >
          确认选择（已选 {selectedIds.length} 项）
        </Button>
      </div>
    </div>
  )
}

