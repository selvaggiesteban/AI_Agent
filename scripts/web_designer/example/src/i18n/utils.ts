import es from './es.json';
import en from './en.json';

const dictionaries = { es, en } as const;

export type Locale = keyof typeof dictionaries;
export type TranslationKey = string;

export function getTranslations(locale: Locale) {
  const dict = dictionaries[locale] || dictionaries.es;
  return dict;
}

export function t(locale: Locale, key: string): string {
  const dict = getTranslations(locale);
  const keys = key.split('.');
  let value: any = dict;
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      return key;
    }
  }
  return typeof value === 'string' ? value : key;
}

export function getLocaleFromUrl(url: URL): Locale {
  const pathname = url.pathname;
  if (pathname.startsWith('/en')) return 'en';
  return 'es';
}

export function getOppositeLocale(locale: Locale): Locale {
  return locale === 'es' ? 'en' : 'es';
}

export function getLocalePrefix(locale: Locale): string {
  return locale === 'es' ? '/es' : '/en';
}

export function localizedPath(locale: Locale, path: string): string {
  const prefix = getLocalePrefix(locale);
  return `${prefix}${path}`;
}

const serviceSlugMap: Record<string, string> = {
  'software-a-medida': 'custom-software',
  'diseno-web-responsive': 'responsive-web-design',
  'posicionamiento-seo': 'seo-positioning',
  'posicionamiento-sem': 'sem-positioning',
  'e-mail-marketing': 'e-mail-marketing',
};

const cvSlugMap: Record<string, string> = {
  'desarrollador-web-full-stack': 'full-stack-web-developer',
  'ingeniero-en-software': 'software-engineer',
  'ingeniero-en-informatica': 'computer-science-engineer',
  'experto-en-posicionamiento-seo': 'seo-positioning-specialist',
};

const blogSlugMap: Record<string, string> = {
  'actualizaciones-web': 'website-updates',
  'agente-de-ia-tu-guia-definitiva-para-la-inteligencia-autonoma': 'ai-agent-your-ultimate-guide-to-autonomous-intelligence',
  'agentes-de-ia-guia-completa-de-sistemas-inteligentes': 'ai-agents-complete-guide-to-intelligent-systems',
  'alojar-web-en-cloudflare-pages-con-astro-y-resend': 'guide-to-hosting-a-website-on-cloudflare-pages-with-astro-and-resend',
  'analitica-web-guia-completa-para-dominar-tus-datos-online': 'web-analytics-complete-guide-to-mastering-your-online-data',
  'automatizacion-de-marketing-profesional': 'professional-marketing-automation',
  'claude-code-gratis': 'free-claude-code',
  'claude-vs-openclaw-guia-comparativa': 'claude-vs-openclaw-comparative-guide',
  'consultoria-seo-guia-definitiva-para-el-exito-digital': 'seo-consulting-the-ultimate-guide-to-digital-success',
  'copias-de-seguridad-tu-escudo-contra-la-perdida-de-datos': 'backups-your-shield-against-data-loss',
  'crea-tu-tienda-online-guia-completa-para-el-exito-digital': 'create-your-online-store-a-complete-guide-to-digital-success',
  'crear-clave-ssh-vps-en-hostinger': 'creating-an-ssh-key-for-a-vps-on-hostinger',
  'desarrollo-web-autonomo-la-guia-definitiva-para-el-exito-freelance': 'autonomous-web-development-the-ultimate-guide-to-freelance-success',
  'diseno-ux-ui-la-clave-para-productos-digitales-excepcionales': 'ux-ui-design-the-key-to-exceptional-digital-products',
  'diseno-web-la-guia-definitiva-para-tu-presencia-online': 'web-design-the-ultimate-guide-for-your-online-presence',
  'ejercito-de-juniors': 'army-of-juniors',
  'el-futuro-de-javascript-que-framework-dominara-en-2026': 'the-future-of-javascript-which-framework-will-dominate-in-2026',
  'experto-en-automatizacion-rpa': 'rpa-automation-expert',
  'experto-wordpress-tu-guia-definitiva-para-el-exito-digital': 'wordpress-expert-your-ultimate-guide-to-digital-success',
  'framework-python-2026-tendencias-y-predicciones-clave': 'python-framework-2026-key-trends-and-predictions',
  'gemini-cli': 'gemini-cli-in-vs-code-using-vertex-ai',
  'generacion-de-codigo-sintetico': 'synthetic-code-generation',
  'guia-oca-vs-correo-argentino': 'oca-vs-correo-argentino-complete-guide',
  'guia-optimizar-fotos-sitios-web': 'guide-to-optimizing-photos-for-websites',
  'guia-precios-mayoristas': 'wholesale-pricing-guide',
  'guia-programacion-y-desarrollo-web': 'web-programming-and-development-guide',
  'guia-servicio-de-oca-woocommerce': 'oca-service-for-woocommerce-complete-guide',
  'guia-api-woocommerce': 'woocommerce-rest-api-guide',
  'guia-woocommerce-desde-excel': 'woocommerce-product-management-via-excel',
  'guia-woocommerce': 'woocommerce-guide',
  'guia-wordpress': 'wordpress-guide',
  'hostinger-premium-web-hosting': 'premium-web-hosting-from-hostinger',
  'investigacion-de-palabras-clave-guia-completa-seo': 'keyword-research-complete-seo-guide',
  'landing-page': 'landing-page',
  'las-mejores-herramientas-de-marketing-digital-para-2024': 'the-best-digital-marketing-tools-for-2024',
  'mantenimiento-web-la-guia-definitiva-para-un-sitio-seguro-y-optimizado': 'web-maintenance-the-ultimate-guide-to-a-secure-and-optimized-website',
  'marketing-digital-en-lanus-guia-completa-para-tu-negocio': 'digital-marketing-in-lanus-complete-guide-for-your-business',
  'mercadolibre-woocommerce-sincronizar-envios-precios-stock': 'mercadolibre-and-woocommerce-how-to-sync-shipments-prices-and-stock-without-losing-sales',
  'monitorizacion-y-soporte-tecnico-web': 'web-monitoring-and-technical-support',
  'optimizacion-de-velocidad-web-guia-definitiva-para-el-exito': 'web-speed-optimization-the-ultimate-guide-to-success',
  'poisson-products-predecir-bugs-cumplir-deadlines': 'poisson-products-how-the-poisson-distribution-helps-me-meet-deadlines-at-200-quality',
  'posicionamiento-web-la-guia-definitiva-para-dominar-los-buscadores': 'web-positioning-the-ultimate-guide-to-mastering-search-engines',
  'prestashop-guia-completa-para-tu-tienda-online-exitosa': 'prestashop-complete-guide-to-your-successful-online-store',
  'prompts-para-ia': 'ai-prompts',
  'restauracion-de-sitio-web-guia-completa-para-recuperar-tu-presencia': 'website-restoration-complete-guide-to-recovering-your-online-presence',
  'seguridad-web-protegiendo-tu-fortaleza-digital': 'web-security-protecting-your-digital-fortress',
  'seo-de-contenidos-guia-completa-para-dominar-el-ranking': 'content-seo-complete-guide-to-mastering-the-rankings',
  'seo-local-guia-completa-para-dominar-la-busqueda-local': 'local-seo-complete-guide-to-mastering-local-search',
  'seo-local-la-guia-definitiva-para-atraer-clientes-cercanos': 'local-seo-the-ultimate-guide-to-attracting-nearby-customers',
  'seo-off-page-la-guia-definitiva-para-dominar-el-posicionamiento': 'off-page-seo-the-ultimate-guide-to-mastering-external-positioning',
  'seo-on-page-la-guia-definitiva-para-dominar-tu-web': 'on-page-seo-the-ultimate-guide-to-mastering-your-website',
  'servicios-de-programacion-y-desarrollo-web-mas-demandados-en-2026': 'most-in-demand-programming-and-web-development-services-in-2026',
  'sistema-multi-agente-con-ia': 'ai-multi-agent-system',
  'trafico-bots-supera-humanos-cloudflare': 'automated-traffic-dominates-the-web-bots-outnumber-humans-according-to-cloudflare',
  'woocommerce-la-guia-definitiva-para-tu-tienda-online': 'woocommerce-the-ultimate-guide-for-your-online-store',
  'wordpress-la-guia-definitiva-para-crear-tu-web-ideal': 'wordpress-the-ultimate-guide-to-creating-your-ideal-website',
};

function getMappedPath(pathname: string, from: Locale, to: Locale): string {
  const segments = pathname.split('/').filter(Boolean);
  if (segments.length < 2) return pathname;

  const section = segments[0];
  const slug = segments.slice(1).join('/');

  const map = section === 'services' ? serviceSlugMap
    : section === 'cv' ? cvSlugMap
    : section === 'blog' ? blogSlugMap
    : null;

  if (!map) return pathname;

  const mappedSlug = from === 'es'
    ? (map[slug] ?? slug)
    : Object.entries(map).find(([, v]) => v === slug)?.[0] ?? slug;

  const newPrefix = getLocalePrefix(to);
  return `${newPrefix}/${section}/${mappedSlug}`;
}

export function getLocalizedUrl(url: URL, targetLocale: Locale): string {
  const currentLocale = getLocaleFromUrl(url);
  const pathname = url.pathname;

  if (targetLocale === currentLocale) return pathname;

  let cleanPath = pathname;
  const prefix = getLocalePrefix(currentLocale);
  if (cleanPath.startsWith(prefix)) {
    cleanPath = cleanPath.slice(prefix.length) || '/';
  }

  const segments = cleanPath.split('/').filter(Boolean);
  if (segments.length >= 1 && ['services', 'cv', 'blog'].includes(segments[0])) {
    return getMappedPath(cleanPath, currentLocale, targetLocale);
  }

  return `${getLocalePrefix(targetLocale)}${cleanPath === '/' ? '/' : cleanPath}`;
}