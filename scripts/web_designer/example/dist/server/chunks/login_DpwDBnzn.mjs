globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { r as renderScript, $ as $$Button } from "./global_tQVAIOUq.mjs";
import { $ as $$BaseLayout } from "./BaseLayout_Dc4xzKg4.mjs";
const $$Login = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Login;
  const title = "Acceso Restringido";
  const description = "Inicia sesión para continuar.";
  if (Astro2.cookies.has("admin_session")) {
    return Astro2.redirect("/presupuestos");
  }
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": title, "description": description }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="min-h-[60vh] flex items-center justify-center px-4"> <div class="w-full max-w-md bg-white p-8 rounded-[9px] border border-hairline shadow-sm text-center"> <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mx-auto mb-6 text-primary"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg> <h1 class="text-2xl font-bold text-ink mb-2">Acceso Restringido</h1> <p class="text-ink/60 text-sm mb-8">Ingresa la contraseña maestra para acceder al CRM.</p> <form id="login-form" class="space-y-6 text-left"> <div class="space-y-2"> <label for="password" class="font-mono text-xs uppercase tracking-widest text-ink/40">Contraseña</label> <input type="password" id="password" name="password" required class="w-full p-4 bg-surface-soft border border-hairline rounded-[9px] focus:border-primary outline-none transition-colors" placeholder="••••••••"> </div> ${renderComponent($$result2, "Button", $$Button, { "type": "submit", "class": "w-full py-4" }, { "default": async ($$result3) => renderTemplate`Ingresar al sistema` })} <p id="login-error" class="text-red-500 text-sm mt-4 hidden text-center">Contraseña incorrecta.</p> </form> </div> </div> ` })} ${renderScript($$result, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/login.astro?astro&type=script&index=0&lang.ts")}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/login.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/login.astro";
const $$url = "/login";
const _page = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: $$Login,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: "Module" }));
const page = () => _page;
export {
  page
};
