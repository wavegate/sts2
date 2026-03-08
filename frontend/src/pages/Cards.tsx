import { useQuery } from '@tanstack/react-query'
import { getCards } from '@/src/services/cardsService'
import { Card as CardUi } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

function CardsPage() {
  const { data: cards, isLoading } = useQuery({
    queryKey: ['cards'],
    queryFn: () => getCards(),
  })

  return (
    <div className="container mx-auto p-6">
      <h1 className="mb-6 text-2xl font-semibold">Cards</h1>
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 12 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-lg" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {cards?.map((card) => (
            <CardUi key={card.id} className="p-4">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <p className="font-medium truncate" title={card.name}>{card.name}</p>
                  <p className="text-muted-foreground text-sm">
                    {card.type ?? '—'} · {card.rarity ?? '—'}
                  </p>
                </div>
                {card.cost != null && (
                  <span className="shrink-0 rounded bg-muted px-2 py-0.5 text-sm font-medium">
                    {card.cost}
                  </span>
                )}
              </div>
              {card.description && (
                <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">
                  {card.description.replace(/\[.*?\]/g, '').trim()}
                </p>
              )}
            </CardUi>
          ))}
        </div>
      )}
    </div>
  )
}

export default CardsPage
