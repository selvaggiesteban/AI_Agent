globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$BaseLayout } from "./BaseLayout_Dc4xzKg4.mjs";
import { $ as $$Section } from "./Section_X3fkqAep.mjs";
const $$PrivacyPolicy = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Privacy Policy", "description": "Privacy Policy and personal data protection for selvaggiesteban.dev" }, { "default": ($$result2) => renderTemplate` ${renderComponent($$result2, "Section", $$Section, {}, { "default": ($$result3) => renderTemplate` ${maybeRenderHead()}<div class="max-w-3xl mx-auto"> <h1 class="display-lg mb-md">Privacy Policy</h1> <p class="text-sm text-ink/60 mb-xl">Last updated: May 2026</p> <div class="prose prose-ink max-w-none"> <p>At selvaggiesteban.dev we respect your privacy and are committed to protecting the personal data you provide. This Privacy Policy explains how we collect, use, and protect your information.</p> <h2>1. Information We Collect</h2> <p>Through our contact form, we may request and collect personal information including, but not limited to, your name, email address, and the details of your message.</p> <h2>2. Use of Information</h2> <p>The collected information is used exclusively to respond to your inquiries, send you quotes, or provide the consulting, computer engineering, development, and SEO services you have requested. We do not sell or share your data with third parties.</p> <h2>3. Data Protection</h2> <p>We implement technical security measures to protect your information against unauthorized access. However, no data transmission over the Internet is 100% secure.</p> <h2>4. Analytics and Tracking Technologies</h2> <p>We may use analytics tools (such as Google Analytics 4) that collect anonymous information about traffic and visitor behavior on our website. This collection is subject to your express consent through our cookie banner.</p> <h2>5. User Rights</h2> <p>You have the right to request access to, correction of, or deletion of your personal information. To exercise these rights, please contact us at selvaggiesteban@gmail.com.</p> </div> </div> ` })} ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/en/privacy-policy.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/en/privacy-policy.astro";
const $$url = "/en/privacy-policy";
const _page = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: $$PrivacyPolicy,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: "Module" }));
const page = () => _page;
export {
  page
};
