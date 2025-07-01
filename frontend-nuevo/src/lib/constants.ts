// Lista predefinida de razones de reporte
export const RAZONES_REPORTE = [
  { value: "spam", label: "Spam o contenido repetitivo" },
  { value: "acoso", label: "Acoso o hostigamiento" },
  { value: "odio", label: "Discurso de odio" },
  { value: "violencia", label: "Amenazas o incitación a la violencia" },
  { value: "contenido_sexual", label: "Contenido sexual inapropiado" },
  { value: "desinformacion", label: "Desinformación o noticias falsas" },
  { value: "lenguaje_ofensivo", label: "Lenguaje ofensivo o vulgar" },
  { value: "suplantacion", label: "Suplantación de identidad" },
  { value: "contenido_ilegal", label: "Contenido ilegal" },
  { value: "fuera_de_tema", label: "Fuera del tema del foro" },
  { value: "publicidad", label: "Publicidad no autorizada" }
] as const

export type RazonReporte = typeof RAZONES_REPORTE[number]['value'] 