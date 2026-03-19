import { Card, Typography } from 'antd'
import { ChatPanel } from '../chat/ChatPanel'

export function RightPanel() {
  return (
    <Card
      title="AI 对话"
      bodyStyle={{ padding: 16, height: '100%', display: 'flex', flexDirection: 'column' }}
      style={{ height: '100%', minHeight: 360 }}
    >
      <Typography.Paragraph type="secondary" style={{ marginBottom: 8 }}>
        生成行程后，你可以在这里通过标准化指令修改天数和预算。
      </Typography.Paragraph>
      <div style={{ flex: 1, minHeight: 0 }}>
        <ChatPanel />
      </div>
    </Card>
  )
}

