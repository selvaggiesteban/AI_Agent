globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$BaseLayout } from "./BaseLayout_Dc4xzKg4.mjs";
import { $ as $$Section } from "./Section_X3fkqAep.mjs";
const $$PrivacyPolicy = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Política de Privacidad", "description": "Política de Privacidad y protección de datos personales de selvaggiesteban.dev" }, { "default": ($$result2) => renderTemplate` ${renderComponent($$result2, "Section", $$Section, {}, { "default": ($$result3) => renderTemplate` ${maybeRenderHead()}<div class="max-w-3xl mx-auto"> <h1 class="display-lg mb-md">Política de Privacidad</h1> <p class="text-sm text-ink/60 mb-xl">Última actualización: Mayo 2026</p> <div class="prose prose-ink max-w-none"> <p>En selvaggiesteban.dev respetamos su privacidad y estamos comprometidos a proteger los datos personales que nos proporcione. Esta Política de Privacidad explica cómo recopilamos, usamos, y protegemos su información.</p> <h2>1. Información que recopilamos</h2> <p>A través de nuestro formulario de contacto, podemos solicitar y recopilar información personal que incluye, pero no se limita a, su nombre, dirección de correo electrónico, y los detalles de su mensaje.</p> <h2>2. Uso de la información</h2> <p>La información recopilada se utiliza exclusivamente para responder a sus consultas, enviarle presupuestos o proveer los servicios de consultoría, ingeniería informática, desarrollo y posicionamiento SEO solicitados. No vendemos ni cedemos sus datos a terceros.</p> <h2>3. Protección de datos</h2> <p>Implementamos medidas de seguridad técnicas para proteger su información contra accesos no autorizados. Sin embargo, ninguna transmisión de datos a través de Internet es 100% segura.</p> <h2>4. Analítica y Tecnologías de Rastreo</h2> <p>Podemos utilizar herramientas de análisis (como Google Analytics 4) que recogen información anónima sobre el tráfico y comportamiento de los visitantes en nuestro sitio web. Esta recolección está sujeta a su consentimiento expreso mediante nuestro banner de cookies.</p> <h2>5. Derechos del Usuario</h2> <p>Usted tiene derecho a solicitar el acceso, la corrección, o eliminación de su información personal. Para ejercer estos derechos, comuníquese con nosotros a través de selvaggiesteban@gmail.com.</p> </div> </div> ` })} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/es/privacy-policy.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/es/privacy-policy.astro";
const $$url = "/es/privacy-policy";
const _page = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: $$PrivacyPolicy,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: "Module" }));
const page = () => _page;
export {
  page
};
