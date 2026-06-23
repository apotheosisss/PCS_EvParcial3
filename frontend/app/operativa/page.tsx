"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PredictForm } from "@/components/views/predict-form"
import { BatchPredict } from "@/components/views/batch-predict"
import { PredictionsTable } from "@/components/views/predictions-table"

export default function OperativaPage() {
  return (
    <Tabs defaultValue="simulador" className="space-y-4">
      <TabsList>
        <TabsTrigger value="simulador">Simulador</TabsTrigger>
        <TabsTrigger value="lote">Por lote</TabsTrigger>
        <TabsTrigger value="muestra">Predicciones</TabsTrigger>
      </TabsList>

      <TabsContent value="simulador">
        <PredictForm />
      </TabsContent>
      <TabsContent value="lote">
        <BatchPredict />
      </TabsContent>
      <TabsContent value="muestra">
        <PredictionsTable />
      </TabsContent>
    </Tabs>
  )
}
