import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';

function slugify(str: string) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function dateSlug() {
  const d = new Date();
  return `${String(d.getDate()).padStart(2,'0')}${String(d.getMonth()+1).padStart(2,'0')}${d.getFullYear()}`;
}

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json() as any;
    const { cliente, items, proyecto, condicionVenta } = body;

    if (!cliente?.nombre || !proyecto || !items?.length) {
      return new Response(JSON.stringify({ error: 'Faltan campos obligatorios' }), { status: 400 });
    }

    const db = env?.DB as D1Database | undefined;
    if (!db) {
      return new Response(JSON.stringify({ error: 'Base de datos no disponible' }), { status: 500 });
    }

    // Generate IDs
    const clienteId = `cliente-${slugify(cliente.nombre)}-${Date.now()}`;
    const presupuestoId = `${dateSlug()}-${slugify(cliente.empresa || cliente.nombre)}`;
    const today = new Date();
    const fechaEmision = `${String(today.getDate()).padStart(2,'0')}/${String(today.getMonth()+1).padStart(2,'0')}/${today.getFullYear()}`;
    const vto = new Date(today.getTime() + 14 * 24 * 60 * 60 * 1000);
    const fechaVto = `${String(vto.getDate()).padStart(2,'0')}/${String(vto.getMonth()+1).padStart(2,'0')}/${vto.getFullYear()}`;

    // Calculate total
    const montoTotal = items.reduce((sum: number, item: any) => {
      const subtotal = (item.cantidad || 1) * (item.precioUnitario || 0);
      const bonif = subtotal * ((item.bonificacion || 0) / 100);
      return sum + subtotal - bonif;
    }, 0);

    // Insert cliente
    await db.prepare(
      'INSERT OR IGNORE INTO clientes (id, nombre, empresa, cuit, iva, domicilio) VALUES (?, ?, ?, ?, ?, ?)'
    ).bind(clienteId, cliente.nombre, cliente.empresa || '', cliente.cuit || '', cliente.iva || '', cliente.domicilio || '').run();

    // Insert presupuesto
    await db.prepare(
      'INSERT INTO presupuestos (id, cliente_id, proyecto, monto_total, estado, fecha_emision, fecha_vto, condicion_venta) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    ).bind(presupuestoId, clienteId, proyecto, montoTotal, 'borrador', fechaEmision, fechaVto, condicionVenta || 'Transferencia / MercadoPago (Contado)').run();

    // Insert items
    for (const item of items) {
      await db.prepare(
        'INSERT INTO items (presupuesto_id, codigo, descripcion, cantidad, unidad, precio_unitario, bonificacion) VALUES (?, ?, ?, ?, ?, ?, ?)'
      ).bind(presupuestoId, item.codigo || '', item.descripcion, item.cantidad || 1, item.unidad || 'unid', item.precioUnitario || 0, item.bonificacion || 0).run();
    }

    return new Response(JSON.stringify({
      ok: true,
      id: presupuestoId,
      url: `/presupuestos/${presupuestoId}`
    }), { status: 201 });
  } catch (err) {
    console.error('presupuesto-create error:', err);
    return new Response(JSON.stringify({ error: 'Error interno' }), { status: 500 });
  }
};
