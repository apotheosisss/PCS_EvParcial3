import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface KpiCardProps {
  title: string
  value: string
  hint?: string
  icon?: React.ReactNode
}

export function KpiCard({ title, value, hint, icon }: KpiCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
          {title}
        </CardTitle>
        {icon ? <span className="text-muted-foreground">{icon}</span> : null}
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-semibold tabular-nums">{value}</div>
        {hint ? <p className="mt-1 text-xs text-muted-foreground">{hint}</p> : null}
      </CardContent>
    </Card>
  )
}
