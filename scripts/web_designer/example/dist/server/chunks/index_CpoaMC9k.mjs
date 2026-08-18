globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead, a0 as addAttribute } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { g as getCollection } from "./_astro_content_DL4dQ2_T.mjs";
import { $ as $$BaseLayout } from "./BaseLayout_Dc4xzKg4.mjs";
import { $ as $$Section } from "./Section_X3fkqAep.mjs";
import { g as getLocaleFromUrl, t } from "./global_tQVAIOUq.mjs";
const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Index;
  const locale = getLocaleFromUrl(Astro2.url);
  const lang = locale;
  const allServicios = await getCollection("servicios");
  const servicios = allServicios.filter((s) => s.id.startsWith("en/"));
  const servicesPrefix = locale === "es" ? "/es/services" : "/en/services";
  const title = t(lang, "servicesPage.title");
  const description = t(lang, "servicesPage.description");
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": title, "description": description }, { "default": async ($$result2) => renderTemplate` ${renderComponent($$result2, "Section", $$Section, {}, { "default": async ($$result3) => renderTemplate` ${maybeRenderHead()}<h1 class="font-bold text-[44px] md:text-[72px] leading-tight text-center">${t(lang, "servicesPage.heading")}</h1> <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-lg"> ${servicios.map((servicio) => {
    const slug = servicio.id.replace("en/", "");
    return renderTemplate`<article class="group relative p-lg bg-surface-soft rounded-lg border border-transparent transition-all"> <a${addAttribute(`${servicesPrefix}/${slug}`, "href")} class="absolute inset-0 z-10"><span class="sr-only">${t(lang, "servicesPage.viewService")}</span></a> <h2 class="text-xl font-bold mb-sm text-center group-hover:text-primary">${servicio.data.title}</h2> <p class="text-ink/60">${servicio.data.description}</p> </article>`;
  })} </div> ` })} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/en/services/index.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/en/services/index.astro";
const $$url = "/en/services";
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
