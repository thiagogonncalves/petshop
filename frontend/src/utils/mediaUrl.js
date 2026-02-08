/**
 * Normaliza URL de mídia para sempre usar caminho relativo à origem.
 * Corrige o caso em que o backend retorna URL absoluta sem a porta (ex: https://72.60.147.9/media/...)
 * quando o app está em https://72.60.147.9:8082 - a img quebraria ao carregar.
 */
export function mediaUrl(url) {
  if (!url) return null
  if (typeof url !== 'string') return null
  if (url.startsWith('/')) return url
  try {
    const u = new URL(url)
    return u.pathname
  } catch {
    return url
  }
}
