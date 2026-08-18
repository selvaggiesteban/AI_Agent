globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead, a0 as addAttribute } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$PresupuestoLayout } from "./PresupuestoLayout_Dm1ew5YS.mjs";
import { $ as $$Button } from "./global_tQVAIOUq.mjs";
import { env } from "cloudflare:workers";
const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  let presupuestos = [];
  try {
    const db = env?.DB;
    if (db) {
      const result = await db.prepare(`SELECT p.id, p.proyecto, p.monto_total, p.estado, p.fecha_emision,
                c.nombre as cliente, c.empresa
                FROM presupuestos p JOIN clientes c ON p.cliente_id = c.id
                ORDER BY p.created_at DESC`).all();
      presupuestos = result.results.map((p) => ({
        id: p.id,
        cliente: p.cliente,
        empresa: p.empresa || "",
        proyecto: p.proyecto,
        monto: `$${Number(p.monto_total).toLocaleString("es-AR")} ARS`,
        fecha: p.fecha_emision,
        estado: p.estado
      }));
    }
  } catch {
  }
  if (presupuestos.length === 0) {
    presupuestos = [
      { id: "08062026-identidad-marketing", cliente: "María Agostina", empresa: "Identidad Marketing Digital", proyecto: "Sitio Web Institucional", monto: "$363.500 ARS", fecha: "08/06/2026", estado: "enviado" },
      { id: "08062026-mora-garcia", cliente: "Mora García", empresa: "Particular", proyecto: "Landing Page Festival", monto: "$128.500 ARS", fecha: "08/06/2026", estado: "borrador" }
    ];
  }
  const getStatusColor = (status) => {
    switch (status) {
      case "pagado":
        return "bg-semantic-success/10 text-semantic-success border-semantic-success/20";
      case "enviado":
        return "bg-primary/10 text-primary border-primary/20";
      default:
        return "bg-ink/5 text-ink/60 border-hairline";
    }
  };
  return renderTemplate`${renderComponent($$result, "PresupuestoLayout", $$PresupuestoLayout, { "title": "Panel de Presupuestos | CRM Interno", "description": "Panel de gestión de presupuestos." }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="mb-12 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"> <div> <h1 class="text-3xl font-bold text-ink mb-2">Panel de Presupuestos</h1> <p class="text-ink/60">Gestiona y consulta el estado de tus cotizaciones enviadas.</p> </div> ${renderComponent($$result2, "Button", $$Button, { "href": "/presupuestos/nuevo", "variant": "primary", "class": "flex items-center gap-2" }, { "default": async ($$result3) => renderTemplate` <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="M12 5v14"></path></svg>
Nuevo Presupuesto
` })} </div> <div class="bg-white rounded-[9px] shadow-sm border border-hairline overflow-hidden"> <div class="overflow-x-auto"> <table class="w-full text-left text-sm whitespace-nowrap"> <thead class="bg-surface-soft border-b border-hairline text-ink/70 uppercase text-xs tracking-wider"> <tr> <th class="p-4 font-bold">ID / Fecha</th> <th class="p-4 font-bold">Cliente</th> <th class="p-4 font-bold">Proyecto</th> <th class="p-4 font-bold text-right">Monto Total</th> <th class="p-4 font-bold text-center">Estado</th> <th class="p-4 font-bold text-right">Acciones</th> </tr> </thead> <tbody class="divide-y divide-hairline"> ${presupuestos.map((p) => renderTemplate`<tr class="hover:bg-surface-soft/50 transition-colors"> <td class="p-4"> <span class="font-mono text-xs text-ink/60 block mb-1">${p.id}</span> <span class="text-ink/80">${p.fecha}</span> </td> <td class="p-4"> <span class="font-bold text-ink block">${p.cliente}</span> <span class="text-xs text-ink/60">${p.empresa}</span> </td> <td class="p-4 text-ink/80">${p.proyecto}</td> <td class="p-4 text-right font-medium">${p.monto}</td> <td class="p-4 text-center"> <span${addAttribute(`text-[10px] uppercase tracking-widest font-bold px-3 py-1 rounded-full border ${getStatusColor(p.estado)}`, "class")}> ${p.estado} </span> </td> <td class="p-4 text-right"> <a${addAttribute(`/presupuestos/${p.id}`, "href")} target="_blank" class="inline-flex items-center gap-2 text-primary hover:underline font-medium text-xs">
Ver Documento
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg> </a> </td> </tr>`)} </tbody> </table> </div> </div> <div class="mt-8 text-center text-sm text-ink/40 font-mono flex items-center justify-center gap-2"> <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
Acceso Restringido - Sólo Personal Autorizado
</div> ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/presupuestos/index.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/presupuestos/index.astro";
const $$url = "/presupuestos";
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
