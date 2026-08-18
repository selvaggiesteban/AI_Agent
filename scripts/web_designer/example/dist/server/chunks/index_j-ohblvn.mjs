globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$BaseLayout } from "./BaseLayout_Dc4xzKg4.mjs";
import { $ as $$Section } from "./Section_X3fkqAep.mjs";
import { g as getLocaleFromUrl, t, $ as $$Button } from "./global_tQVAIOUq.mjs";
import { $ as $$ProjectCarousel, a as $$SkillsSection, b as $$ReviewsCarousel, c as $$RecentPosts, d as $$RecommendedPosts } from "./RecommendedPosts_DLR_S97E.mjs";
const $$Index = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Index;
  const locale = getLocaleFromUrl(Astro2.url);
  const lang = locale;
  const title = t(lang, "home.title");
  const description = t(lang, "home.description");
  const p = (path) => locale === "es" ? `/es${path}` : `/en${path}`;
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": title, "description": description }, { "default": ($$result2) => renderTemplate`  ${renderComponent($$result2, "Section", $$Section, { "variant": "white", "class": "pt-24 pb-16 reveal" }, { "default": ($$result3) => renderTemplate` ${maybeRenderHead()}<div class="max-w-4xl mx-auto text-center flex flex-col items-center"> <h1 class="font-bold text-[56px] md:text-[86px] leading-tight" style="margin-bottom: 50px;">
Esteban Selvaggi<br><span class="text-primary/60">Ingeniero en Informática</span> </h1> <div class="flex flex-wrap justify-center gap-md"> ${renderComponent($$result3, "Button", $$Button, { "href": p("/contact") }, { "default": ($$result4) => renderTemplate`Empezar ahora` })} ${renderComponent($$result3, "Button", $$Button, { "href": p("/services"), "variant": "secondary" }, { "default": ($$result4) => renderTemplate`Ver servicios` })} </div> </div> ` })}  ${renderComponent($$result2, "Section", $$Section, { "variant": "white", "class": "reveal !py-0", "fullWidth": true }, { "default": ($$result3) => renderTemplate` ${renderComponent($$result3, "ProjectCarousel", $$ProjectCarousel, {})} ` })}  <div class="reveal"> ${renderComponent($$result2, "SkillsSection", $$SkillsSection, {})} </div>  <div class="reveal"> ${renderComponent($$result2, "ReviewsCarousel", $$ReviewsCarousel, {})} </div>  ${renderComponent($$result2, "RecentPosts", $$RecentPosts, {})}  ${renderComponent($$result2, "RecommendedPosts", $$RecommendedPosts, {})} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/es/index.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/es/index.astro";
const $$url = "/es";
const _page = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: "Module" }));
const page = () => _page;
export {
  page
};
