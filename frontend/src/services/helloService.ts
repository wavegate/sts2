import api from '@/lib/api'

export async function fetchHello(): Promise<{ Hello: string }> {
  const res = await api.get<{ Hello: string }>('/')
  return res.data
}
