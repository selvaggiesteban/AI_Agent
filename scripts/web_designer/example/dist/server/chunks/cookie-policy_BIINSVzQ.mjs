globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$BaseLayout } from "./BaseLayout_Dc4xzKg4.mjs";
import { $ as $$Section } from "./Section_X3fkqAep.mjs";
const $$CookiePolicy = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Cookie Policy", "description": "Cookie Policy for the selvaggiesteban.dev website" }, { "default": ($$result2) => renderTemplate` ${renderComponent($$result2, "Section", $$Section, {}, { "default": ($$result3) => renderTemplate` ${maybeRenderHead()}<div class="max-w-3xl mx-auto"> <h1 class="display-lg mb-md">Cookie Policy</h1> <p class="text-sm text-ink/60 mb-xl">Last updated: May 2026</p> <div class="prose prose-ink max-w-none"> <p>This website, selvaggiesteban.dev, uses cookies to improve the user experience and analyze site traffic. In compliance with current regulations, this page explains what cookies are, which ones we use, and how you can manage them.</p> <h2>What Are Cookies?</h2> <p>Cookies are small text files that websites you visit place on your computer or mobile device. They are widely used to make websites function, or function more efficiently, as well as to provide information to site owners.</p> <h2>Types of Cookies We Use</h2> <h3>1. Essential Cookies (Technical)</h3> <p>These cookies are necessary for the website to function and cannot be disabled in our systems. They are generally only set in response to actions you take (e.g., remembering your cookie preferences or securely submitting the form through Cloudflare Turnstile). These cookies do not store personally identifiable information.</p> <h3>2. Analytics Cookies</h3> <p>We use tools like Google Analytics (GA4) to understand how visitors interact with our website. These cookies collect information anonymously, reporting website trends without identifying individual visitors. These cookies are only activated if you give your express consent through our cookie banner.</p> <h2>Consent Management</h2> <p>When you first visit our site, a banner is presented that allows you to accept all cookies or reject non-essential ones (such as analytics cookies). Your decision to reject non-essential cookies will not affect general navigation or access to content on our website.</p> <p>To manage or modify your consent, you can clear cookies from your browser settings, after which our consent banner will be shown again.</p> </div> </div> ` })} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/en/cookie-policy.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/en/cookie-policy.astro";
const $$url = "/en/cookie-policy";
const _page = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: $$CookiePolicy,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: "Module" }));
const page = () => _page;
export {
  page
};
