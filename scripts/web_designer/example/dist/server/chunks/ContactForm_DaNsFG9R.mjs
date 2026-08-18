globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { v as maybeRenderHead, a0 as addAttribute, K as renderTemplate } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { g as getLocaleFromUrl, t, $ as $$Button, r as renderScript } from "./global_tQVAIOUq.mjs";
const $$ContactForm = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$ContactForm;
  const locale = getLocaleFromUrl(Astro2.url);
  const lang = locale;
  const privacyHref = locale === "es" ? "/es/privacy-policy" : "/en/privacy-policy";
  return renderTemplate`${maybeRenderHead()}<div class="mt-xl pt-xl border-t border-hairline"> <div class="max-w-4xl mx-auto text-center flex flex-col items-center"> <h2 class="display-sm mb-4">${t(lang, "contact.heading")}</h2> <p class="mb-12 text-ink/70 max-w-2xl text-center"> ${t(lang, "contact.subtitle")} </p> <form id="contact-form" class="w-full space-y-6 bg-canvas p-8 md:p-12 rounded-[9px] border border-hairline shadow-sm text-left"> <div class="space-y-2"> <label for="name" class="font-mono text-xs uppercase tracking-widest text-ink/40">${t(lang, "contact.nombre")}</label> <input type="text" id="name" name="name" required class="w-full p-4 bg-surface-soft border border-hairline rounded-[9px] focus:border-primary outline-none transition-colors"> </div> <div class="space-y-2"> <label for="email" class="font-mono text-xs uppercase tracking-widest text-ink/40">${t(lang, "contact.email")}</label> <input type="email" id="email" name="email" required class="w-full p-4 bg-surface-soft border border-hairline rounded-[9px] focus:border-primary outline-none transition-colors"> </div> <div class="space-y-2"> <label for="message" class="font-mono text-xs uppercase tracking-widest text-ink/40">${t(lang, "contact.mensaje")}</label> <textarea id="message" name="message" rows="4" required class="w-full p-4 bg-surface-soft border border-hairline rounded-[9px] focus:border-primary outline-none transition-colors"></textarea> </div> <div class="flex items-start gap-2 pt-2"> <input type="checkbox" id="privacy" name="privacy" required class="mt-1 accent-primary focus:ring-primary w-4 h-4"> <label for="privacy" class="text-sm text-ink/70"> ${t(lang, "contact.privacyPrefix")} <a${addAttribute(privacyHref, "href")} class="text-primary underline hover:text-primary-dark" target="_blank">${t(lang, "contact.privacyLink")}</a> ${t(lang, "contact.privacySuffix")} </label> </div> <div id="my-turnstile-container" class="min-h-[65px] flex justify-center mb-4"></div> ${renderComponent($$result, "Button", $$Button, { "type": "submit", "class": "w-full text-lg py-4" }, { "default": async ($$result2) => renderTemplate`${t(lang, "contact.submit")}` })} <p id="form-status" class="text-sm mt-4 hidden"></p> </form> </div> </div> ${renderScript($$result, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/ContactForm.astro?astro&type=script&index=0&lang.ts")}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/ContactForm.astro", void 0);
export {
  $$ContactForm as $
};
