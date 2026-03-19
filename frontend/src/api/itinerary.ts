import { apiClient } from './client'

export interface ItineraryContent {
  // 预留给后续富结构行程内容
  [key: string]: unknown
}

export interface CreateItineraryPayload {
  title: string
  description?: string | null
  content?: ItineraryContent | null
}

export interface ItineraryDto {
  id: number
  user_id: number
  title: string
  description: string | null
  content: ItineraryContent | null
  created_at: string
  updated_at: string
}

export async function createItinerary(
  payload: CreateItineraryPayload,
): Promise<ItineraryDto> {
  const { data } = await apiClient.post<ItineraryDto>('/itineraries', payload)
  return data
}

export interface ItinerarySpot {
  spot_name: string
  duration_hours: number
  traffic: string
  cost: number
  tip: string[]
}

export interface ItineraryDay {
  day_index: number
  date: string | null
  weather: {
    condition?: string
    high?: number
    low?: number
    [key: string]: unknown
  }
  spots: ItinerarySpot[]
  total_cost: number
}

export interface ItineraryPlan {
  destination: string
  days: ItineraryDay[]
  budget_hint: string
}

export async function generateItinerary(): Promise<ItineraryPlan> {
  const { data } = await apiClient.post<ItineraryPlan>(
    '/itinerary/generate-itinerary',
  )
  return data
}

export interface ModifyItineraryPayload {
  days?: number
  daily_budget_per_person?: number
}

export async function modifyItineraryAndRegenerate(
  payload: ModifyItineraryPayload,
): Promise<ItineraryPlan> {
  const { data } = await apiClient.post<ItineraryPlan>(
    '/itinerary/modify-and-regenerate',
    payload,
  )
  return data
}

// 景点推荐卡片（与 SpotCardSelector 中结构对齐）
export interface RecommendedSpotDto {
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

export interface SpotRecommendResponseDto {
  destination: string
  spots: RecommendedSpotDto[]
}

export async function fetchRecommendedSpots(): Promise<SpotRecommendResponseDto> {
  const { data } = await apiClient.get<SpotRecommendResponseDto>(
    '/itinerary/get-spots',
  )
  return data
}
