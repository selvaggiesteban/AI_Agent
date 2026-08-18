import { defineMiddleware } from "astro:middleware";

export const onRequest = defineMiddleware((context, next) => {
  const { url, cookies, redirect } = context;

  // Protect the CRM dashboard and any budget management routes
  if (
    url.pathname === "/presupuestos" ||
    url.pathname === "/presupuestos/" ||
    url.pathname.startsWith("/presupuestos/index") ||
    url.pathname.startsWith("/presupuestos/nuevo")
  ) {
    // Check for the session cookie
    if (!cookies.has("admin_session")) {
      // If no valid session, redirect to the login page
      return redirect("/login");
    }
  }

  // Allow the request to proceed if authenticated or not on a protected route
  return next();
});