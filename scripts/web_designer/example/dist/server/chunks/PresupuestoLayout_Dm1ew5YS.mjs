globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { a0 as addAttribute, bn as renderHead, bm as renderSlot, K as renderTemplate } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { g as getLocaleFromUrl, c as $$SEO, b as $$Navbar, a as $$Footer } from "./global_tQVAIOUq.mjs";
const $$PresupuestoLayout = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$PresupuestoLayout;
  const { title, description, locale: propLocale } = Astro2.props;
  const locale = propLocale || getLocaleFromUrl(Astro2.url);
  return renderTemplate`<html${addAttribute(locale, "lang")}> <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><link rel="icon" type="image/svg+xml" href="/favicon.svg"><meta name="generator"${addAttribute(Astro2.generator, "content")}><!-- Block indexing of budgets --><meta name="robots" content="noindex, nofollow">${renderComponent($$result, "SEO", $$SEO, { "title": title, "description": description })}${renderHead()}</head> <body class="bg-surface"> ${renderComponent($$result, "Navbar", $$Navbar, {})} <main class="max-w-7xl mx-auto px-lg md:px-xxl pb-20"> ${renderSlot($$result, $$slots["default"])} </main> ${renderComponent($$result, "Footer", $$Footer, {})} </body></html>`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/layouts/PresupuestoLayout.astro", void 0);
export {
  $$PresupuestoLayout as $
};
