globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { v as maybeRenderHead, a0 as addAttribute, K as renderTemplate, bm as renderSlot, bn as renderHead, bj as unescapeHTML } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { g as getLocaleFromUrl, t, r as renderScript, a as $$Footer, b as $$Navbar, c as $$SEO } from "./global_tQVAIOUq.mjs";
const $$WhatsAppButton = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$WhatsAppButton;
  const locale = getLocaleFromUrl(Astro2.url);
  const lang = locale;
  const { phone, message = t(lang, "whatsapp.message") } = Astro2.props;
  const cleanPhone = phone.replace(/\s+/g, "");
  const formattedPhone = cleanPhone.startsWith("54") ? cleanPhone : `549${cleanPhone}`;
  const whatsappUrl = `https://wa.me/${formattedPhone}?text=${encodeURIComponent(message)}`;
  return renderTemplate`${maybeRenderHead()}<a${addAttribute(whatsappUrl, "href")} class="fixed bottom-8 right-8 z-50 bg-[#25D366] text-white p-3 rounded-full shadow-[0_10px_25px_-5px_rgba(37,211,102,0.4)] hover:scale-110 transition-transform flex items-center justify-center " target="_blank" rel="noopener noreferrer"${addAttribute(t(lang, "whatsapp.ariaLabel"), "aria-label")}> <svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="currentColor"> <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L0 24l6.335-1.662c1.72.94 3.659 1.437 5.634 1.437h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"></path> </svg> </a>`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/WhatsAppButton.astro", void 0);
const $$CookieBanner = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$CookieBanner;
  const locale = getLocaleFromUrl(Astro2.url);
  const lang = locale;
  const cookiePolicyHref = locale === "es" ? "/es/cookie-policy" : "/en/cookie-policy";
  return renderTemplate`${maybeRenderHead()}<div id="cookie-banner" class="fixed bottom-4 left-4 z-50 w-[300px] sm:w-[400px] bg-white border border-hairline shadow-2xl rounded-2xl p-6 transform translate-y-[150%] opacity-0 transition-all duration-700 ease-out"> <div class="flex flex-col gap-4"> <div> <h3 class="text-lg font-bold text-ink mb-2">${t(lang, "cookie.title")}</h3> <p class="text-sm text-ink/70 leading-relaxed"> ${t(lang, "cookie.message")} <a${addAttribute(cookiePolicyHref, "href")} class="text-primary hover:underline font-medium">${t(lang, "cookie.readMore")}</a> </p> </div> <div class="flex flex-col sm:flex-row gap-3"> <button id="accept-cookies" class="w-full sm:w-auto bg-primary text-white font-medium px-4 py-2.5 rounded-lg hover:bg-ink transition-colors text-sm text-center"> ${t(lang, "cookie.accept")} </button> <button id="reject-cookies" class="w-full sm:w-auto bg-surface-soft text-ink font-medium px-4 py-2.5 rounded-lg hover:bg-gray-200 transition-colors text-sm text-center border border-hairline"> ${t(lang, "cookie.reject")} </button> </div> </div> </div> ${renderScript($$result, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/CookieBanner.astro?astro&type=script&index=0&lang.ts")}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/CookieBanner.astro", void 0);
var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a, _b;
const $$BaseLayout = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$BaseLayout;
  const { title, description, image, canonical, articleSchema, pubDate, isService, isProfile, locale: propLocale } = Astro2.props;
  const locale = propLocale || getLocaleFromUrl(Astro2.url);
  const currentUrl = Astro2.url.href;
  const siteUrl = "https://selvaggiesteban.dev";
  const currentPath = Astro2.url.pathname;
  let alternatePath = currentPath;
  if (currentPath.startsWith("/es/")) {
    alternatePath = "/en" + currentPath.slice(3);
  } else if (currentPath.startsWith("/en/")) {
    alternatePath = "/es" + currentPath.slice(3);
  } else {
    alternatePath = "/en" + currentPath;
  }
  const alternateUrl = `${siteUrl}${alternatePath}`;
  const baseEntitySchema = {
    "@context": "https://schema.org",
    "@type": ["ProfessionalService", "Person"],
    "@id": `${siteUrl}/#identity`,
    "name": "Esteban Selvaggi",
    "url": siteUrl,
    "image": "https://media.licdn.com/dms/image/v2/C4E03AQEYYjT26_Y7Wg/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1628026194726?e=1746662400&v=beta&t=90Q5k3s31p6Aqz6m1k46uJ321q535q3065w019p9e9A",
    "jobTitle": locale === "en" ? "Computer Engineer" : "Ingeniero Informático",
    "description": locale === "en" ? "Computer Engineer specialized in software engineering and SEO positioning." : "Ingeniero informático especializado en ingeniería de software y posicionamiento SEO.",
    "inLanguage": locale,
    "sameAs": [
      "https://x.com/selvaggiesteban",
      "https://linkedin.com/in/selvaggiesteban",
      "https://github.com/selvaggiesteban",
      "https://selvaggiesteban.dev"
    ],
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "La Rioja 1900",
      "addressLocality": "Lanús Oeste",
      "addressRegion": "Provincia de Buenos Aires",
      "postalCode": "1824",
      "addressCountry": "AR"
    },
    "areaServed": {
      "@type": "GeoCircle",
      "description": "Worldwide"
    },
    "priceRange": "$$"
  };
  const blogSchema = articleSchema ? {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": currentUrl
    },
    "headline": title,
    "description": description,
    "author": { "@id": `${siteUrl}/#identity` },
    "publisher": { "@id": `${siteUrl}/#identity` },
    "datePublished": pubDate,
    "inLanguage": locale
  } : null;
  const serviceSchema = isService ? {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": title,
    "description": description,
    "provider": { "@id": `${siteUrl}/#identity` },
    "areaServed": "Worldwide",
    "offers": {
      "@type": "Offer",
      "price": "16.00",
      "priceCurrency": "USD",
      "description": locale === "en" ? "Base price from 16 USD" : "Precio base desde 16 USD / 16.000 ARS"
    }
  } : null;
  const profileSchema = isProfile ? {
    "@context": "https://schema.org",
    "@type": "ProfilePage",
    "mainEntity": { "@id": `${siteUrl}/#identity` }
  } : null;
  const schemas = [baseEntitySchema, blogSchema, serviceSchema, profileSchema].filter(Boolean);
  return renderTemplate(_b || (_b = __template(["<html", '> <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><link rel="icon" type="image/svg+xml" href="/favicon.svg"><meta name="generator"', ">", '<meta property="og:locale"', '><meta property="og:locale:alternate"', '><link rel="alternate"', "", '><link rel="alternate"', "", '><link rel="alternate" hreflang="x-default"', ">", "", "</head> <body> ", " <main> ", " </main> ", " ", " ", " <script>\n      const observerOptions = {\n        threshold: 0.1\n      };\n\n      const observer = new IntersectionObserver((entries) => {\n        entries.forEach(entry => {\n          if (entry.isIntersecting) {\n            entry.target.classList.add('in');\n            observer.unobserve(entry.target);\n          }\n        });\n      }, observerOptions);\n\n      function initReveal() {\n        document.querySelectorAll('.reveal:not(.in)').forEach(el => observer.observe(el));\n      }\n\n      initReveal();\n      document.addEventListener('astro:after-swap', initReveal);\n    <\/script> </body> </html>"])), addAttribute(locale, "lang"), addAttribute(Astro2.generator, "content"), renderComponent($$result, "SEO", $$SEO, { "title": title, "description": description, "image": image, "canonical": canonical }), addAttribute(locale === "es" ? "es_AR" : "en_US", "content"), addAttribute(locale === "es" ? "en_US" : "es_AR", "content"), addAttribute(locale, "hreflang"), addAttribute(currentUrl, "href"), addAttribute(locale === "es" ? "en" : "es", "hreflang"), addAttribute(alternateUrl, "href"), addAttribute(`${siteUrl}${currentPath.startsWith("/en") ? currentPath : currentPath}`, "href"), schemas.map((schema) => renderTemplate(_a || (_a = __template(['<script type="application/ld+json">', "<\/script>"])), unescapeHTML(JSON.stringify(schema)))), renderHead(), renderComponent($$result, "Navbar", $$Navbar, {}), renderSlot($$result, $$slots["default"]), renderComponent($$result, "WhatsAppButton", $$WhatsAppButton, { "phone": "1153323937" }), renderComponent($$result, "Footer", $$Footer, {}), renderComponent($$result, "CookieBanner", $$CookieBanner, {}));
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/layouts/BaseLayout.astro", void 0);
export {
  $$BaseLayout as $
};
