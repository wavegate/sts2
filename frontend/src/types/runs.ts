/**
 * Run as returned from GET /api/runs and POST /api/runs/upload.
 * Id is (start_time, seed); use `${start_time}_${seed}` for a single key.
 */
export interface Run {
  start_time: number
  seed: string
  build_id: string
  schema_version: number
  run_time: number
  win: boolean
  was_abandoned: boolean
  killed_by_encounter: string
  killed_by_event: string
  character: string
  ascension: number
  game_mode: string
  deck_size: number
  upgraded_card_count: number
  relic_count: number
  floor_reached: number
  bosses_killed: number
}
