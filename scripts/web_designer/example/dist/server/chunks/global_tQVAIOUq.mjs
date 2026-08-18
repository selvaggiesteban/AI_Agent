globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { L as createRenderInstruction, K as renderTemplate, a0 as addAttribute, v as maybeRenderHead, bm as renderSlot } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
async function renderScript(result, id) {
  const inlined = result.inlinedScripts.get(id);
  let content = "";
  if (inlined != null) {
    if (inlined) {
      content = `<script type="module">${inlined}<\/script>`;
    }
  } else {
    const resolved = await result.resolve(id);
    content = `<script type="module" src="${result.userAssetsBase ? (result.base === "/" ? "" : result.base) + result.userAssetsBase : ""}${resolved}"><\/script>`;
  }
  return createRenderInstruction({ type: "script", id, content });
}
var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$SEO = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$SEO;
  const {
    title,
    description,
    canonical = Astro2.url.href,
    image = "/og-image.svg",
    noindex = false
  } = Astro2.props;
  const siteName = "selvaggiesteban.dev";
  const fullTitle = `${title} | ${siteName}`;
  return renderTemplate(_a || (_a = __template(["<!-- Basic Meta Tags --><title>", '</title><meta name="description"', '><link rel="canonical"', ">", '<!-- Open Graph / Facebook --><meta property="og:type" content="website"><meta property="og:url"', '><meta property="og:title"', '><meta property="og:description"', '><meta property="og:image"', '><!-- Twitter --><meta property="twitter:card" content="summary_large_image"><meta property="twitter:url"', '><meta property="twitter:title"', '><meta property="twitter:description"', '><meta property="twitter:image"', '><!-- JSON-LD --><script type="application/ld+json">\n  {\n    "@context": "https://schema.org",\n    "@type": "WebSite",\n    "name": "selvaggiesteban.dev",\n    "url": "https://selvaggiesteban.dev/"\n  }\n<\/script>'])), fullTitle, addAttribute(description, "content"), addAttribute(canonical, "href"), noindex && renderTemplate`<meta name="robots" content="noindex, nofollow">`, addAttribute(Astro2.url, "content"), addAttribute(fullTitle, "content"), addAttribute(description, "content"), addAttribute(new URL(image, Astro2.site), "content"), addAttribute(Astro2.url, "content"), addAttribute(fullTitle, "content"), addAttribute(description, "content"), addAttribute(new URL(image, Astro2.site), "content"));
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/seo/SEO.astro", void 0);
const $$Container = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Container;
  const { class: className } = Astro2.props;
  return renderTemplate`${maybeRenderHead()}<div${addAttribute(["max-w-[1280px] mx-auto px-lg md:px-xxl", className], "class:list")}> ${renderSlot($$result, $$slots["default"])} </div>`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/Container.astro", void 0);
const $$Button = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Button;
  const { variant = "primary", class: className, href, type = "button", ...rest } = Astro2.props;
  const variants = {
    primary: "btn-primary",
    secondary: "btn-secondary",
    magenta: "btn-magenta"
  };
  const Tag = href ? "a" : "button";
  return renderTemplate`${renderComponent($$result, "Tag", Tag, { "href": href, "type": !href ? type : void 0, "class:list": [variants[variant], className], ...rest }, { "default": ($$result2) => renderTemplate` ${renderSlot($$result2, $$slots["default"])} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/Button.astro", void 0);
const nav$1 = { "inicio": "Inicio", "sobreMi": "Sobre mí", "servicios": "Servicios", "blog": "Blog", "contacto": "Contacto", "empezar": "Empezar", "empezarAhora": "Empezar ahora", "menu": "Menú" };
const services$1 = { "softwareAMedida": "Software a medida", "disenoWeb": "Diseño web responsive", "seo": "Posicionamiento SEO", "sem": "Posicionamiento SEM", "emailMarketing": "E-mail marketing" };
const footer$1 = { "bio": "Ingeniero en Informática especializado en Ingeniería en Software", "ingenieroInformatica": "Ingeniero en Informática UBA", "ingenieroSoftware": "Ingeniero en software", "desarrolladorFullStack": "Desarrollador Web Full-Stack", "expertoSEO": "Experto en posicionamiento SEO", "contacto": "Contacto", "email": "E-mail:", "telefono": "Teléfono:", "servicios": "Servicios", "guiasSEO": "Guías SEO & Marketing", "desarrolloIA": "Desarrollo & Inteligencia Artificial", "privacidad": "Privacidad", "cookies": "Cookies" };
const cookie$1 = { "title": "Uso de Cookies", "message": "Uso cookies técnicas para que mi web funcione y analíticas para entender cómo interactúas con ella. Solo activaré las analíticas si me das tu consentimiento.", "readMore": "Leer política completa.", "accept": "Aceptar todas", "reject": "Rechazar no esenciales" };
const contact$1 = { "heading": "¿Hablamos sobre tu proyecto?", "subtitle": "Completa el formulario y me pondré en contacto contigo lo antes posible.", "nombre": "Nombre", "email": "Email", "mensaje": "Mensaje", "privacyPrefix": "He leído y acepto la", "privacyLink": "Política de Privacidad", "privacySuffix": "y el tratamiento de mis datos personales.", "submit": "Enviar mensaje", "captchaWait": "Por favor, espera a que el captcha de seguridad se complete.", "sending": "Enviando...", "errorSend": "No se pudo enviar el mensaje.", "errorConnection": "Error de conexión. Inténtalo de nuevo." };
const whatsapp$1 = { "message": "Hola! Me gustaría recibir más información.", "ariaLabel": "Contactar por WhatsApp" };
const author$1 = { "bio": "Ingeniero informático especializado en ingeniería de software", "description": "Con más de 10 años de trayectoria, construyo aplicaciones web responsive y escalables, ayudando a negocios a destacar en el mundo digital con productos que cargan instantáneamente y están optimizados para motores de búsqueda (SEO).", "cta": "Hablemos sobre tu proyecto" };
const reviews$1 = { "heading": "Reseñas de clientes", "subtitle": "Lo que dicen quienes ya confían en mi ingeniería de excelencia.", "prev": "Anterior", "next": "Siguiente", "readMore": "Leer más en Google" };
const recommended$1 = { "heading": "Recomendado para usted", "badge": "Artículo", "placeholder": "Lectura recomendada", "prev": "Anterior", "next": "Siguiente", "leerMas": "Leer más" };
const recent$1 = { "heading": "Publicaciones recientes", "description": "Compartiendo código, algoritmos y avances sobre ingeniería en software e IA.", "viewCode": "Ver código fuente →", "githubRepo": "Repositorio en GitHub", "repos": { "30_days_coding": "Desafío de programación de 30 días con algoritmos, estructuras de datos y resolución de problemas.", "spec-driven": "Metodología y herramientas para construir aplicaciones robustas a partir de especificaciones estrictas.", "hands-on-ai": "Implementaciones prácticas de modelos de Inteligencia Artificial, agentes LLM e ingeniería de prompts." } };
const skills$1 = { "heading": "Tecnologías de vanguardia", "subtitle": "Código optimizado para el máximo rendimiento.", "categories": { "frontend": "Desarrollo frontend", "backend": "Desarrollo backend", "apis": "APIs e integraciones", "databases": "Bases de datos", "infra": "Despliegue e infraestructura", "ai": "Inteligencia artificial y automatizaciones", "productivity": "Productividad", "cms": "Gestión de contenido", "seo": "SEO y analítica" } };
const toc$1 = { "heading": "Índice de Contenidos", "filterWords": ["tabla de contenido", "índice de contenido"] };
const home$1 = { "title": "Ingeniero en Informática especializado en Ingeniería en Software", "description": "Ingeniería en Informática profesional desde Buenos Aires Argentina - Ingeniero en Informática UBA", "role": "Ingeniero en Informática", "empezarAhora": "Empezar ahora", "verServicios": "Ver servicios" };
const about$1 = { "title": "Esteban Selvaggi Ingeniero en Informática UBA", "description": "Conoce más sobre Esteban Selvaggi, ingeniero en software especializado en desarrollo full-stack, con 10 años de experiencia.", "heading": "Sobre mí", "bio1": "Soy un apasionado de la ingeniería de software y el diseño web, enfocado en crear experiencias digitales excepcionales que combinan una estética cuidada y un rendimiento sobresaliente.", "bio2": "Con más de 10 años de trayectoria, construyo aplicaciones web responsive y escalables, ayudando a negocios y profesionales a destacar en el mundo digital con productos que cargan instantáneamente y están optimizados para motores de búsqueda y altas tasas de conversión.", "experiencia": "Experiencia Laboral", "educacion": "Educación", "copyLink": "Copiar Enlace", "print": "Imprimir", "shareEmail": "Compartir por Email", "shareWhatsApp": "Compartir por WhatsApp", "shareTelegram": "Compartir por Telegram", "linkCopied": "Enlace copiado al portapapeles;", "email": "E-mail:", "telefono": "Teléfono:", "linkedin": "LinkedIn:", "github": "GitHub:", "actualidad": "actualidad" };
const contactPage$1 = { "title": "Contacto", "description": "Ponte en contacto con nosotros para discutir tu próximo proyecto web.", "heading": "Hablemos.", "subtitle": "¿Tienes un proyecto en mente o simplemente quieres saludar? Completa el formulario y te responderé lo antes posible." };
const thankYou$1 = { "title": "¡Gracias!", "description": "Gracias por ponerte en contacto con nosotros.", "heading": "¡Mensaje enviado!", "message": "He recibido tu mensaje y me pondré en contacto contigo a la brevedad.", "volver": "Volver al inicio" };
const blog$1 = { "title": "Blog de Ingeniería y SEO", "description": "Artículos técnicos sobre ingeniería de software, automatización con inteligencia artificial y estrategias avanzadas de posicionamiento web (SEO/SEM).", "heading": "Blog", "subtitle": "Reflexiones, tutoriales y estrategias sobre ingeniería en software, IA y posicionamiento web.", "featured": "Destacado", "readArticle": "Leer artículo", "readMore": "Leer más" };
const servicesPage$1 = { "title": "Servicios", "description": "Explora las soluciones de diseño y desarrollo web que ofrecemos.", "heading": "Servicios de consultores en informática y suministros de programas de informática", "verServicio": "Ver servicio", "viewService": "Ver servicio" };
const login$1 = { "title": "Acceso Restringido", "heading": "Acceso Restringido", "description": "Inicia sesión para continuar.", "subtitle": "Ingresa la contraseña maestra para acceder al CRM.", "password": "Contraseña", "submit": "Ingresar al sistema", "errorPassword": "Contraseña incorrecta.", "errorConnection": "Error de conexión" };
const share$1 = { "whatsapp": "Compartir por WhatsApp", "twitter": "Compartir en X (Twitter)", "x": "Compartir en X (Twitter)", "linkedin": "Compartir en LinkedIn", "telegram": "Compartir por Telegram", "copyLink": "Copiar enlace", "copied": "¡Copiado!" };
const breadcrumbs$1 = { "home": "Inicio", "blog": "Blog", "servicios": "Servicios" };
const es = {
  nav: nav$1,
  services: services$1,
  footer: footer$1,
  cookie: cookie$1,
  contact: contact$1,
  whatsapp: whatsapp$1,
  author: author$1,
  reviews: reviews$1,
  recommended: recommended$1,
  recent: recent$1,
  skills: skills$1,
  toc: toc$1,
  home: home$1,
  about: about$1,
  contactPage: contactPage$1,
  thankYou: thankYou$1,
  blog: blog$1,
  servicesPage: servicesPage$1,
  login: login$1,
  share: share$1,
  breadcrumbs: breadcrumbs$1
};
const nav = { "inicio": "Home", "sobreMi": "About", "servicios": "Services", "blog": "Blog", "contacto": "Contact", "empezar": "Get Started", "empezarAhora": "Get Started Now", "menu": "Menu" };
const services = { "softwareAMedida": "Custom Software", "disenoWeb": "Responsive Web Design", "seo": "SEO Positioning", "sem": "SEM Advertising", "emailMarketing": "Email Marketing" };
const footer = { "bio": "Computer Engineer specialized in Software Engineering", "ingenieroInformatica": "Computer Engineer — UBA", "ingenieroSoftware": "Software Engineer", "desarrolladorFullStack": "Full-Stack Web Developer", "expertoSEO": "SEO Positioning Specialist", "contacto": "Contact", "email": "Email:", "telefono": "Phone:", "servicios": "Services", "guiasSEO": "SEO & Marketing Guides", "desarrolloIA": "Development & Artificial Intelligence", "privacidad": "Privacy", "cookies": "Cookies" };
const cookie = { "title": "Cookie Usage", "message": "I use technical cookies to make my website work and analytics to understand how you interact with it. I will only enable analytics if you give your consent.", "readMore": "Read full policy.", "accept": "Accept all", "reject": "Reject non-essential" };
const contact = { "heading": "Let's talk about your project?", "subtitle": "Fill out the form and I'll get back to you as soon as possible.", "nombre": "Name", "email": "Email", "mensaje": "Message", "privacyPrefix": "I have read and accept the", "privacyLink": "Privacy Policy", "privacySuffix": "and the processing of my personal data.", "submit": "Send message", "captchaWait": "Please wait for the security captcha to complete.", "sending": "Sending...", "errorSend": "Could not send the message.", "errorConnection": "Connection error. Please try again." };
const whatsapp = { "message": "Hi! I'd like to get more information.", "ariaLabel": "Contact via WhatsApp" };
const author = { "bio": "Computer Engineer specialized in Software Engineering", "description": "With over 10 years of experience, I build responsive and scalable web applications, helping businesses stand out in the digital world with products that load instantly and are optimized for search engines (SEO).", "cta": "Let's talk about your project" };
const reviews = { "heading": "Client Reviews", "subtitle": "What those who trust my engineering excellence have to say.", "prev": "Previous", "next": "Next", "readMore": "Read more on Google" };
const recommended = { "heading": "Recommended for you", "badge": "Article", "placeholder": "Recommended reading", "prev": "Previous", "next": "Next", "leerMas": "Read more" };
const recent = { "heading": "Recent Publications", "description": "Sharing code, algorithms, and advances in Software Engineering and AI.", "viewCode": "View source code →", "githubRepo": "GitHub Repository", "repos": { "30_days_coding": "30-day programming challenge with algorithms, data structures, and problem solving.", "spec-driven": "Methodology and tools for building robust applications from strict specifications.", "hands-on-ai": "Practical implementations of Artificial Intelligence models, LLM agents, and prompt engineering." } };
const skills = { "heading": "Cutting-Edge Technologies", "subtitle": "Code optimized for maximum performance.", "categories": { "frontend": "Frontend Development", "backend": "Backend Development", "apis": "APIs & Integrations", "databases": "Databases", "infra": "Deployment & Infrastructure", "ai": "Artificial Intelligence & Automations", "productivity": "Productivity", "cms": "Content Management", "seo": "SEO & Analytics" } };
const toc = { "heading": "Table of Contents", "filterWords": ["table of contents", "table of content"] };
const home = { "title": "Computer Engineer specialized in Software Engineering", "description": "Professional Computer Engineering from Buenos Aires Argentina - Computer Engineer UBA", "role": "Computer Engineer", "empezarAhora": "Get Started Now", "verServicios": "View Services" };
const about = { "title": "Esteban Selvaggi Computer Engineer UBA", "description": "Learn more about Esteban Selvaggi, a software engineer specialized in full-stack development with 10 years of experience.", "heading": "About Me", "bio1": "I am passionate about software engineering and web design, focused on creating exceptional digital experiences that combine careful aesthetics with outstanding performance.", "bio2": "With over 10 years of experience, I build responsive and scalable web applications, helping businesses and professionals stand out in the digital world with products that load instantly and are optimized for search engines and high conversion rates.", "experiencia": "Work Experience", "educacion": "Education", "copyLink": "Copy Link", "print": "Print", "shareEmail": "Share by Email", "shareWhatsApp": "Share via WhatsApp", "shareTelegram": "Share via Telegram", "linkCopied": "Link copied to clipboard;", "email": "Email:", "telefono": "Phone:", "linkedin": "LinkedIn:", "github": "GitHub:", "actualidad": "present" };
const contactPage = { "title": "Contact", "description": "Get in touch with us to discuss your next web project.", "heading": "Let's talk.", "subtitle": "Have a project in mind or just want to say hello? Fill out the form and I'll get back to you as soon as possible." };
const thankYou = { "title": "Thank You!", "description": "Thank you for getting in touch with us.", "heading": "Message Sent!", "message": "I have received your message and will get back to you shortly.", "volver": "Back to Home" };
const blog = { "title": "Engineering & SEO Blog", "description": "Technical articles on software engineering, artificial intelligence automation, and advanced web positioning strategies (SEO/SEM).", "heading": "Blog", "subtitle": "Reflections, tutorials, and strategies on software engineering, AI, and web positioning.", "destacado": "Featured", "leerArticulo": "Read article", "leerMas": "Read more" };
const servicesPage = { "title": "Services", "description": "Explore the web design and development solutions we offer.", "heading": "IT Consulting Services & Software Supply", "verServicio": "View service", "viewService": "View service" };
const login = { "title": "Restricted Access", "heading": "Restricted Access", "description": "Log in to continue.", "subtitle": "Enter the master password to access the CRM.", "password": "Password", "submit": "Log in", "errorPassword": "Incorrect password.", "errorConnection": "Connection error" };
const share = { "whatsapp": "Share via WhatsApp", "twitter": "Share on X (Twitter)", "x": "Share on X (Twitter)", "linkedin": "Share on LinkedIn", "telegram": "Share via Telegram", "copyLink": "Copy link", "copied": "Copied!" };
const breadcrumbs = { "home": "Home", "blog": "Blog", "servicios": "Services" };
const en = {
  nav,
  services,
  footer,
  cookie,
  contact,
  whatsapp,
  author,
  reviews,
  recommended,
  recent,
  skills,
  toc,
  home,
  about,
  contactPage,
  thankYou,
  blog,
  servicesPage,
  login,
  share,
  breadcrumbs
};
const dictionaries = { es, en };
function getTranslations(locale) {
  const dict = dictionaries[locale] || dictionaries.es;
  return dict;
}
function t(locale, key) {
  const dict = getTranslations(locale);
  const keys = key.split(".");
  let value = dict;
  for (const k of keys) {
    if (value && typeof value === "object" && k in value) {
      value = value[k];
    } else {
      return key;
    }
  }
  return typeof value === "string" ? value : key;
}
function getLocaleFromUrl(url) {
  const pathname = url.pathname;
  if (pathname.startsWith("/en")) return "en";
  return "es";
}
function getOppositeLocale(locale) {
  return locale === "es" ? "en" : "es";
}
function getLocalePrefix(locale) {
  return locale === "es" ? "/es" : "/en";
}
const serviceSlugMap = {
  "software-a-medida": "custom-software",
  "diseno-web-responsive": "responsive-web-design",
  "posicionamiento-seo": "seo-positioning",
  "posicionamiento-sem": "sem-positioning",
  "e-mail-marketing": "e-mail-marketing"
};
const cvSlugMap = {
  "desarrollador-web-full-stack": "full-stack-web-developer",
  "ingeniero-en-software": "software-engineer",
  "ingeniero-en-informatica": "computer-science-engineer",
  "experto-en-posicionamiento-seo": "seo-positioning-specialist"
};
const blogSlugMap = {
  "actualizaciones-web": "website-updates",
  "agente-de-ia-tu-guia-definitiva-para-la-inteligencia-autonoma": "ai-agent-your-ultimate-guide-to-autonomous-intelligence",
  "agentes-de-ia-guia-completa-de-sistemas-inteligentes": "ai-agents-complete-guide-to-intelligent-systems",
  "alojar-web-en-cloudflare-pages-con-astro-y-resend": "guide-to-hosting-a-website-on-cloudflare-pages-with-astro-and-resend",
  "analitica-web-guia-completa-para-dominar-tus-datos-online": "web-analytics-complete-guide-to-mastering-your-online-data",
  "automatizacion-de-marketing-profesional": "professional-marketing-automation",
  "claude-code-gratis": "free-claude-code",
  "claude-vs-openclaw-guia-comparativa": "claude-vs-openclaw-comparative-guide",
  "consultoria-seo-guia-definitiva-para-el-exito-digital": "seo-consulting-the-ultimate-guide-to-digital-success",
  "copias-de-seguridad-tu-escudo-contra-la-perdida-de-datos": "backups-your-shield-against-data-loss",
  "crea-tu-tienda-online-guia-completa-para-el-exito-digital": "create-your-online-store-a-complete-guide-to-digital-success",
  "crear-clave-ssh-vps-en-hostinger": "creating-an-ssh-key-for-a-vps-on-hostinger",
  "desarrollo-web-autonomo-la-guia-definitiva-para-el-exito-freelance": "autonomous-web-development-the-ultimate-guide-to-freelance-success",
  "diseno-ux-ui-la-clave-para-productos-digitales-excepcionales": "ux-ui-design-the-key-to-exceptional-digital-products",
  "diseno-web-la-guia-definitiva-para-tu-presencia-online": "web-design-the-ultimate-guide-for-your-online-presence",
  "ejercito-de-juniors": "army-of-juniors",
  "el-futuro-de-javascript-que-framework-dominara-en-2026": "the-future-of-javascript-which-framework-will-dominate-in-2026",
  "experto-en-automatizacion-rpa": "rpa-automation-expert",
  "experto-wordpress-tu-guia-definitiva-para-el-exito-digital": "wordpress-expert-your-ultimate-guide-to-digital-success",
  "framework-python-2026-tendencias-y-predicciones-clave": "python-framework-2026-key-trends-and-predictions",
  "gemini-cli": "gemini-cli-in-vs-code-using-vertex-ai",
  "generacion-de-codigo-sintetico": "synthetic-code-generation",
  "guia-oca-vs-correo-argentino": "oca-vs-correo-argentino-complete-guide",
  "guia-optimizar-fotos-sitios-web": "guide-to-optimizing-photos-for-websites",
  "guia-precios-mayoristas": "wholesale-pricing-guide",
  "guia-programacion-y-desarrollo-web": "web-programming-and-development-guide",
  "guia-servicio-de-oca-woocommerce": "oca-service-for-woocommerce-complete-guide",
  "guia-api-woocommerce": "woocommerce-rest-api-guide",
  "guia-woocommerce-desde-excel": "woocommerce-product-management-via-excel",
  "guia-woocommerce": "woocommerce-guide",
  "guia-wordpress": "wordpress-guide",
  "hostinger-premium-web-hosting": "premium-web-hosting-from-hostinger",
  "investigacion-de-palabras-clave-guia-completa-seo": "keyword-research-complete-seo-guide",
  "landing-page": "landing-page",
  "las-mejores-herramientas-de-marketing-digital-para-2024": "the-best-digital-marketing-tools-for-2024",
  "mantenimiento-web-la-guia-definitiva-para-un-sitio-seguro-y-optimizado": "web-maintenance-the-ultimate-guide-to-a-secure-and-optimized-website",
  "marketing-digital-en-lanus-guia-completa-para-tu-negocio": "digital-marketing-in-lanus-complete-guide-for-your-business",
  "mercadolibre-woocommerce-sincronizar-envios-precios-stock": "mercadolibre-and-woocommerce-how-to-sync-shipments-prices-and-stock-without-losing-sales",
  "monitorizacion-y-soporte-tecnico-web": "web-monitoring-and-technical-support",
  "optimizacion-de-velocidad-web-guia-definitiva-para-el-exito": "web-speed-optimization-the-ultimate-guide-to-success",
  "poisson-products-predecir-bugs-cumplir-deadlines": "poisson-products-how-the-poisson-distribution-helps-me-meet-deadlines-at-200-quality",
  "posicionamiento-web-la-guia-definitiva-para-dominar-los-buscadores": "web-positioning-the-ultimate-guide-to-mastering-search-engines",
  "prestashop-guia-completa-para-tu-tienda-online-exitosa": "prestashop-complete-guide-to-your-successful-online-store",
  "prompts-para-ia": "ai-prompts",
  "restauracion-de-sitio-web-guia-completa-para-recuperar-tu-presencia": "website-restoration-complete-guide-to-recovering-your-online-presence",
  "seguridad-web-protegiendo-tu-fortaleza-digital": "web-security-protecting-your-digital-fortress",
  "seo-de-contenidos-guia-completa-para-dominar-el-ranking": "content-seo-complete-guide-to-mastering-the-rankings",
  "seo-local-guia-completa-para-dominar-la-busqueda-local": "local-seo-complete-guide-to-mastering-local-search",
  "seo-local-la-guia-definitiva-para-atraer-clientes-cercanos": "local-seo-the-ultimate-guide-to-attracting-nearby-customers",
  "seo-off-page-la-guia-definitiva-para-dominar-el-posicionamiento": "off-page-seo-the-ultimate-guide-to-mastering-external-positioning",
  "seo-on-page-la-guia-definitiva-para-dominar-tu-web": "on-page-seo-the-ultimate-guide-to-mastering-your-website",
  "servicios-de-programacion-y-desarrollo-web-mas-demandados-en-2026": "most-in-demand-programming-and-web-development-services-in-2026",
  "sistema-multi-agente-con-ia": "ai-multi-agent-system",
  "trafico-bots-supera-humanos-cloudflare": "automated-traffic-dominates-the-web-bots-outnumber-humans-according-to-cloudflare",
  "woocommerce-la-guia-definitiva-para-tu-tienda-online": "woocommerce-the-ultimate-guide-for-your-online-store",
  "wordpress-la-guia-definitiva-para-crear-tu-web-ideal": "wordpress-the-ultimate-guide-to-creating-your-ideal-website"
};
function getMappedPath(pathname, from, to) {
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length < 2) return pathname;
  const section = segments[0];
  const slug = segments.slice(1).join("/");
  const map = section === "services" ? serviceSlugMap : section === "cv" ? cvSlugMap : section === "blog" ? blogSlugMap : null;
  if (!map) return pathname;
  const mappedSlug = from === "es" ? map[slug] ?? slug : Object.entries(map).find(([, v]) => v === slug)?.[0] ?? slug;
  const newPrefix = getLocalePrefix(to);
  return `${newPrefix}/${section}/${mappedSlug}`;
}
function getLocalizedUrl(url, targetLocale) {
  const currentLocale = getLocaleFromUrl(url);
  const pathname = url.pathname;
  if (targetLocale === currentLocale) return pathname;
  let cleanPath = pathname;
  const prefix = getLocalePrefix(currentLocale);
  if (cleanPath.startsWith(prefix)) {
    cleanPath = cleanPath.slice(prefix.length) || "/";
  }
  const segments = cleanPath.split("/").filter(Boolean);
  if (segments.length >= 1 && ["services", "cv", "blog"].includes(segments[0])) {
    return getMappedPath(cleanPath, currentLocale, targetLocale);
  }
  return `${getLocalePrefix(targetLocale)}${cleanPath === "/" ? "/" : cleanPath}`;
}
const $$LanguageSwitcher = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$LanguageSwitcher;
  const currentUrl = Astro2.url;
  const currentLocale = getLocaleFromUrl(currentUrl);
  const oppositeLocale = getOppositeLocale(currentLocale);
  const targetUrl = getLocalizedUrl(currentUrl, oppositeLocale);
  return renderTemplate`${maybeRenderHead()}<a${addAttribute(targetUrl, "href")} class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold uppercase tracking-widest border border-hairline rounded-full hover:bg-ink hover:text-white transition-colors text-ink"${addAttribute(oppositeLocale === "en" ? "Switch to English" : "Cambiar a Español", "aria-label")}> <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"> <circle cx="12" cy="12" r="10"></circle> <path d="M2 12h20"></path> <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path> </svg> ${oppositeLocale === "en" ? "EN" : "ES"} </a>`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/LanguageSwitcher.astro", void 0);
const $$Navbar = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Navbar;
  const locale = getLocaleFromUrl(Astro2.url);
  const lang = locale;
  const navLinks = [
    { href: locale === "es" ? "/es/" : "/en/", label: t(lang, "nav.inicio") },
    { href: locale === "es" ? "/es/about" : "/en/about", label: t(lang, "nav.sobreMi") },
    {
      label: t(lang, "nav.servicios"),
      href: locale === "es" ? "/es/services" : "/en/services",
      dropdown: [
        { href: locale === "es" ? "/es/services/software-a-medida" : "/en/services/custom-software", label: t(lang, "services.softwareAMedida") },
        { href: locale === "es" ? "/es/services/diseno-web-responsive" : "/en/services/responsive-web-design", label: t(lang, "services.disenoWeb") },
        { href: locale === "es" ? "/es/services/posicionamiento-seo" : "/en/services/seo-positioning", label: t(lang, "services.seo") },
        { href: locale === "es" ? "/es/services/posicionamiento-sem" : "/en/services/sem-positioning", label: t(lang, "services.sem") },
        { href: locale === "es" ? "/es/services/e-mail-marketing" : "/en/services/e-mail-marketing", label: t(lang, "services.emailMarketing") }
      ]
    },
    { href: locale === "es" ? "/es/blog" : "/en/blog", label: t(lang, "nav.blog") },
    { href: locale === "es" ? "/es/contact" : "/en/contact", label: t(lang, "nav.contacto") }
  ];
  const contactHref = locale === "es" ? "/es/contact" : "/en/contact";
  const homeHref = locale === "es" ? "/es/" : "/en/";
  return renderTemplate`${maybeRenderHead()}<header class="sticky top-0 z-50 bg-canvas/80 backdrop-blur-md border-b border-hairline h-[56px] flex items-center"> ${renderComponent($$result, "Container", $$Container, { "class": "flex justify-between items-center w-full" }, { "default": ($$result2) => renderTemplate` <a${addAttribute(homeHref, "href")} class="text-2xl font-bold tracking-tighter hover:opacity-80 transition-opacity">selvaggiesteban<span class="text-primary/50">.dev</span></a> <nav class="hidden md:flex gap-lg items-center text-sm font-medium"> ${navLinks.map((link) => renderTemplate`<div class="relative group h-[56px] flex items-center"> <a${addAttribute(link.href, "href")} class="hover:text-primary transition-colors flex items-center gap-1"> ${link.label} ${link.dropdown && renderTemplate`<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-40 group-hover:rotate-180 transition-transform"><path d="m6 9 6 6 6-6"></path></svg>`} </a> ${link.dropdown && renderTemplate`<div class="absolute top-[56px] left-1/2 -translate-x-1/2 w-48 bg-white border border-hairline shadow-xl rounded-none py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all transform group-hover:translate-y-0 translate-y-2"> ${link.dropdown.map((subItem) => renderTemplate`<a${addAttribute(subItem.href, "href")} class="block px-4 py-2 hover:bg-surface-soft hover:text-primary transition-colors whitespace-nowrap"> ${subItem.label} </a>`)} </div>`} </div>`)} ${renderComponent($$result2, "LanguageSwitcher", $$LanguageSwitcher, {})} ${renderComponent($$result2, "Button", $$Button, { "href": contactHref, "variant": "secondary", "class": "!py-1.5 !text-sm ml-2" }, { "default": ($$result3) => renderTemplate`${t(lang, "nav.empezar")}` })} </nav> <button id="menu-toggle" class="md:hidden p-2 z-50 relative"${addAttribute(t(lang, "nav.menu"), "aria-label")} aria-expanded="false"> <svg id="menu-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg> <svg id="close-icon" class="hidden" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg> </button> ` })} </header> <!-- Mobile Menu Overlay — OUTSIDE header --> <div id="mobile-menu" class="fixed inset-0 top-[56px] bg-canvas z-40 flex flex-col items-center justify-start gap-6 translate-x-full transition-transform duration-300 md:hidden overflow-y-auto pt-10 pb-10 px-6 text-center"> ${navLinks.map((link, i) => renderTemplate`<div class="w-full"> ${link.dropdown ? renderTemplate`<button${addAttribute(i, "data-dropdown-toggle")} class="text-2xl font-bold hover:text-primary transition-colors flex items-center justify-center gap-2 w-full py-2 cursor-pointer"> ${link.label} <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="transition-transform duration-200"><path d="m6 9 6 6 6-6"></path></svg> </button>` : renderTemplate`<a${addAttribute(link.href, "href")} class="text-2xl font-bold hover:text-primary transition-colors block py-2">${link.label}</a>`} ${link.dropdown && renderTemplate`<div${addAttribute(i, "data-dropdown-content")} class="flex flex-col gap-2 overflow-hidden transition-all duration-300 max-h-0"> <div class="bg-surface-soft py-4 flex flex-col gap-2"> ${link.dropdown.map((subItem) => renderTemplate`<a${addAttribute(subItem.href, "href")} class="text-lg text-ink/60 hover:text-primary transition-colors py-1">${subItem.label}</a>`)} </div> </div>`} </div>`)} <div class="mt-2"> ${renderComponent($$result, "LanguageSwitcher", $$LanguageSwitcher, {})} </div> ${renderComponent($$result, "Button", $$Button, { "href": contactHref, "variant": "primary", "class": "mt-4 w-full max-w-[280px]" }, { "default": ($$result2) => renderTemplate`${t(lang, "nav.empezarAhora")}` })} </div> ${renderScript($$result, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/Navbar.astro?astro&type=script&index=0&lang.ts")}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/Navbar.astro", void 0);
const $$Footer = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Footer;
  const locale = getLocaleFromUrl(Astro2.url);
  const lang = locale;
  const year = (/* @__PURE__ */ new Date()).getFullYear();
  const isCV = Astro2.url.pathname.includes("/cv/");
  const p = (path) => locale === "es" ? `/es${path}` : `/en${path}`;
  const serviceLink = (esSlug, enSlug) => locale === "es" ? `/es/services/${esSlug}` : `/en/services/${enSlug}`;
  const cvLink = (esSlug, enSlug) => locale === "es" ? `/es/cv/${esSlug}` : `/en/cv/${enSlug}`;
  const blogLink = (esSlug, enSlug) => locale === "es" ? `/es/blog/${esSlug}` : `/en/blog/${enSlug}`;
  return renderTemplate`${maybeRenderHead()}<footer class="bg-canvas border-t border-hairline pt-section pb-8 mt-section"> ${renderComponent($$result, "Container", $$Container, {}, { "default": ($$result2) => renderTemplate` <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-xl mb-xl"> <div class="lg:col-span-2"> <a${addAttribute(p("/"), "href")} class="text-2xl font-bold tracking-tighter">selvaggiesteban.dev</a> <p class="mt-4 text-sm text-ink/60 mb-6 leading-relaxed"> ${t(lang, "footer.bio")} </p> <ul class="space-y-3 text-sm text-ink/80 mb-8"> <li><a${addAttribute(cvLink("ingeniero-en-informatica", "computer-science-engineer"), "href")} class="hover:underline text-primary">${t(lang, "footer.ingenieroInformatica")}</a></li> <li><a${addAttribute(cvLink("ingeniero-en-software", "software-engineer"), "href")} class="hover:underline text-primary">${t(lang, "footer.ingenieroSoftware")}</a></li> <li><a${addAttribute(cvLink("desarrollador-web-full-stack", "full-stack-web-developer"), "href")} class="hover:underline text-primary">${t(lang, "footer.desarrolladorFullStack")}</a></li> <li><a${addAttribute(cvLink("experto-en-posicionamiento-seo", "seo-positioning-specialist"), "href")} class="hover:underline text-primary">${t(lang, "footer.expertoSEO")}</a></li> </ul> <h4 class="font-mono text-xs uppercase tracking-widest text-ink/40 mb-4">${t(lang, "footer.contacto")}</h4> <ul class="space-y-2 text-sm text-ink/80 flex flex-col"> <li>${t(lang, "footer.email")} <a href="mailto:selvaggiesteban@gmail.com" class="hover:underline text-primary">selvaggiesteban@gmail.com</a></li> <li>${t(lang, "footer.telefono")} <a href="tel:+5491153323937" class="hover:underline text-primary">(+54) 9 11 5332-3937</a></li> </ul> </div> ${!isCV && renderTemplate`<div> <h4 class="font-mono text-xs uppercase tracking-widest text-ink/40 mb-6">${t(lang, "footer.servicios")}</h4> <ul class="space-y-3 text-sm text-ink/80"> <li><a${addAttribute(serviceLink("software-a-medida", "custom-software"), "href")} class="hover:underline hover:text-primary transition-colors">${t(lang, "services.softwareAMedida")}</a></li> <li><a${addAttribute(serviceLink("diseno-web-responsive", "responsive-web-design"), "href")} class="hover:underline hover:text-primary transition-colors">${t(lang, "services.disenoWeb")}</a></li> <li><a${addAttribute(serviceLink("posicionamiento-seo", "seo-positioning"), "href")} class="hover:underline hover:text-primary transition-colors">${t(lang, "services.seo")}</a></li> <li><a${addAttribute(serviceLink("posicionamiento-sem", "sem-positioning"), "href")} class="hover:underline hover:text-primary transition-colors">${t(lang, "services.sem")}</a></li> <li><a${addAttribute(serviceLink("e-mail-marketing", "e-mail-marketing"), "href")} class="hover:underline hover:text-primary transition-colors">${t(lang, "services.emailMarketing")}</a></li> </ul> </div>`} ${!isCV && renderTemplate`<div> <h4 class="font-mono text-xs uppercase tracking-widest text-ink/40 mb-6">${t(lang, "footer.guiasSEO")}</h4> <ul class="space-y-3 text-sm text-ink/80 flex flex-col"> <li><a${addAttribute(blogLink("seo-local-guia-completa-para-dominar-la-busqueda-local", "local-seo-complete-guide-to-mastering-local-search"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">SEO Local</a></li> <li><a${addAttribute(blogLink("seo-on-page-la-guia-definitiva-para-dominar-tu-web", "on-page-seo-the-ultimate-guide-to-mastering-your-website"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">SEO On-Page</a></li> <li><a${addAttribute(blogLink("seo-off-page-la-guia-definitiva-para-dominar-el-posicionamiento", "off-page-seo-the-ultimate-guide-to-mastering-external-positioning"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">SEO Off-Page</a></li> <li><a${addAttribute(blogLink("seo-de-contenidos-guia-completa-para-dominar-el-ranking", "content-seo-complete-guide-to-mastering-the-rankings"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">SEO de Contenidos</a></li> <li><a${addAttribute(blogLink("consultoria-seo-guia-definitiva-para-el-exito-digital", "seo-consulting-the-ultimate-guide-to-digital-success"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Consultoría SEO</a></li> <li><a${addAttribute(blogLink("seo-local-la-guia-definitiva-para-atraer-clientes-cercanos", "local-seo-the-ultimate-guide-to-attracting-nearby-customers"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">SEO Local Avanzado</a></li> <li><a${addAttribute(blogLink("mantenimiento-web-la-guia-definitiva-para-un-sitio-seguro-y-optimizado", "web-maintenance-the-ultimate-guide-to-a-secure-and-optimized-website"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Mantenimiento Web</a></li> <li><a${addAttribute(blogLink("las-mejores-herramientas-de-marketing-digital-para-2024", "the-best-digital-marketing-tools-for-2024"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Herramientas Marketing Digital</a></li> <li><a${addAttribute(blogLink("analitica-web-guia-completa-para-dominar-tus-datos-online", "web-analytics-complete-guide-to-mastering-your-online-data"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Analítica Web</a></li> </ul> </div>`} ${!isCV && renderTemplate`<div> <h4 class="font-mono text-xs uppercase tracking-widest text-ink/40 mb-6">${t(lang, "footer.desarrolloIA")}</h4> <ul class="space-y-3 text-sm text-ink/80 flex flex-col"> <li><a${addAttribute(blogLink("actualizaciones-web", "website-updates"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Actualizaciones Web</a></li> <li><a${addAttribute(blogLink("landing-page", "landing-page"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Landing Pages Optimizadas</a></li> <li><a${addAttribute(blogLink("experto-wordpress-tu-guia-definitiva-para-el-exito-digital", "wordpress-expert-your-ultimate-guide-to-digital-success"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Experto WordPress</a></li> <li><a${addAttribute(blogLink("sistema-multi-agente-con-ia", "ai-multi-agent-system"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Sistemas Multi-Agente con IA</a></li> <li><a${addAttribute(blogLink("ejercito-de-juniors", "army-of-juniors"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Ejército de Juniors</a></li> <li><a${addAttribute(blogLink("claude-code-gratis", "free-claude-code"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Claude Code Gratis</a></li> <li><a${addAttribute(blogLink("prompts-para-ia", "ai-prompts"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Prompts para IA</a></li> <li><a${addAttribute(blogLink("automatizacion-de-marketing-profesional", "professional-marketing-automation"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Automatización de Marketing</a></li> <li><a${addAttribute(blogLink("experto-en-automatizacion-rpa", "rpa-automation-expert"), "href")} class="hover:underline hover:text-primary transition-colors line-clamp-1">Experto en Automatización RPA</a></li> </ul> </div>`} </div> <div class="pt-8 border-t border-hairline flex flex-col md:flex-row justify-between items-center text-xs text-ink/40 uppercase tracking-widest font-mono gap-4 md:gap-0"> <span>© ${year} Esteban Selvaggi</span> <div class="flex gap-6"> <a${addAttribute(p("/privacy-policy"), "href")} class="hover:text-primary transition-colors">${t(lang, "footer.privacidad")}</a> <a${addAttribute(p("/cookie-policy"), "href")} class="hover:text-primary transition-colors">${t(lang, "footer.cookies")}</a> </div> </div> ` })} </footer>`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/Footer.astro", void 0);
export {
  $$Button as $,
  $$Footer as a,
  $$Navbar as b,
  $$SEO as c,
  $$Container as d,
  getLocaleFromUrl as g,
  renderScript as r,
  t
};
