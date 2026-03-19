import { create } from 'zustand'

export type CreationStage =
  | 'idle'
  | 'requirements_collecting'
  | 'requirements_finalized'
  | 'intelligence_collecting'
  | 'intelligence_completed'
  | 'itinerary_planning'
  | 'itinerary_completed'

export interface TravelTaskBook {
  user_nickname: string
  destination: string
  dates: [string, string]
  total_days: number
  total_budget_range: [string, string]
  travel_purposes: string[]
  preference_intensity: string
  preference_budget: string
  must_visit: string[]
  notes?: string | null
}

interface ItineraryCreationState {
  stage: CreationStage
  travelTaskBook: TravelTaskBook | null
  isConfirming: boolean
  hasConfirmedTaskBook: boolean
  setStage: (stage: CreationStage) => void
  setTravelTaskBook: (taskBook: TravelTaskBook | null) => void
  setIsConfirming: (value: boolean) => void
  setHasConfirmedTaskBook: (value: boolean) => void
}

export const useItineraryCreationStore = create<ItineraryCreationState>((set) => ({
  stage: 'idle',
  travelTaskBook: null,
  isConfirming: false,
  hasConfirmedTaskBook: false,
  setStage: (stage) => set({ stage }),
  setTravelTaskBook: (taskBook) => {
    // #region agent log
    fetch('http://127.0.0.1:7890/ingest/3ed81db4-2443-4139-90ac-27b9e957c4f4', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Debug-Session-Id': 'aadaee',
      },
      body: JSON.stringify({
        sessionId: 'aadaee',
        runId: 'run1',
        hypothesisId: 'A',
        location: 'frontend/src/stores/itineraryCreationStore.ts:setTravelTaskBook',
        message: 'setTravelTaskBook called',
        data: {
          hasTaskBook: Boolean(taskBook),
          destination: taskBook?.destination,
        },
        timestamp: Date.now(),
      }),
    }).catch(() => {})
    // #endregion agent log

    return set({
      travelTaskBook: taskBook,
      hasConfirmedTaskBook: false,
    })
  },
  setIsConfirming: (value) => set({ isConfirming: value }),
  setHasConfirmedTaskBook: (value) => set({ hasConfirmedTaskBook: value }),
}))

