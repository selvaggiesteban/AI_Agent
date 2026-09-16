#!/usr/bin/env python3
"""
HTML Report Generator - Genera reportes HTML interactivos para SEO
Convierte resultados JSON en reportes visuales
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import argparse


class HTMLReportGenerator:
    def __init__(self, input_file: str, output_dir: str):
        """
        Inicializa el generador de reportes
        
        Args:
            input_file: Archivo JSON con resultados de seo_verifier.py
            output_dir: Directorio de salida para reportes HTML
        """
        self.input_file = input_file
        self.output_dir = output_dir
        
        with open(input_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        os.makedirs(output_dir, exist_ok=True)
    
    def get_status_emoji(self, passed: bool) -> str:
        """Retorna emoji según estado"""
        return '✅' if passed else '❌'
    
    def get_status_class(self, passed: bool) -> str:
        """Retorna clase CSS según estado"""
        return 'pass' if passed else 'fail'
    
    def generate_summary_html(self) -> str:
        """Genera HTML de resumen"""
        results = self.data.get('results', [])
        total_pages = len(results)
        
        if total_pages == 0:
            return '<p>No hay resultados</p>'
        
        # Calcular estadísticas
        avg_score = sum(r['score'] for r in results) / total_pages
        total_checks = sum(r['total_checks'] for r in results)
        total_passed = sum(r['passed'] for r in results)
        total_failed = sum(r['failed'] for r in results)
        
        # Estadísticas por check
        check_stats = {}
        for r in results:
            for c in r.get('checks', []):
                name = c['name']
                if name not in check_stats:
                    check_stats[name] = {'pass': 0, 'fail': 0, 'total': 0}
                check_stats[name]['total'] += 1
                if c['pass']:
                    check_stats[name]['pass'] += 1
                else:
                    check_stats[name]['fail'] += 1
        
        html = f"""
        <div class="summary">
            <h2>Resumen General</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{total_pages}</div>
                    <div class="stat-label">Páginas Analizadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{avg_score:.1f}%</div>
                    <div class="stat-label">Score Promedio</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_passed}</div>
                    <div class="stat-label">Verificaciones Pasadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_failed}</div>
                    <div class="stat-label">Verificaciones Fallidas</div>
                </div>
            </div>
            
            <h3>Detalle por Verificación</h3>
            <table class="check-stats">
                <thead>
                    <tr>
                        <th>Verificación</th>
                        <th>Estado</th>
                        <th>Pasadas</th>
                        <th>Fallidas</th>
                        <th>% Éxito</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for name, stats in sorted(check_stats.items()):
            pct = (stats['pass'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status_class = 'pass' if pct == 100 else ('warning' if pct >= 50 else 'fail')
            status_emoji = '✅' if pct == 100 else ('⚠️' if pct >= 50 else '❌')
            
            html += f"""
                    <tr class="{status_class}">
                        <td>{name.replace('_', ' ').title()}</td>
                        <td>{status_emoji}</td>
                        <td>{stats['pass']}</td>
                        <td>{stats['fail']}</td>
                        <td>{pct:.1f}%</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    def generate_pages_html(self) -> str:
        """Genera HTML de detalle por página"""
        results = self.data.get('results', [])
        
        html = """
        <div class="pages-detail">
            <h2>Detalle por Página</h2>
            <div class="page-cards">
        """
        
        for r in results:
            url = r['url']
            score = r['score']
            passed = r['passed']
            total = r['total_checks']
            
            # Clase según score
            if score >= 80:
                card_class = 'good'
            elif score >= 50:
                card_class = 'warning'
            else:
                card_class = 'bad'
            
            html += f"""
            <div class="page-card {card_class}">
                <div class="page-header">
                    <h3 class="page-url">{url}</h3>
                    <span class="page-score">{score}%</span>
                </div>
                <div class="page-stats">
                    <span class="stat-pass">{passed} pasadas</span>
                    <span class="stat-fail">{r['failed']} fallidas</span>
                </div>
                <div class="checks-list">
            """
            
            for c in r.get('checks', []):
                status_class = 'pass' if c['pass'] else 'fail'
                status_emoji = self.get_status_emoji(c['pass'])
                
                html += f"""
                <div class="check-item {status_class}">
                    <span class="check-icon">{status_emoji}</span>
                    <span class="check-name">{c['name'].replace('_', ' ').title()}</span>
                    <span class="check-message">{c['message']}</span>
                </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def generate_full_report(self) -> str:
        """Genera reporte HTML completo"""
        base_url = self.data.get('base_url', 'N/A')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte SEO - {base_url}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        header p {{
            opacity: 0.9;
        }}
        
        .summary {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        
        tr.pass {{
            background: #d4edda;
        }}
        
        tr.fail {{
            background: #f8d7da;
        }}
        
        tr.warning {{
            background: #fff3cd;
        }}
        
        .pages-detail {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .page-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .page-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .page-card.good {{
            border-left: 4px solid #28a745;
        }}
        
        .page-card.warning {{
            border-left: 4px solid #ffc107;
        }}
        
        .page-card.bad {{
            border-left: 4px solid #dc3545;
        }}
        
        .page-header {{
            background: #f8f9fa;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .page-url {{
            font-size: 14px;
            word-break: break-all;
            flex: 1;
            margin-right: 10px;
        }}
        
        .page-score {{
            font-size: 20px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .page-stats {{
            padding: 10px 15px;
            background: #fff;
            border-bottom: 1px solid #eee;
            font-size: 13px;
        }}
        
        .stat-pass {{
            color: #28a745;
            margin-right: 15px;
        }}
        
        .stat-fail {{
            color: #dc3545;
        }}
        
        .checks-list {{
            padding: 10px 15px;
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .check-item {{
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
            font-size: 13px;
        }}
        
        .check-item:last-child {{
            border-bottom: none;
        }}
        
        .check-icon {{
            width: 24px;
            text-align: center;
        }}
        
        .check-name {{
            font-weight: 500;
            width: 180px;
            flex-shrink: 0;
        }}
        
        .check-message {{
            color: #666;
            flex: 1;
        }}
        
        .check-item.pass .check-message {{
            color: #28a745;
        }}
        
        .check-item.fail .check-message {{
            color: #dc3545;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 13px;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .page-cards {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Reporte de Verificación SEO</h1>
            <p>Sitio: {base_url}</p>
            <p>Generado: {timestamp}</p>
        </header>
        
        {self.generate_summary_html()}
        
        {self.generate_pages_html()}
        
        <footer>
            <p>Reporte generado automáticamente por SEO Verifier</p>
            <p>{timestamp}</p>
        </footer>
    </div>
</body>
</html>
"""
        
        return html
    
    def generate_comparison_html(self, other_reports: List[str]) -> str:
        """Genera reporte comparativo de múltiples sitios"""
        # Cargar otros reportes
        all_data = [self.data]
        for report_file in other_reports:
            with open(report_file, 'r', encoding='utf-8') as f:
                all_data.append(json.load(f))
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Comparativo SEO</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        h1 {{ font-size: 28px; }}
        h2 {{ margin: 20px 0; }}
        
        .comparison-table {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        
        .good {{ background: #d4edda; }}
        .warning {{ background: #fff3cd; }}
        .bad {{ background: #f8d7da; }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 13px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Reporte Comparativo SEO</h1>
            <p>Sitios analizados: {len(all_data)}</p>
            <p>Generado: {timestamp}</p>
        </header>
        
        <div class="comparison-table">
            <h2>Comparación de Scores</h2>
            <table>
                <thead>
                    <tr>
                        <th>Sitio</th>
                        <th>Páginas</th>
                        <th>Score Promedio</th>
                        <th>Checks Pasadas</th>
                        <th>Checks Fallidas</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for data in all_data:
            base_url = data.get('base_url', 'N/A')
            results = data.get('results', [])
            total_pages = len(results)
            
            if total_pages > 0:
                avg_score = sum(r['score'] for r in results) / total_pages
                total_passed = sum(r['passed'] for r in results)
                total_failed = sum(r['failed'] for r in results)
            else:
                avg_score = 0
                total_passed = 0
                total_failed = 0
            
            score_class = 'good' if avg_score >= 80 else ('warning' if avg_score >= 50 else 'bad')
            
            html += f"""
                    <tr>
                        <td><strong>{base_url}</strong></td>
                        <td>{total_pages}</td>
                        <td class="{score_class}">{avg_score:.1f}%</td>
                        <td>{total_passed}</td>
                        <td>{total_failed}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Reporte comparativo generado automáticamente por SEO Verifier</p>
        </footer>
    </div>
</body>
</html>
"""
        
        return html
    
    def save_report(self, filename: str = 'reporte_seo.html'):
        """Guarda el reporte HTML"""
        html = self.generate_full_report()
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Reporte guardado en: {filepath}")
        return filepath


def main():
    parser = argparse.ArgumentParser(
        description='HTML Report Generator - Genera reportes HTML interactivos'
    )
    parser.add_argument('input', help='Archivo JSON con resultados de seo_verifier.py')
    parser.add_argument('-o', '--output-dir', default='reportes',
                        help='Directorio de salida (default: reportes)')
    parser.add_argument('-n', '--name', default='reporte_seo.html',
                        help='Nombre del archivo de salida (default: reporte_seo.html)')
    parser.add_argument('--compare', nargs='*',
                        help='Archivos JSON adicionales para comparar')
    
    args = parser.parse_args()
    
    generator = HTMLReportGenerator(args.input, args.output_dir)
    
    if args.compare:
        # Generar reporte comparativo
        html = generator.generate_comparison_html(args.compare)
        filepath = os.path.join(args.output_dir, 'comparativo.html')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Reporte comparativo guardado en: {filepath}")
    else:
        # Generar reporte individual
        generator.save_report(args.name)


if __name__ == '__main__':
    main()
