globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$BaseLayout } from "./BaseLayout_Dc4xzKg4.mjs";
import { $ as $$Section } from "./Section_X3fkqAep.mjs";
const $$ThankYou = createComponent(($$result, $$props, $$slots) => {
  const title = "Thank You!";
  const description = "Thank you for getting in touch with us.";
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": title, "description": description, "locale": "en" }, { "default": ($$result2) => renderTemplate` ${renderComponent($$result2, "Section", $$Section, { "variant": "lilac" }, { "default": ($$result3) => renderTemplate` ${maybeRenderHead()}<div class="text-center py-xl"> <h1 class="display-lg mb-md">Message Sent!</h1> <p class="text-xl opacity-70 mb-xl">
I have received your message and will get back to you shortly.
</p> <a href="/en/" class="btn-primary">Back to Home</a> </div> ` })} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/en/contact/thank-you.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/en/contact/thank-you.astro";
const $$url = "/en/contact/thank-you";
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
