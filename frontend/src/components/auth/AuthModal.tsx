import { useState } from 'react'
import { Modal, Tabs, Form, Input, Button, message, Alert } from 'antd'
import type { TabsProps } from 'antd'
import { login, register } from '../../api/auth'

interface AuthModalProps {
  open: boolean
  onClose: () => void
}

export function AuthModal({ open, onClose }: AuthModalProps) {
  const [activeKey, setActiveKey] = useState<'login' | 'register'>('login')
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()
  const [errorText, setErrorText] = useState<string | null>(null)

  const handleOk = async () => {
    const values = await form.validateFields()
    setLoading(true)
    setErrorText(null)

    try {
      if (activeKey === 'login') {
        await login({
          email: values.email,
          password: values.password,
        })
        message.success('登录成功')
        onClose()
      } else {
        await register({
          email: values.email,
          name: values.name,
          password: values.password,
        })
        message.success('注册成功，请使用邮箱和密码登录')
        setActiveKey('login')
        // 切回登录时保留邮箱，清空密码
        form.setFieldsValue({ password: undefined })
      }
    } catch (err: unknown) {
      // 解析后端错误信息
      const anyErr = err as { response?: { data?: unknown } }
      const detail =
        (anyErr.response?.data as { detail?: string })?.detail ??
        (anyErr.response?.data as { message?: string })?.message

      const fallbackMessage =
        activeKey === 'login' ? '登录失败，请检查邮箱和密码后重试。' : '注册失败，请稍后重试。'

      const msg = detail || fallbackMessage
      setErrorText(msg)
      message.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const items: TabsProps['items'] = [
    {
      key: 'login',
      label: '登录',
      children: (
        <Form layout="vertical" form={form}>
          {errorText && (
            <Form.Item>
              <Alert type="error" message={errorText} showIcon />
            </Form.Item>
          )}
          <Form.Item
            label="邮箱"
            name="email"
            rules={[{ required: true, message: '请输入邮箱' }]}
          >
            <Input placeholder="you@example.com" />
          </Form.Item>
          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
        </Form>
      ),
    },
    {
      key: 'register',
      label: '注册',
      children: (
        <Form layout="vertical" form={form}>
          {errorText && (
            <Form.Item>
              <Alert type="error" message={errorText} showIcon />
            </Form.Item>
          )}
          <Form.Item
            label="邮箱"
            name="email"
            rules={[{ required: true, message: '请输入邮箱' }]}
          >
            <Input placeholder="you@example.com" />
          </Form.Item>
          <Form.Item
            label="昵称"
            name="name"
            rules={[{ required: true, message: '请输入昵称' }]}
          >
            <Input placeholder="例如：cheyann" />
          </Form.Item>
          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
        </Form>
      ),
    },
  ]

  return (
    <Modal
      open={open}
      title="登录 / 注册 ItinerAI"
      onCancel={onClose}
      footer={
        <Button type="primary" loading={loading} onClick={handleOk}>
          {activeKey === 'login' ? '登录' : '注册'}
        </Button>
      }
      destroyOnClose
    >
      <Tabs
        activeKey={activeKey}
        onChange={(key) => {
          setActiveKey(key as 'login' | 'register')
          form.resetFields()
          setErrorText(null)
        }}
        items={items}
      />
    </Modal>
  )
}

