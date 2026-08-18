-- Clientes
CREATE TABLE IF NOT EXISTS clientes (
  id TEXT PRIMARY KEY,
  nombre TEXT NOT NULL,
  empresa TEXT,
  cuit TEXT,
  iva TEXT,
  domicilio TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Presupuestos
CREATE TABLE IF NOT EXISTS presupuestos (
  id TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL,
  proyecto TEXT NOT NULL,
  monto_total INTEGER DEFAULT 0,
  estado TEXT DEFAULT 'borrador',
  fecha_emision TEXT,
  fecha_vto TEXT,
  condicion_venta TEXT DEFAULT 'Transferencia / MercadoPago (Contado)',
  mp_preference_id TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- Items de presupuesto
CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  presupuesto_id TEXT NOT NULL,
  codigo TEXT,
  descripcion TEXT NOT NULL,
  cantidad INTEGER DEFAULT 1,
  unidad TEXT DEFAULT 'unid',
  precio_unitario INTEGER DEFAULT 0,
  bonificacion INTEGER DEFAULT 0,
  FOREIGN KEY (presupuesto_id) REFERENCES presupuestos(id)
);

-- Seed: datos existentes (María Agustina - Identidad Marketing)
INSERT OR IGNORE INTO clientes (id, nombre, empresa) VALUES
  ('cliente-identidad-marketing', 'María Agustina', 'Identidad Marketing Digital'),
  ('cliente-mora-garcia', 'Mora García', 'Particular');

INSERT OR IGNORE INTO presupuestos (id, cliente_id, proyecto, monto_total, estado, fecha_emision, fecha_vto) VALUES
  ('08062026-identidad-marketing', 'cliente-identidad-marketing', 'Sitio Web Institucional', 363500, 'enviado', '08/06/2026', '22/06/2026'),
  ('08062026-mora-garcia', 'cliente-mora-garcia', 'Landing Page Festival', 128500, 'borrador', '08/06/2026', '22/06/2026');
