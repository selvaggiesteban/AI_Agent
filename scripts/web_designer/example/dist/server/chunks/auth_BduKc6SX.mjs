globalThis.process ??= {};
globalThis.process.env ??= {};
import { env } from "cloudflare:workers";
function getLocale(request) {
  const referer = request.headers.get("referer") || "";
  if (referer.includes("/en/")) return "en";
  return "es";
}
const errors = {
  es: {
    config: "Configuración del servidor incompleta.",
    wrongPassword: "Contraseña incorrecta.",
    requestError: "Error en la solicitud."
  },
  en: {
    config: "Incomplete server configuration.",
    wrongPassword: "Incorrect password.",
    requestError: "Request error."
  }
};
const POST = async ({ request, cookies }) => {
  try {
    const data = await request.json();
    const lang = getLocale(request);
    const t = errors[lang];
    const masterPassword = env.MASTER_PASSWORD || process.env.MASTER_PASSWORD;
    if (!masterPassword) {
      return new Response(JSON.stringify({ error: t.config }), { status: 500 });
    }
    if (data.password === masterPassword) {
      cookies.set("admin_session", "authenticated", {
        path: "/",
        httpOnly: true,
        secure: true,
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 7
      });
      return new Response(JSON.stringify({ success: true }), { status: 200 });
    }
    return new Response(JSON.stringify({ error: t.wrongPassword }), { status: 401 });
  } catch (error) {
    return new Response(JSON.stringify({ error: errors.es.requestError }), { status: 400 });
  }
};
const _page = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  POST
}, Symbol.toStringTag, { value: "Module" }));
const page = () => _page;
export {
  page
};
