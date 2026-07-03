// Genera el Informe Tecnico Ejecutivo (EFT) en Word. Requiere: npm install -g docx
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, LevelFormat, TableOfContents,
  HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
} = require("docx");

const OUT = "docs/Informe_Tecnico_Ejecutivo.docx";
const CONTENT_W = 9360; // US Letter, 1" margenes

// ---- helpers ---------------------------------------------------------------
const AZUL = "1A365D", AZULC = "2B6CB0", GRIS = "4A5568", HEADBG = "D5E8F0";
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] }); }
function p(t, opts = {}) { return new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: t, ...opts })] }); }
function bullet(t) { return new Paragraph({ numbering: { reference: "b", level: 0 }, spacing: { after: 40 }, children: [runs(t)].flat() }); }
function runs(t) {
  // permite **negrita** simple
  const parts = t.split(/\*\*(.+?)\*\*/g);
  return parts.map((s, i) => new TextRun({ text: s, bold: i % 2 === 1 }));
}
function cell(text, { head = false, w = 0, align = AlignmentType.LEFT } = {}) {
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: head ? { fill: HEADBG, type: ShadingType.CLEAR } : undefined,
    margins: { top: 60, bottom: 60, left: 110, right: 110 },
    children: [new Paragraph({ alignment: align, children: [new TextRun({ text, bold: head, size: 19 })] })],
  });
}
function table(headers, rows, widths) {
  const mk = (arr, head) => new TableRow({
    children: arr.map((c, i) => cell(String(c), { head, w: widths[i], align: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER })),
  });
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: widths,
    rows: [mk(headers, true), ...rows.map((r) => mk(r, false))],
  });
}
function img(path, w, h) {
  const ext = path.split(".").pop();
  return new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 80, after: 80 },
    children: [new ImageRun({ type: ext, data: fs.readFileSync(path),
      transformation: { width: w, height: h },
      altText: { title: "figura", description: "figura del informe", name: "fig" } })],
  });
}
function caption(t) { return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: t, italics: true, size: 18, color: GRIS })] }); }

// ---- estilos ---------------------------------------------------------------
const styles = {
  default: { document: { run: { font: "Arial", size: 21 } } },
  paragraphStyles: [
    { id: "Title", name: "Title", basedOn: "Normal", next: "Normal",
      run: { size: 52, bold: true, color: AZUL, font: "Arial" },
      paragraph: { spacing: { after: 120 } } },
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 30, bold: true, color: AZUL, font: "Arial" },
      paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 0 } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 24, bold: true, color: AZULC, font: "Arial" },
      paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 } },
  ],
};
const numbering = { config: [
  { reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 560, hanging: 280 } } } }] },
] };

// ---- contenido -------------------------------------------------------------
const cover = [
  new Paragraph({ spacing: { before: 1200 }, alignment: AlignmentType.CENTER,
    children: [new ImageRun({ type: "png", data: fs.readFileSync("assets/logo.png"),
      transformation: { width: 120, height: 120 }, altText: { title: "logo", description: "logo", name: "logo" } })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, style: "Title", spacing: { before: 240 }, children: [new TextRun("Informe Tecnico Ejecutivo")] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "DiabetesNHANES - Pipeline de Ciencia de Datos", size: 28, color: GRIS })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80 }, children: [new TextRun({ text: "Evaluacion Final Transversal - SCY1101 Programacion para la Ciencia de Datos", size: 20, color: GRIS })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600 }, children: [new TextRun({ text: "Equipo: apotheosisss, manueladmn, ElChacra", size: 20 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Repositorio: github.com/apotheosisss/PCS_EvParcial3", size: 18, color: AZULC })] }),
  new Paragraph({ children: [new PageBreak()] }),
];

const toc = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Tabla de contenidos")] }),
  new TableOfContents("Tabla de contenidos", { hyperlink: true, headingStyleRange: "1-2" }),
  new Paragraph({ children: [new PageBreak()] }),
];

const body = [
  // 1. Executive summary
  h1("1. Resumen ejecutivo"),
  p("DiabetesNHANES es una solucion de ciencia de datos de extremo a extremo que estima el riesgo de diabetes en poblacion adulta a partir de datos publicos de la encuesta NHANES 2021-2023 (CDC/NCHS). El sistema integra multiples fuentes, ejecuta un pipeline ETL reproducible con Kedro, entrena un portafolio de seis modelos de machine learning y expone los resultados mediante una API REST y un dashboard interactivo, todo containerizado con Docker y desplegable en la nube (AWS)."),
  p("Sobre 8.149 participantes adultos, el modelo seleccionado (regresion logistica calibrada) alcanza un ROC-AUC de 0,81 y un PR-AUC de 0,44, con una prevalencia real de diabetes del 16 %. El valor de negocio es un instrumento de tamizaje temprano y educativo que prioriza el recall (detectar casos) sobre la exactitud global, adecuado a un problema de salud publica con clases desbalanceadas.", { italics: false }),
  p("Aviso: la variable objetivo es una aproximacion analitica/educativa basada en criterios ADA; no constituye diagnostico clinico.", { italics: true, color: GRIS }),

  // 2. Contexto de negocio
  h1("2. Contexto de negocio"),
  bullet("**Problema:** la diabetes tipo 2 suele diagnosticarse tarde; un tamizaje temprano de bajo costo permite intervenir sobre factores de riesgo modificables."),
  bullet("**Objetivo:** estimar el riesgo/estado de diabetes usando variables demograficas, antropometricas, de estilo de vida y biomarcadores disponibles en NHANES."),
  bullet("**Impacto esperado:** priorizar poblacion para chequeos, dimensionar el problema por segmentos y ofrecer un simulador individual de riesgo."),

  // 3. Arquitectura
  h1("3. Arquitectura tecnica"),
  p("El proyecto usa Kedro como framework de orquestacion: catalogo de datos declarativo (las rutas viven en catalog.yml, no en el codigo) y el flujo dividido en pipelines independientes y reproducibles."),
  table(["Capa", "Componente", "Tecnologia"], [
    ["Ingesta", "8 archivos XPT + umbrales + auditoria", "Kedro, pandas, pyreadstat"],
    ["Limpieza/Features", "merge SEQN, imputacion, target, encoding", "pandas, numpy"],
    ["Modelado", "6 clasificadores + calibracion", "scikit-learn, xgboost, lightgbm, catboost"],
    ["Servicio", "API REST + dashboard", "FastAPI, Next.js"],
    ["Infraestructura", "containers + despliegue", "Docker Compose, AWS EC2, GitHub Actions"],
  ], [1900, 4260, 3200]),
  p(""),
  p("Pipelines Kedro: ingestion -> cleaning -> feature_engineering -> modeling -> reporting. Cada uno se ejecuta con kedro run y produce artefactos versionados por capa (data/01_raw ... data/08_reporting)."),

  // 4. ETL
  h1("4. Pipeline ETL y fuentes de datos"),
  p("Integra tres tipos de fuentes, cumpliendo el requisito de multi-fuente:"),
  bullet("**NHANES XPT (SAS transport):** DEMO, DIQ, BMX, GHB, GLU, PAQ, SLQ, BPXO del ciclo 2021-2023."),
  bullet("**Archivo propio de umbrales (CSV):** criterios clinicos parametrizados (A1C, glucosa, IMC, edad)."),
  bullet("**Base SQLite de auditoria:** tablas ingestion_audit y etl_audit que registran filas, columnas y nulos antes/despues por corrida."),
  p("Robustez: la union se hace por la llave SEQN con validacion que aborta si hay SEQN duplicado; validate_required_columns lanza error si falta una columna obligatoria; los codigos especiales NHANES (7, 9, 77, 99) se convierten a nulo antes de imputar."),

  // 5. Transformaciones avanzadas
  h1("5. Transformaciones avanzadas y optimizacion"),
  p("Se aplican tecnicas optimizadas para gran escala (modulo utils/transforms.py), con impacto medido sobre el dataset real:"),
  table(["Tecnica", "Metodo", "Resultado"], [
    ["Optimizacion memoria", "downcast dtypes + category", "2,74 MB -> 0,76 MB (-72 %)"],
    ["Broadcasting", "z-score vectorizado NumPy", "estandarizacion sin bucles"],
    ["Pivot", "pivot_table agregado", "prevalencia por segmento"],
    ["Reshape", "melt wide->long", "8149x44 -> 16298x3"],
    ["Chunking", "lectura por bloques", "memoria O(grupos)"],
  ], [2400, 3560, 3400]),

  // 6. Limpieza y target
  h1("6. Limpieza y construccion del target"),
  p("La variable diabetes_target se construye ANTES de imputar sus fuentes para no inventar positivos: vale 1 si DIQ010 = 1 (diagnostico reportado), o LBXGH >= 6,5 (A1C), o LBXGLU >= 126 (glucosa en ayunas); 0 en caso contrario. Las filas sin ninguna fuente determinable se descartan en lugar de asumir un 0."),
  p("Decision clave (revision de calidad): se detecto y corrigio una fuga de datos excluyendo los biomarcadores que definen el target (LBXGH, LBXGLU y derivados) del conjunto de features, evitando metricas infladas artificialmente."),

  // 7. Modelos
  h1("7. Portafolio de modelos ML"),
  p("Se entrenaron y compararon seis clasificadores dentro de un Pipeline ajustado solo con train (sin fuga), con class_weight balanceado y seleccion por PR-AUC, metrica honesta ante clases desbalanceadas (prevalencia 16 %)."),
  table(["Modelo", "Accuracy", "Recall", "F1", "ROC-AUC", "PR-AUC"], [
    ["Logistic Regression *", "0,723", "0,747", "0,463", "0,816", "0,441"],
    ["Random Forest", "0,765", "0,678", "0,480", "0,811", "0,403"],
    ["Gradient Boosting", "0,742", "0,705", "0,466", "0,814", "0,423"],
    ["XGBoost", "0,734", "0,690", "0,454", "0,808", "0,414"],
    ["LightGBM", "0,758", "0,590", "0,438", "0,797", "0,395"],
    ["CatBoost", "0,748", "0,655", "0,454", "0,807", "0,421"],
  ], [2760, 1320, 1320, 1320, 1320, 1320]),
  caption("* Modelo seleccionado (mayor PR-AUC). Calibrado con isotonic regression, umbral optimo 0,31, Brier 0,11."),
  p("Interpretacion: la regresion logistica gana en PR-AUC y recall, detectando ~75 % de los casos positivos; el resto de modelos ofrece mayor accuracy pero menor recall, poco util cuando el costo de no detectar un caso es alto."),
  img("data/08_reporting/confusion_matrix.png", 260, 230),
  caption("Figura 1. Matriz de confusion (umbral 0,31): TN=1109, FP=260, FN=99, TP=162."),
  img("data/08_reporting/feature_importance.png", 380, 300),
  caption("Figura 2. Importancia de variables del modelo."),

  // 8. API y dashboard
  h1("8. API REST y dashboard"),
  p("La API FastAPI expone salud, metadatos, metricas y prediccion (individual y por lote), documentada automaticamente en /docs. Si el modelo no existe responde 503 en lugar de caerse."),
  table(["Endpoint", "Metodo", "Descripcion"], [
    ["/health", "GET", "estado del servicio y del modelo"],
    ["/model-info", "GET", "nombre y version del modelo"],
    ["/metrics", "GET", "metricas del modelo entrenado"],
    ["/predict", "POST", "prediccion de riesgo individual"],
    ["/predict/batch", "POST", "prediccion por lote"],
  ], [3000, 1560, 4800]),
  p(""),
  p("El dashboard (Next.js) ofrece tres vistas por audiencia: Ejecutiva (KPIs y distribuciones), Tecnica (metricas, matriz de confusion, importancia) y Operativa (filtros, descarga CSV y simulador de prediccion)."),

  // 9. Containerizacion, CI/CD y AWS
  h1("9. Containerizacion, CI/CD y despliegue"),
  bullet("**Docker:** cuatro servicios (kedro-etl, api, dashboard, db) orquestados con docker-compose; depends_on para el orden, volumen data/ compartido e imagenes python:3.11-slim optimizadas por capas."),
  bullet("**CI/CD:** workflow de GitHub Actions (.github/workflows/ci.yml) que corre lint, tests (pytest), build del frontend y build de la imagen Docker en cada push/PR a develop y main."),
  bullet("**AWS:** despliegue en EC2 + docker-compose documentado en docs/guia_despliegue_aws.md, con scripts de bootstrap (user_data.sh) y deploy (deploy.sh) para AWS Academy Learner Lab."),

  // 10. KPIs
  h1("10. KPIs y analisis de resultados"),
  table(["KPI", "Valor"], [
    ["Participantes analizados", "8.149"],
    ["Prevalencia de diabetes (target)", "16,0 %"],
    ["Recall del modelo (casos detectados)", "~75 %"],
    ["ROC-AUC / PR-AUC", "0,81 / 0,44"],
    ["Reduccion de memoria (ETL)", "-72 %"],
    ["Modelos comparados", "6"],
  ], [6000, 3360]),

  // 11. Colaboracion
  h1("11. Colaboracion y gestion de proyecto"),
  p("Estrategia Git Flow simplificada: main estable, develop de integracion y una rama feature por responsabilidad. Ninguna rama feature se integro directo a main; todo paso por Pull Request a develop con revision. Se registraron 8 Pull Requests y un revert (PR #4) que evidencia que el control de calidad detecto y corrigio un merge incorrecto."),
  p("La colaboracion se apoyo en un contrato de interfaz (docs/CONTRATO_FEATURE_B.md) que fijo las columnas del dataset entre ramas, permitiendo desarrollar modelado, API y dashboard en paralelo."),

  // 12. Limitaciones
  h1("12. Limitaciones y mejoras futuras"),
  bullet("El target es una etiqueta educativa (criterios ADA), no un diagnostico clinico; algunas variables son autoinformadas."),
  bullet("NHANES es una encuesta poblacional transversal, no una historia clinica longitudinal."),
  bullet("Mejoras: CI que bloquee merges con tests en rojo, build multi-stage, monitoreo de data drift y reentrenamiento programado."),

  // Anexos
  new Paragraph({ children: [new PageBreak()] }),
  h1("Anexos"),
  h2("A. Estructura del repositorio"),
  p("/src (pipelines Kedro), /api (FastAPI), /frontend (Next.js), /dashboards, /docker, /docs, /tests, /repo (evidencias Git), /data, /scripts, /deploy/aws.", { font: "Arial" }),
  h2("B. Reproducibilidad"),
  p("cp .env.example .env  ->  python scripts/download_nhanes.py  ->  kedro run  ->  docker compose -f docker/docker-compose.yml up --build"),
  h2("C. Evidencias de pruebas"),
  p("Suite pytest sobre ingesta, limpieza, features, modelo y transformaciones avanzadas; ejecutada localmente y en CI (GitHub Actions)."),
];

const doc = new Document({
  styles, numbering,
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "DiabetesNHANES - Informe Tecnico Ejecutivo", size: 16, color: GRIS })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Pagina ", size: 16, color: GRIS }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GRIS })] })] }) },
    children: [...cover, ...toc, ...body],
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("[OK] " + OUT); });
