import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"
import { Disclaimer } from "@/components/layout/disclaimer"

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-svh">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        <main className="flex-1 space-y-6 p-5 lg:p-8">
          <Disclaimer />
          {children}
        </main>
      </div>
    </div>
  )
}
