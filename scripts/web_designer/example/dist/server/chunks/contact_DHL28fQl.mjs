globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$BaseLayout } from "./BaseLayout_Dc4xzKg4.mjs";
import { $ as $$Section } from "./Section_X3fkqAep.mjs";
import { $ as $$ContactForm } from "./ContactForm_DaNsFG9R.mjs";
const $$Contact = createComponent(($$result, $$props, $$slots) => {
  const title = "Contacto";
  const description = "Ponte en contacto con nosotros para discutir tu próximo proyecto web.";
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": title, "description": description }, { "default": ($$result2) => renderTemplate` ${renderComponent($$result2, "Section", $$Section, { "variant": "white", "class": "reveal" }, { "default": ($$result3) => renderTemplate` ${maybeRenderHead()}<div class="max-w-4xl mx-auto text-center flex flex-col items-center"> <h1 class="display-lg mb-md">Hablemos.</h1> <p class="mb-xl text-lg opacity-70 max-w-2xl text-center">
¿Tienes un proyecto en mente o simplemente quieres saludar? Completa el formulario y te responderé lo antes posible.
</p> ${renderComponent($$result3, "ContactForm", $$ContactForm, {})} </div> ` })} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/es/contact.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/es/contact.astro";
const $$url = "/es/contact";
const _page = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: $$Contact,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: "Module" }));
const page = () => _page;
export {
  page
};
