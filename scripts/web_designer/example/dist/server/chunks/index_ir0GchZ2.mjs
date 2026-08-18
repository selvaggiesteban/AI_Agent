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
  const posts = (await getCollection("blog")).filter((p) => p.id.startsWith("en/")).sort(
    (a, b) => {
      const dateA = a.data.pubDate ? new Date(a.data.pubDate).valueOf() : 0;
      const dateB = b.data.pubDate ? new Date(b.data.pubDate).valueOf() : 0;
      return dateB - dateA;
    }
  );
  const blogPrefix = locale === "es" ? "/es/blog" : "/en/blog";
  const getSlug = (id) => id.replace(/^(en|es)\//, "");
  const postUrl = (id) => `${blogPrefix}/${getSlug(id)}`;
  let featuredPost = posts.find((post) => getSlug(post.id) === "free-claude-code");
  let remainingPosts = posts.filter((post) => getSlug(post.id) !== "free-claude-code");
  if (!featuredPost && posts.length > 0) {
    featuredPost = posts[0];
    remainingPosts = posts.slice(1);
  }
  const title = t(lang, "blog.title");
  const description = t(lang, "blog.description");
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": title, "description": description }, { "default": async ($$result2) => renderTemplate` ${renderComponent($$result2, "Section", $$Section, {}, { "default": async ($$result3) => renderTemplate` ${maybeRenderHead()}<div class="mb-16 text-center md:text-left"> <h1 class="display-lg mb-4">${t(lang, "blog.heading")}</h1> <p class="text-xl text-ink/60 max-w-2xl">${t(lang, "blog.subtitle")}</p> </div> ${featuredPost && renderTemplate`<div class="mb-20"> <article class="group relative bg-surface-soft rounded-3xl overflow-hidden border border-hairline transition-all overflow-hidden"> <a${addAttribute(`${postUrl(featuredPost.id)}`, "href")} class="absolute inset-0 z-10"><span class="sr-only">${t(lang, "blog.readArticle")}</span></a> ${featuredPost.data.heroImage && renderTemplate`<div class="w-full aspect-[21/9] overflow-hidden"> <img${addAttribute(featuredPost.data.heroImage, "src")}${addAttribute(featuredPost.data.title, "alt")} class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="eager"> </div>`} <div class="p-8 md:p-12"> <span class="inline-block px-3 py-1 bg-primary/10 text-primary font-bold text-xs uppercase tracking-widest rounded-full mb-6">${t(lang, "blog.featured")}</span> <a${addAttribute(`${postUrl(featuredPost.id)}`, "href")} class="block"> <h2 class="text-3xl md:text-5xl font-bold mb-6 group-hover:text-primary transition-colors leading-tight text-pretty">${featuredPost.data.title}</h2> </a> <p class="text-lg md:text-xl text-ink/70 leading-relaxed mb-8 max-w-3xl">${featuredPost.data.description}</p> <div class="flex items-center justify-between mt-auto pt-8 border-t border-hairline-soft"> <span class="font-mono text-xs uppercase tracking-widest text-ink/50"> ${featuredPost.data.pubDate ? new Date(featuredPost.data.pubDate).toLocaleDateString(locale === "es" ? "es-AR" : "en-US", { year: "numeric", month: "long", day: "numeric" }) : ""} </span> <a${addAttribute(`${postUrl(featuredPost.id)}`, "href")} class="inline-flex items-center gap-2 font-bold text-primary hover:underline"> ${t(lang, "blog.readArticle")} <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg> </a> </div> </div> </article> </div>`}<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"> ${remainingPosts.map((post) => renderTemplate`<article class="group bg-white relative rounded-2xl border border-hairline hover:shadow-lg transition-all border-transparent flex flex-col h-full overflow-hidden"> <a${addAttribute(`${postUrl(post.id)}`, "href")} class="absolute inset-0 z-10"><span class="sr-only">${t(lang, "blog.readMore")}</span></a> ${post.data.heroImage && renderTemplate`<div class="w-full aspect-video overflow-hidden"> <img${addAttribute(post.data.heroImage, "src")}${addAttribute(post.data.title, "alt")} class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy"> </div>`} <div class="p-6 flex flex-col flex-grow"> <span class="font-mono text-[10px] uppercase tracking-widest text-ink/40 mb-4 block"> ${post.data.pubDate ? new Date(post.data.pubDate).toLocaleDateString(locale === "es" ? "es-AR" : "en-US", { year: "numeric", month: "long", day: "numeric" }) : ""} </span> <a${addAttribute(`${postUrl(post.id)}`, "href")} class="block mb-4 flex-grow"> <h2 class="text-xl font-bold group-hover:text-primary transition-colors leading-snug line-clamp-3">${post.data.title}</h2> </a> <p class="text-sm text-ink/60 leading-relaxed mb-6 line-clamp-3">${post.data.description}</p> <div class="mt-auto pt-4 border-t border-hairline-soft"> <a${addAttribute(`${postUrl(post.id)}`, "href")} class="text-sm font-bold text-primary group-hover:underline inline-flex items-center gap-1"> ${t(lang, "blog.readMore")} <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="transition-transform group-hover:translate-x-1"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg> </a> </div> </div> </article>`)} </div> ` })} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/en/blog/index.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/en/blog/index.astro";
const $$url = "/en/blog";
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
