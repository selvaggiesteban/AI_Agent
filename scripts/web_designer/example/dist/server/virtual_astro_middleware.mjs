globalThis.process ??= {};
globalThis.process.env ??= {};
import { d as defineMiddleware, s as sequence } from "./chunks/sequence_BvoC4k2m.mjs";
const onRequest$1 = defineMiddleware((context, next) => {
  const { url, cookies, redirect } = context;
  if (url.pathname === "/presupuestos" || url.pathname === "/presupuestos/" || url.pathname.startsWith("/presupuestos/index") || url.pathname.startsWith("/presupuestos/nuevo")) {
    if (!cookies.has("admin_session")) {
      return redirect("/login");
    }
  }
  return next();
});
const onRequest = sequence(
  onRequest$1
);
export {
  onRequest
};
