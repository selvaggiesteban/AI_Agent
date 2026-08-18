globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { K as renderTemplate, v as maybeRenderHead, a0 as addAttribute } from "./sequence_BvoC4k2m.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$PresupuestoLayout } from "./PresupuestoLayout_Dm1ew5YS.mjs";
import { env } from "cloudflare:workers";
const $$08062026IdentidadMarketing = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$08062026IdentidadMarketing;
  const miRazonSocial = "SELVAGGI ESTEBAN";
  const miDomicilio = "La Rioja 1935 - Villa Industriales, Buenos Aires";
  const miCuit = "20433102593";
  const fechaEmision = "12/06/2026";
  const fechaVto = "19/06/2026";
  const clienteNombre = "María Agostina";
  const clienteEmpresa = "Identidad Marketing Digital";
  const condicionVenta = "MercadoPago";
  const proyecto = "Desarrollo de Sitio Web Institucional";
  const urlPresupuesto = "https://selvaggiesteban.dev/presupuestos/08062026-identidad-marketing";
  let payLink = "#";
  try {
    const mpResponse = await fetch("https://api.mercadopago.com/checkout/preferences", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.MP_ACCESS_TOKEN || process.env.MP_ACCESS_TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        items: [
          {
            title: "Sitio Web Institucional - Identidad Marketing Digital",
            quantity: 1,
            unit_price: 32e4,
            currency_id: "ARS"
          },
          {
            title: "Landing Page - Identidad Marketing Digital",
            quantity: 1,
            unit_price: 16e4,
            currency_id: "ARS"
          }
        ],
        back_urls: {
          success: "https://selvaggiesteban.dev/",
          failure: "https://selvaggiesteban.dev/",
          pending: "https://selvaggiesteban.dev/"
        },
        auto_return: "approved"
      })
    });
    const mpData = await mpResponse.json();
    payLink = mpData.init_point || "#";
  } catch (error) {
    console.error("Error al generar el link de Mercado Pago:", error);
  }
  return renderTemplate`${renderComponent($$result, "PresupuestoLayout", $$PresupuestoLayout, { "title": `Presupuesto: ${proyecto}`, "description": `Propuesta comercial para ${clienteNombre}` }, { "default": async ($$result2) => renderTemplate`  ${maybeRenderHead()}<div class="flex justify-end gap-3 mb-6" style="margin-top: 50px;"> <button onclick="navigator.clipboard.writeText(window.location.href); alert('Enlace copiado al portapapeles');" class="p-2 bg-surface-soft border border-hairline rounded-full hover:bg-ink hover:text-white transition-colors text-ink" title="Copiar Enlace"> <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg> </button> <button onclick="window.print()" class="p-2 bg-surface-soft border border-hairline rounded-full hover:bg-ink hover:text-white transition-colors text-ink hidden sm:inline-block" title="Imprimir Presupuesto"> <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect width="12" height="8" x="6" y="14"></rect></svg> </button> <a${addAttribute(`mailto:?subject=Presupuesto%20Web%20-%20SelvaggiEsteban.dev&body=Hola!%20Te%20comparto%20el%20link%20de%20la%20cotizaci%C3%B3n:%20${urlPresupuesto}`, "href")} class="p-2 bg-surface-soft border border-hairline rounded-full hover:bg-ink hover:text-white transition-colors text-ink" title="Compartir por Email"> <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"></rect><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path></svg> </a> <a${addAttribute(`https://api.whatsapp.com/send?text=Hola,%20aquí%20tienes%20el%20presupuesto%20del%20sitio%20web:%20${urlPresupuesto}`, "href")} target="_blank" class="p-2 bg-surface-soft border border-hairline rounded-full hover:bg-[#25D366] hover:text-white transition-colors text-ink" title="Compartir por WhatsApp"> <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"></path><path d="M3 21l1.65 -3.8a9 9 0 1 1 3.4 2.9l-5.05 .9"></path><path d="M9 10a.5 .5 0 0 0 1 0v-1a.5 .5 0 0 0 -1 0v1a5 5 0 0 0 5 5h1a.5 .5 0 0 0 0 -1h-1a.5 .5 0 0 0 0 1"></path></svg> </a> <a${addAttribute(`https://t.me/share/url?url=${urlPresupuesto}&text=Presupuesto%20Web`, "href")} target="_blank" class="p-2 bg-surface-soft border border-hairline rounded-full hover:bg-[#0088cc] hover:text-white transition-colors text-ink" title="Compartir por Telegram"> <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"></path><path d="M15 10l-4 4l6 6l4 -16l-18 7l4 2l2 6l3 -4"></path></svg> </a> </div> <div class="mb-8"> <!-- Encabezado de Facturación / Presupuesto --> <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12 border-b border-hairline-soft pb-8"> <div> <h1 class="text-3xl font-bold text-ink mb-6">Presupuesto</h1> <div class="text-sm text-ink/80 space-y-1"> <p><span class="font-bold">Razón Social:</span> ${miRazonSocial}</p> <p><span class="font-bold">CUIT:</span> ${miCuit}</p> <p><span class="font-bold">Domicilio Comercial:</span> ${miDomicilio}</p> </div> </div> <div class="md:text-right text-sm text-ink/80 space-y-1 bg-surface-soft p-5 rounded-[9px] border border-hairline"> <p><span class="font-bold">Fecha de emisión:</span> ${fechaEmision}</p> <p><span class="font-bold text-primary">Válido hasta:</span> ${fechaVto}</p> <div class="my-4 border-t border-hairline-soft"></div> <p><span class="font-bold">Apellido y nombre / Razón social:</span> ${clienteNombre} (${clienteEmpresa})</p> <p><span class="font-bold">CUIT:</span> ${renderTemplate`<span class="text-red-500 font-normal">A COMPLETAR</span>`}</p> <p><span class="font-bold">Condición IVA:</span> ${renderTemplate`<span class="text-red-500 font-normal">A COMPLETAR</span>`}</p> <p><span class="font-bold">Domicilio:</span> ${renderTemplate`<span class="text-red-500 font-normal">A COMPLETAR</span>`}</p> <p><span class="font-bold">Condición de Venta:</span> ${condicionVenta}</p> </div> </div> <!-- Tabla de Facturación --> <div class="overflow-x-auto mb-8 border border-hairline rounded-[9px]"> <table class="w-full text-left text-sm whitespace-nowrap"> <thead class="bg-surface-soft border-b border-hairline text-ink/70 uppercase text-xs tracking-wider"> <tr> <th class="p-4 font-bold">Código</th> <th class="p-4 font-bold">Producto / Servicio</th> <th class="p-4 font-bold text-right">Cantidad</th> <th class="p-4 font-bold text-center">U. Medida</th> <th class="p-4 font-bold text-right">Precio Unit.</th> <th class="p-4 font-bold text-right">% Bonif</th> <th class="p-4 font-bold text-right">Imp. Bonif.</th> <th class="p-4 font-bold text-right">Subtotal</th> </tr> </thead> <tbody class="divide-y divide-hairline"> <tr class="hover:bg-surface-soft/50 transition-colors"> <td class="p-4 font-mono text-xs text-ink/60">DEV-01</td> <td class="p-4 font-bold text-ink whitespace-normal min-w-[200px]">${proyecto}</td> <td class="p-4 text-right">1.00</td> <td class="p-4 text-center">unidades</td> <td class="p-4 text-right">$320.000,00</td> <td class="p-4 text-right">0.00</td> <td class="p-4 text-right">$0,00</td> <td class="p-4 text-right font-bold">$320.000,00</td> </tr> <tr class="hover:bg-surface-soft/50 transition-colors"> <td class="p-4 font-mono text-xs text-ink/60">DEV-02</td> <td class="p-4 font-bold text-ink whitespace-normal min-w-[200px]">Landing Page: Identidad Marketing Digital</td> <td class="p-4 text-right">1.00</td> <td class="p-4 text-center">unidades</td> <td class="p-4 text-right">$160.000,00</td> <td class="p-4 text-right">0.00</td> <td class="p-4 text-right">$0,00</td> <td class="p-4 text-right font-bold">$160.000,00</td> </tr> <tr class="hover:bg-surface-soft/50 transition-colors"> <td class="p-4 font-mono text-xs text-ink/60">HOS-01</td> <td class="p-4 whitespace-normal min-w-[200px]">Hosting y Soporte Técnico (Mensual)<br><em class="text-xs text-ink/60">*Actualización trimestral IPC</em></td> <td class="p-4 text-right">1.00</td> <td class="p-4 text-center">meses</td> <td class="p-4 text-right">$35.000,00</td> <td class="p-4 text-right">0.00</td> <td class="p-4 text-right">$0,00</td> <td class="p-4 text-right font-medium">$35.000,00</td> </tr> <tr class="hover:bg-surface-soft/50 transition-colors"> <td class="p-4 font-mono text-xs text-ink/60">DOM-01</td> <td class="p-4 whitespace-normal min-w-[200px]">Renovación de Dominio .com.ar (Anual)<br><em class="text-xs text-ink/60">*Costo aproximado Nic.ar</em></td> <td class="p-4 text-right">1.00</td> <td class="p-4 text-center">unidades</td> <td class="p-4 text-right">$8.500,00</td> <td class="p-4 text-right">0.00</td> <td class="p-4 text-right">$0,00</td> <td class="p-4 text-right font-medium">$8.500,00</td> </tr> </tbody> </table> </div> <!-- Totales: ancho completo --> <div class="mb-8 bg-surface-soft rounded-[9px] p-6 border border-hairline space-y-3"> <div class="flex justify-between items-center text-sm text-ink/80"> <span>Subtotal:</span> <span class="font-medium">$523.500,00</span> </div> <div class="flex justify-between items-center text-sm text-ink/80 border-b border-hairline-soft pb-3"> <span>Importe Otros Tributos:</span> <span class="font-medium">$0,00</span> </div> <div class="flex justify-between items-center text-xl font-bold text-primary pt-2"> <span>Importe Total:</span> <span>$523.500,00</span> </div> </div> <!-- Detalle de la propuesta: sección completa, debajo del subtotal --> <div class="mb-12"> <h2 class="text-xl font-bold mb-2">Detalle de la propuesta</h2> <p class="text-ink/60 text-lg mb-8">${proyecto}</p> <div class="prose prose-ink max-w-none"> <h3>El desafío</h3><p>Creación de un sitio web institucional ultrarrápido, seguro y optimizado para motores de búsqueda (SEO) y alta conversión. El ecosistema digital estará basado en tecnologías de vanguardia (Astro + Cloudflare) garantizando tiempos de carga inferiores a un segundo.</p><h3>Alcance del proyecto</h3><ul><li><strong>Diseño y Desarrollo Frontend:</strong> Interfaz gráfica a medida con enfoque "mobile-first".</li><li><strong>Arquitectura Serverless:</strong> Alojamiento en la red global de Cloudflare Pages.</li><li><strong>Formulario de Contacto Avanzado:</strong> Integración de formularios conectados vía API (Resend) con anti-spam Turnstile.</li><li><strong>Optimización SEO Técnica:</strong> Configuración de metadatos, optimización Core Web Vitals e inyección de Schema.org.</li></ul> </div> </div> <!-- Cierre y Pago --> <div class="text-center pt-8 border-t border-hairline-soft"> <h3 class="text-lg font-bold mb-4">¿Todo listo para comenzar?</h3> <p class="text-ink/60 mb-6 text-sm mx-auto">Al realizar el pago total o la seña inicial según la condición de venta acordada, confirmas la aceptación del presupuesto y damos inicio formal al proyecto.</p> <a${addAttribute(payLink, "href")} target="_blank" class="inline-flex items-center justify-center gap-3 bg-[#009EE3] hover:bg-[#0088cc] text-white rounded-[9px] px-8 py-4 font-semibold text-lg transition-colors shadow-md mx-auto w-full sm:w-auto"> <img src="/assets/mp/mercadopago.svg" alt="Mercado Pago" class="h-6 object-contain">
Pagar con Mercado Pago
</a> <div class="mt-6 flex flex-wrap justify-center items-center gap-3 opacity-90"> <span class="flex items-center justify-center h-8 max-w-[100px] min-w-[64px] px-2"><img src="/assets/mp/visa.svg" alt="Visa" class="h-8 w-auto object-contain" title="Visa"></span> <span class="flex items-center justify-center h-8 max-w-[100px] min-w-[64px] px-2"><img src="/assets/mp/mastercard.svg" alt="Mastercard" class="h-8 w-auto object-contain" title="Mastercard"></span> <span class="flex items-center justify-center h-8 max-w-[100px] min-w-[64px] px-2"><img src="/assets/mp/amex.svg" alt="American Express" class="h-8 w-auto object-contain" title="American Express"></span> <span class="flex items-center justify-center h-8 max-w-[100px] min-w-[64px] px-2"><img src="/assets/mp/naranjax.svg" alt="Naranja X" class="h-8 w-auto object-contain" title="Naranja X"></span> <span class="flex items-center justify-center h-8 max-w-[100px] min-w-[64px] px-2"><img src="/assets/mp/pagofacil.svg" alt="Pago Fácil" class="h-8 w-auto object-contain" title="Pago Fácil"></span> <span class="flex items-center justify-center h-8 max-w-[100px] min-w-[64px] px-2"><img src="/assets/mp/rapipago.svg" alt="Rapipago" class="h-8 w-auto object-contain" title="Rapipago"></span> </div> </div> </div> ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/presupuestos/08062026-identidad-marketing.astro", void 0);
const $$file = "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/pages/presupuestos/08062026-identidad-marketing.astro";
const $$url = "/presupuestos/08062026-identidad-marketing";
const _page = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: $$08062026IdentidadMarketing,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: "Module" }));
const page = () => _page;
export {
  page
};
