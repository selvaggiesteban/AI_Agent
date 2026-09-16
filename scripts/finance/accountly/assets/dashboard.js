// Lógica de Renderizado del Dashboard

document.addEventListener('DOMContentLoaded', () => {
    if (typeof FINANCIAL_DATA === 'undefined') return;

    renderMetrics(FINANCIAL_DATA);
    renderMainChart(FINANCIAL_DATA.monthly_history);
    renderMonthlyTable(FINANCIAL_DATA.monthly_history);
    
    // Nuevas funciones
    render2025Chart(FINANCIAL_DATA);
    renderMonthlyCards(FINANCIAL_DATA.potential_clients);
});

function formatCurrency(value) {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value);
}

function renderMonthlyCards(clientsData) {
    const container = document.getElementById('monthly-cards-container');
    if (!container) {
        console.error("Container 'monthly-cards-container' not found.");
        return;
    }
    
    if (!clientsData || !Array.isArray(clientsData)) {
        container.innerHTML = '<div class="col-12 text-muted">Sin datos de ingresos.</div>';
        return;
    }

    try {
        // 1. Agrupar por Mes
        const monthlyGroups = {}; 

        clientsData.forEach(client => {
            if (!client.details) return;
            
            client.details.forEach(tx => {
                if (!tx.date) return;
                
                // tx.date es dd/mm/yyyy
                const parts = tx.date.split('/');
                if (parts.length !== 3) return;
                
                const day = parts[0];
                const month = parts[1];
                const year = parts[2];
                const key = `${year}-${month}`;
                
                if (!monthlyGroups[key]) {
                    // Crear objeto de mes
                    // month en Date es 0-indexado (0=Enero)
                    const dateObj = new Date(parseInt(year), parseInt(month) - 1, 1);
                    const monthName = dateObj.toLocaleString('es-AR', { month: 'long', year: 'numeric' });
                    
                    monthlyGroups[key] = { 
                        total: 0, 
                        label: monthName.charAt(0).toUpperCase() + monthName.slice(1), // Capitalizar
                        timestamp: dateObj.getTime(),
                        items: [] 
                    };
                }
                
                monthlyGroups[key].total += tx.amount;
                monthlyGroups[key].items.push({
                    name: client.name || "Desconocido",
                    amount: tx.amount,
                    day: day,
                    isInvoiced: tx.is_invoiced
                });
            });
        });

        // 2. Convertir a array y ordenar (Más reciente primero)
        const sortedMonths = Object.values(monthlyGroups).sort((a, b) => b.timestamp - a.timestamp);

        // 3. Generar HTML
        if (sortedMonths.length === 0) {
            container.innerHTML = '<div class="col-12 text-muted">No hay ingresos identificados para mostrar.</div>';
            return;
        }

        container.innerHTML = sortedMonths.map(m => {
            // Ordenar items del mes por día (descendiente)
            m.items.sort((a, b) => parseInt(b.day) - parseInt(a.day));

            const listHtml = m.items.map(i => {
                const statusIcon = i.isInvoiced 
                    ? '<span class="text-success" title="Factura Encontrada">✅</span>' 
                    : '<span class="text-warning" title="Falta Factura de Respaldo">⚠️</span>';
                
                return `
                <div class="d-flex justify-content-between border-bottom border-secondary py-1" style="font-size: 0.75rem;">
                    <div class="text-truncate" style="max-width: 70%;" title="${i.name}">
                        ${statusIcon} <span class="text-muted me-1">${i.day}</span> ${i.name}
                    </div>
                    <div class="${i.isInvoiced ? 'text-muted' : 'text-white'}">${formatCurrency(i.amount)}</div>
                </div>
                `;
            }).join('');

            return `
            <div class="col-md-4 col-lg-3 mb-3">
                <div class="card h-100 border-secondary shadow-sm">
                    <div class="card-header bg-dark border-secondary d-flex justify-content-between align-items-center py-2">
                        <span class="fw-bold text-white small">${m.label}</span>
                        <span class="badge bg-success" style="font-size: 0.8rem;">${formatCurrency(m.total)}</span>
                    </div>
                    <div class="card-body p-2 bg-dark" style="max-height: 300px; overflow-y: auto;">
                        ${listHtml}
                    </div>
                </div>
            </div>
            `;
        }).join('');
        
    } catch (e) {
        console.error("Error rendering monthly cards:", e);
        container.innerHTML = `<div class="col-12 text-danger">Error visualizando datos: ${e.message}</div>`;
    }
}

function render2025Chart(data) {
    const ctx = document.getElementById('chart2025').getContext('2d');
    
    // 1. Estructura base de meses 2025
    const months = Array.from({length: 12}, (_, i) => {
        return { 
            index: i, 
            label: new Date(2025, i, 1).toLocaleString('es-AR', { month: 'short' }),
            arca: 0
        };
    });

    // 2. Llenar Facturación ARCA (Facturado Real)
    data.monthly_history.forEach(h => {
        if (h.month.startsWith('2025-')) {
            const monthIndex = parseInt(h.month.split('-')[1]) - 1;
            if (months[monthIndex]) {
                months[monthIndex].arca = h.arca;
            }
        }
    });

    // 3. Preparar Datasets para Chart.js
    // Dataset 0: ARCA (Base)
    const datasets = [{
        label: 'Facturado (ARCA)',
        data: months.map(m => m.arca),
        backgroundColor: '#0d6efd',
        stack: 'Stack 0',
        order: 1
    }];

    // Línea de límite $1.5M
    const limitData = Array(12).fill(1500000);
    datasets.push({
        type: 'line',
        label: 'Límite Sugerido ($1.5M)',
        data: limitData,
        borderColor: '#dc3545',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
        order: -1
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months.map(m => m.label),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1500000, // Techo visual solicitado
                    grid: { color: '#333' },
                    ticks: { color: '#aaa' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#aaa' }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                },
                legend: {
                    labels: { color: '#aaa', boxWidth: 12 }
                }
            }
        }
    });
}

function formatCurrency(value) {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value);
}

function renderMetrics(data) {
    document.getElementById('total-arca').textContent = formatCurrency(data.totals.arca);
    document.getElementById('total-ingresos').textContent = formatCurrency(data.totals.income);
    document.getElementById('total-egresos').textContent = formatCurrency(data.totals.expenses);
    
    const neto = document.getElementById('resultado-neto');
    neto.textContent = formatCurrency(data.totals.result);
    neto.className = `metric-value ${data.totals.result >= 0 ? 'text-ingresos' : 'text-egresos'}`;
}

function renderMainChart(history) {
    const ctx = document.getElementById('mainChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: history.map(h => h.month),
            datasets: [
                {
                    label: 'Ingresos Reales',
                    data: history.map(h => h.income),
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Egresos',
                    data: history.map(h => h.expenses),
                    borderColor: '#dc3545',
                    tension: 0.4
                },
                {
                    label: 'Facturado ARCA',
                    data: history.map(h => h.arca),
                    borderColor: '#0d6efd',
                    borderDash: [5, 5],
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'bottom', labels: { color: '#aaa', boxWidth: 12 } }
            },
            scales: {
                y: { grid: { color: '#333' }, ticks: { color: '#888' } },
                x: { grid: { display: false }, ticks: { color: '#888' } }
            }
        }
    });
}

function renderRecurringChart(concepts) {
    const ctx = document.getElementById('recurringChart').getContext('2d');
    const top5 = concepts.slice(0, 5);
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: top5.map(c => c.name),
            datasets: [{
                data: top5.map(c => c.total),
                backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff'],
                borderWidth: 2,
                borderColor: '#1e1e1e'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { color: '#aaa', boxWidth: 10, font: { size: 10 } } } }
        }
    });
}

function renderConceptsTable(concepts) {
    const tbody = document.querySelector('#conceptsTable tbody');
    tbody.innerHTML = concepts.map((c, index) => `
        <tr style="cursor: pointer;" onclick="showAuditModal(${index})">
            <td>${c.name} <small class="text-muted ms-1">(${c.count})</small></td>
            <td class="text-center"><span class="badge bg-secondary">Ver Detalle</span></td>
            <td class="text-end text-white">${formatCurrency(c.total)}</td>
        </tr>
    `).join('');

    document.getElementById('searchConcept').addEventListener('keyup', (e) => {
        const term = e.target.value.toLowerCase();
        const rows = tbody.querySelectorAll('tr');
        rows.forEach(row => {
            const text = row.querySelector('td').textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    });
}

function showAuditModal(index) {
    const concept = FINANCIAL_DATA.recurring_expenses[index];
    document.getElementById('auditTitle').textContent = `Auditoría: ${concept.name}`;
    
    const tbody = document.getElementById('auditBody');
    tbody.innerHTML = concept.details.map(d => `
        <tr>
            <td>${d.date}</td>
            <td class="text-break">${d.original_desc}</td>
            <td><span class="badge bg-dark border">${d.source}</span></td>
            <td class="text-end">${formatCurrency(d.amount)}</td>
        </tr>
    `).join('');
    
    new bootstrap.Modal(document.getElementById('auditModal')).show();
}

function renderMonthlyTable(history) {
    const tbody = document.getElementById('monthlyTable');
    tbody.innerHTML = history.slice().reverse().map(h => `
        <tr>
            <td class="text-center">${h.month}</td>
            <td>${formatCurrency(h.arca)}</td>
            <td class="text-success">${formatCurrency(h.income)}</td>
            <td class="text-danger">${formatCurrency(h.expenses)}</td>
            <td class="${h.result >= 0 ? 'text-success' : 'text-danger'} fw-bold">${formatCurrency(h.result)}</td>
        </tr>
    `).join('');
}