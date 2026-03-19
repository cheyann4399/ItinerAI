import { useState } from 'react'
import {
  Button,
  DatePicker,
  Form,
  Input,
  InputNumber,
  Radio,
  Select,
  Space,
  Typography,
} from 'antd'
import dayjs, { Dayjs } from 'dayjs'

import { apiClient } from '../../api/client'
import { useProfileStore } from '../../stores/profileStore'

type TravelTimeType = 'weekend' | 'weekday' | 'specific_date'
type Rhythm = 'fast' | 'slow'

type PreferenceOption =
  | 'history_culture'
  | 'food'
  | 'nature'
  | 'leisure'
  | 'creative'
  | 'outdoor'

interface DemandFormValues {
  destination: string
  adult_count: number
  child_count: number
  elder_count: number
  days: number
  daily_budget_per_person: number
  travel_time_type: TravelTimeType
  travel_date?: Dayjs
  rhythm: Rhythm
  preferences: PreferenceOption[]
}

interface DemandFormProps {
  onSubmitted?: (payload: unknown) => void
}

export function DemandForm({ onSubmitted }: DemandFormProps) {
  const [form] = Form.useForm<DemandFormValues>()
  const [submitting, setSubmitting] = useState(false)
  const { nickname } = useProfileStore()

  const handleFinish = async (values: DemandFormValues) => {
    setSubmitting(true)
    try {
      const payload = {
        destination: values.destination.trim(),
        adult_count: values.adult_count,
        child_count: values.child_count,
        elder_count: values.elder_count,
        days: values.days,
        daily_budget_per_person: values.daily_budget_per_person,
        travel_time_type: values.travel_time_type,
        travel_date:
          values.travel_time_type === 'specific_date' && values.travel_date
            ? values.travel_date.format('YYYY-MM-DD')
            : null,
        rhythm: values.rhythm,
        preferences: values.preferences,
      }

      // 将表单 JSON 发送给后端（对齐后端实际路由）
      const { data } = await apiClient.post(
        '/itinerary/submit-demand',
        payload,
      )

      onSubmitted?.(data)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      style={{
        borderRadius: 8,
        padding: 24,
        background: 'var(--ant-color-bg-container, #fff)',
      }}
    >
      <Typography.Title level={5} style={{ marginTop: 0 }}>
        旅行需求设置
      </Typography.Title>
      <Typography.Paragraph type="secondary" style={{ marginBottom: 16 }}>
        {nickname ? `${nickname}，` : ''}请通过固定选项框填写你的旅行需求，我们将为你生成专属《旅行图谱》。
      </Typography.Paragraph>

      <Form<DemandFormValues>
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        initialValues={{
          adult_count: 2,
          child_count: 0,
          elder_count: 0,
          days: 3,
          daily_budget_per_person: 300,
          travel_time_type: 'weekend',
          rhythm: 'fast',
          preferences: ['history_culture'],
        }}
      >
        <Form.Item
          label="目的地"
          name="destination"
          rules={[{ required: true, message: '请输入目的地' }]}
        >
          <Input placeholder="例如：西安、青岛、上海" allowClear />
        </Form.Item>

        <Form.Item label="游玩人数">
          <Space.Compact block>
            <Form.Item
              name="adult_count"
              noStyle
              rules={[{ required: true, message: '请输入成人人数' }]}
            >
              <InputNumber min={0} placeholder="成人" style={{ width: '33.33%' }} />
            </Form.Item>
            <Form.Item
              name="child_count"
              noStyle
              rules={[{ required: true, message: '请输入儿童人数' }]}
            >
              <InputNumber min={0} placeholder="儿童" style={{ width: '33.33%' }} />
            </Form.Item>
            <Form.Item
              name="elder_count"
              noStyle
              rules={[{ required: true, message: '请输入老人人数' }]}
            >
              <InputNumber min={0} placeholder="老人" style={{ width: '33.33%' }} />
            </Form.Item>
          </Space.Compact>
        </Form.Item>

        <Space size="middle" style={{ width: '100%' }}>
          <Form.Item
            label="游玩天数"
            name="days"
            style={{ flex: 1 }}
            rules={[{ required: true, message: '请输入游玩天数' }]}
          >
            <InputNumber min={1} precision={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            label="人均日预算（元，不含住宿）"
            name="daily_budget_per_person"
            style={{ flex: 2 }}
            rules={[{ required: true, message: '请输入人均日预算' }]}
          >
            <InputNumber min={0} precision={0} style={{ width: '100%' }} />
          </Form.Item>
        </Space>

        <Form.Item label="出行时间" required>
          <Space.Compact block>
            <Form.Item
              name="travel_time_type"
              noStyle
              rules={[{ required: true, message: '请选择出行时间类型' }]}
            >
              <Radio.Group style={{ width: '50%' }}>
                <Radio.Button value="weekend">周末</Radio.Button>
                <Radio.Button value="weekday">周中</Radio.Button>
                <Radio.Button value="specific_date">具体日期</Radio.Button>
              </Radio.Group>
            </Form.Item>
            <Form.Item shouldUpdate noStyle>
              {({ getFieldValue }) => {
                const type = getFieldValue('travel_time_type') as TravelTimeType
                return (
                  <Form.Item
                    name="travel_date"
                    noStyle
                    rules={
                      type === 'specific_date'
                        ? [{ required: true, message: '请选择出行日期' }]
                        : []
                    }
                  >
                    <DatePicker
                      style={{ width: '50%' }}
                      disabled={type !== 'specific_date'}
                      disabledDate={(current) =>
                        !!current && current < dayjs().startOf('day')
                      }
                    />
                  </Form.Item>
                )
              }}
            </Form.Item>
          </Space.Compact>
        </Form.Item>

        <Form.Item
          label="旅行节奏"
          name="rhythm"
          rules={[{ required: true, message: '请选择旅行节奏' }]}
        >
          <Radio.Group buttonStyle="solid">
            <Radio.Button value="fast">快节奏（3-4 个景点/天）</Radio.Button>
            <Radio.Button value="slow">慢节奏（1-2 个景点/天）</Radio.Button>
          </Radio.Group>
        </Form.Item>

        <Form.Item
          label="旅行偏好（最多选择 3 项）"
          name="preferences"
          rules={[
            { required: true, message: '请至少选择 1 项偏好' },
            {
              validator(_, value: PreferenceOption[]) {
                if (Array.isArray(value) && value.length <= 3) {
                  return Promise.resolve()
                }
                return Promise.reject(
                  new Error('最多只能选择 3 项偏好'),
                )
              },
            },
          ]}
        >
          <Select
            mode="multiple"
            maxTagCount="responsive"
            placeholder="请选择最多 3 项旅行偏好"
          >
            <Select.Option value="history_culture">历史文化</Select.Option>
            <Select.Option value="food">美食探索</Select.Option>
            <Select.Option value="nature">自然风光</Select.Option>
            <Select.Option value="leisure">休闲娱乐</Select.Option>
            <Select.Option value="creative">文化创意</Select.Option>
            <Select.Option value="outdoor">户外探险</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item style={{ marginTop: 16 }}>
          <Button
            type="primary"
            htmlType="submit"
            block
            loading={submitting}
          >
            提交需求
          </Button>
        </Form.Item>
      </Form>
    </div>
  )
}

