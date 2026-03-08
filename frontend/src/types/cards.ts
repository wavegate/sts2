/**
 * Card entity from the API (matches backend Card model).
 */
export interface Card {
  id: string
  name: string
  description: string | null
  description_raw: string | null
  cost: number | null
  is_x_cost: boolean | null
  is_x_star_cost: boolean | null
  star_cost: number | null
  type: string | null
  rarity: string | null
  target: string | null
  color: string | null
  damage: number | null
  block: number | null
  hit_count: number | null
  powers_applied: PowerApplied[] | null
  cards_draw: number | null
  energy_gain: number | null
  hp_loss: number | null
  keywords: string[] | null
  tags: string[] | null
  vars: Record<string, unknown> | null
  upgrade: Record<string, unknown> | null
  image_url: string | null
  beta_image_url: string | null
}

export interface PowerApplied {
  power: string
  amount: number
}

/**
 * Query params for GET /api/cards (list cards).
 */
export interface CardsQueryParams {
  color?: string
  type?: string
  rarity?: string
  search?: string
}
