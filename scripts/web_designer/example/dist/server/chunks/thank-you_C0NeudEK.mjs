globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$BaseLayout } from "./BaseLayout_Dc4xzKg4.mjs";
import { $ as $$Section } from "./Section_X3fkqAep.mjs";
const $$ThankYou = createComponent(($$result, $$props, $$slots) => {
  const title = "¡Gracias!";
  const description = "Gracias por ponerte en contacto con nosotros.";
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": title, "description": description, "noindex": true }, { "default": ($$result2) => renderTemplate` ${renderComponent($$result2, "Section", $$Section, { "variant": "lilac" }, { "default": ($$result3) => renderTemplate` ${maybeRenderHead()}<div class="text-center py-xl"> <h1 class="display-lg mb-md">¡Mensaje enviado!</h1> <p class="text-xl opacity-70 mb-xl">
He recibido tu mensaje y me pondré en contacto contigo a la brevedad.
</p> <a href="/es/" class="btn-primary">Volver al inicio</a> </div> ` })} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/es/contact/thank-you.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/es/contact/thank-you.astro";
const $$url = "/es/contact/thank-you";
const _page = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: $$ThankYou,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: "Module" }));
const page = () => _page;
export {
  page
};
