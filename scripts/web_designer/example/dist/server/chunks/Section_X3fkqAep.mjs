globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { v as maybeRenderHead, a0 as addAttribute, bm as renderSlot, K as renderTemplate } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { d as $$Container } from "./global_tQVAIOUq.mjs";
const $$Section = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$Section;
  const { variant = "white", class: className, fullWidth = false } = Astro2.props;
  const variants = {
    white: "bg-canvas text-ink",
    lime: "bg-block-lime text-ink",
    lilac: "bg-block-lilac text-ink",
    cream: "bg-block-cream text-ink",
    mint: "bg-block-mint text-ink",
    pink: "bg-block-pink text-ink",
    coral: "bg-block-coral text-ink",
    navy: "bg-block-navy text-inverse-ink"
  };
  return renderTemplate`${maybeRenderHead()}<section${addAttribute(["py-section", variants[variant], className], "class:list")}> ${fullWidth ? renderTemplate`${renderSlot($$result, $$slots["default"])}` : renderTemplate`${renderComponent($$result, "Container", $$Container, {}, { "default": ($$result2) => renderTemplate` <div${addAttribute([variant !== "white" ? "section-block" : ""], "class:list")}> ${renderSlot($$result2, $$slots["default"])} </div> ` })}`} </section>`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/Section.astro", void 0);
export {
  $$Section as $
};
