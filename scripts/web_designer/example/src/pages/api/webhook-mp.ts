import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json() as any;
    const { type, data } = body;

    if (type !== 'payment') {
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    }

    const paymentId = data?.id;
    if (!paymentId) {
      return new Response(JSON.stringify({ error: 'No payment id' }), { status: 400 });
    }

    const MP_ACCESS_TOKEN = env?.MP_ACCESS_TOKEN;
    if (!MP_ACCESS_TOKEN) {
      return new Response(JSON.stringify({ error: 'MP token missing' }), { status: 500 });
    }

    // Fetch payment details from MercadoPago
    const mpRes = await fetch(`https://api.mercadopago.com/v1/payments/${paymentId}`, {
      headers: { Authorization: `Bearer ${MP_ACCESS_TOKEN}` },
    });
    const payment = await mpRes.json() as any;

    if (payment.status === 'approved' && payment.external_reference) {
      const presupuestoId = payment.external_reference;
      const db = env?.DB as D1Database | undefined;
      if (db) {
        await db
          .prepare('UPDATE presupuestos SET estado = ?, updated_at = datetime(\'now\') WHERE id = ?')
          .bind('pagado', presupuestoId)
          .run();
      }
    }

    return new Response(JSON.stringify({ ok: true }), { status: 200 });
  } catch (err) {
    console.error('Webhook MP error:', err);
    return new Response(JSON.stringify({ error: 'Internal error' }), { status: 500 });
  }
};
