import { Button, Input, Space, Typography, message } from 'antd'
import { useCallback, useState } from 'react'
import { useProfileStore } from '../../stores/profileStore'
import { modifyItineraryAndRegenerate } from '../../api/itinerary'

export function ChatPanel() {
  const { nickname } = useProfileStore()
  const [modifyText, setModifyText] = useState('')
  const [modifying, setModifying] = useState(false)

  const handleModifyItinerary = useCallback(async () => {
    if (!modifyText.trim() || modifying) {
      return
    }

    const text = modifyText.trim()
    let days: number | undefined
    let dailyBudget: number | undefined

    const daysMatch = text.match(/(\d+)\s*天/)
    if (daysMatch) {
      days = Number(daysMatch[1])
    }

    const budgetMatch = text.match(/预算.*?(\d+)\s*元?\/?天?/)
    if (budgetMatch) {
      dailyBudget = Number(budgetMatch[1])
    }

    if (days == null && dailyBudget == null) {
      message.warning('当前仅支持修改“天数”和“人均日预算”，例如：修改为 4 天；预算调整为 200 元/天')
      return
    }

    try {
      setModifying(true)
      await modifyItineraryAndRegenerate({
        days,
        daily_budget_per_person: dailyBudget,
      })
      message.success('已根据指令更新需求并重新生成行程，请在左侧刷新查看')
      setModifyText('')
    } catch {
      message.error('修改行程失败，请稍后重试')
    } finally {
      setModifying(false)
    }
  }, [modifyText, modifying])

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
      }}
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <Space.Compact style={{ width: '100%' }}>
          <Input
            placeholder="例如：修改为 4 天；预算调整为 200 元/天"
            value={modifyText}
            onChange={(e) => setModifyText(e.target.value)}
            onPressEnter={handleModifyItinerary}
            disabled={modifying}
          />
          <Button
            type="primary"
            onClick={handleModifyItinerary}
            loading={modifying}
          >
            发送指令
          </Button>
        </Space.Compact>
      </div>
    </div>
  )
}
