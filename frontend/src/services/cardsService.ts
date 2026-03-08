import api from '@/lib/api'
import type { Card, CardsQueryParams } from '@/src/types/cards'

const CARDS_BASE = '/api/cards'

/**
 * Build query string from optional filters (omits undefined/null).
 */
function buildSearchParams(params: CardsQueryParams): URLSearchParams {
  const search = new URLSearchParams()
  if (params.color != null && params.color !== '') search.set('color', params.color)
  if (params.type != null && params.type !== '') search.set('type', params.type)
  if (params.rarity != null && params.rarity !== '') search.set('rarity', params.rarity)
  if (params.search != null && params.search !== '') search.set('search', params.search)
  return search
}

/**
 * Fetch cards with optional filters.
 * GET /api/cards?color=...&type=...&rarity=...&search=...
 */
export async function getCards(params: CardsQueryParams = {}): Promise<Card[]> {
  const search = buildSearchParams(params)
  const query = search.toString()
  const url = query ? `${CARDS_BASE}?${query}` : CARDS_BASE
  const res = await api.get<Card[]>(url)
  return res.data
}

/**
 * Fetch a single card by id.
 * GET /api/cards/:id
 * @throws axios error with status 404 when card is not found
 */
export async function getCard(id: string): Promise<Card> {
  const res = await api.get<Card>(`${CARDS_BASE}/${encodeURIComponent(id)}`)
  return res.data
}
