import { useEffect, useState } from 'react'
import { Modal, Form, Input } from 'antd'
import { useProfileStore } from '../../stores/profileStore'

interface NicknameSetupProps {
  open: boolean
  onFinished: () => void
}

export function NicknameSetup({ open, onFinished }: NicknameSetupProps) {
  const { nickname, setNickname } = useProfileStore()
  const [value, setValue] = useState(nickname)

  useEffect(() => {
    if (open && !nickname) {
      setValue('')
    }
  }, [open, nickname])

  const handleOk = () => {
    const trimmed = value.trim()
    if (!trimmed) {
      return
    }
    setNickname(trimmed)
    onFinished()
  }

  return (
    <Modal
      open={open}
      title="设置你的昵称"
      okText="开始规划旅程"
      cancelButtonProps={{ style: { display: 'none' } }}
      onOk={handleOk}
      maskClosable={false}
      closable={false}
    >
      <Form layout="vertical">
        <Form.Item
          label="昵称"
          required
          extra="将用于“[昵称]的旅行图谱”标题和 AI 对话称呼。"
        >
          <Input
            placeholder="例如：cheyann"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onPressEnter={handleOk}
          />
        </Form.Item>
      </Form>
    </Modal>
  )
}

