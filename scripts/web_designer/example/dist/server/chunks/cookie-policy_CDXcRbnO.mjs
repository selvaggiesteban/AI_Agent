globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$BaseLayout } from "./BaseLayout_Dc4xzKg4.mjs";
import { $ as $$Section } from "./Section_X3fkqAep.mjs";
const $$CookiePolicy = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Política de Cookies", "description": "Política de Cookies para el sitio web selvaggiesteban.dev" }, { "default": ($$result2) => renderTemplate` ${renderComponent($$result2, "Section", $$Section, {}, { "default": ($$result3) => renderTemplate` ${maybeRenderHead()}<div class="max-w-3xl mx-auto"> <h1 class="display-lg mb-md">Política de Cookies</h1> <p class="text-sm text-ink/60 mb-xl">Última actualización: Mayo 2026</p> <div class="prose prose-ink max-w-none"> <p>Este sitio web, selvaggiesteban.dev, utiliza cookies para mejorar la experiencia del usuario y analizar el tráfico de nuestro sitio. En cumplimiento de las normativas vigentes, esta página explica qué son las cookies, cuáles usamos y cómo puede gestionarlas.</p> <h2>¿Qué son las cookies?</h2> <p>Las cookies son pequeños archivos de texto que los sitios web que usted visita colocan en su ordenador o dispositivo móvil. Se utilizan ampliamente para hacer que los sitios web funcionen, o funcionen de manera más eficiente, así como para proporcionar información a los propietarios del sitio.</p> <h2>Tipos de Cookies que Utilizamos</h2> <h3>1. Cookies Esenciales (Técnicas)</h3> <p>Estas cookies son necesarias para el funcionamiento del sitio web y no pueden ser desactivadas en nuestros sistemas. Generalmente solo se configuran en respuesta a acciones que usted realiza (por ejemplo, recordar sus preferencias de cookies o enviar de forma segura el formulario a través de Cloudflare Turnstile). Estas cookies no almacenan información de identificación personal.</p> <h3>2. Cookies de Análisis</h3> <p>Utilizamos herramientas como Google Analytics (GA4) para comprender cómo los visitantes interactúan con nuestro sitio web. Estas cookies recopilan información de forma anónima, reportando tendencias del sitio web sin identificar a los visitantes individuales. Estas cookies solo se activan si usted da su consentimiento expreso en nuestro banner de cookies.</p> <h2>Gestión del Consentimiento</h2> <p>Cuando visita nuestro sitio por primera vez, se le presenta un banner que le permite aceptar todas las cookies o rechazar las no esenciales (como las de análisis). Su decisión de rechazar las cookies no esenciales no afectará la navegación general ni el acceso al contenido de nuestro sitio web.</p> <p>Para gestionar o modificar su consentimiento, puede borrar las cookies desde los ajustes de su navegador, tras lo cual se le volverá a mostrar nuestro banner de consentimiento.</p> </div> </div> ` })} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/es/cookie-policy.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/es/cookie-policy.astro";
const $$url = "/es/cookie-policy";
const _page = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: $$CookiePolicy,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: "Module" }));
const page = () => _page;
export {
  page
};
