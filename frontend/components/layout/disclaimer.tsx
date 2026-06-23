import { RiInformationLine } from "@remixicon/react"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export function Disclaimer() {
  return (
    <Alert>
      <RiInformationLine className="size-4" />
      <AlertTitle>Resultado educativo</AlertTitle>
      <AlertDescription>
        Estimaciones basadas en datos públicos NHANES con fines analíticos y educativos.
        No constituyen un diagnóstico clínico ni reemplazan la evaluación de un profesional de salud.
      </AlertDescription>
    </Alert>
  )
}
