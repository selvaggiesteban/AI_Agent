import os
import re
from src.search_engine import SearchEngine
from src.scraper import Scraper
from src.analyzer import Analyzer
from src.html_generator import HTMLArticleGenerator
from src.pdf_generator import ReportGenerator # Use this to save PDF version
from src.local_search import LocalSearch

# Configuration
LOCAL_DATA_PATH = os.path.join("smart-research-assistant", "data")

def main():
    print("========================================")
    print("   Smart Research Assistant (SEO Mode)  ")
    print("========================================")
    
    query = input("Enter target keyword: ").strip()
    if not query:
        return

    # 1. Gather Data
    web_engine = SearchEngine(max_results=10)
    results = web_engine.search(query)
    
    scraper = Scraper()
    full_corpus = ""
    
    print("[*] Building content corpus...")
    for res in results[:5]:
        data = scraper.fetch_content(res['href'])
        if data:
            full_corpus += data['text'] + " "

    # 2. Initialize Generators
    html_gen = HTMLArticleGenerator(main_keyword=query)
    analyzer = Analyzer(language="spanish")
    
    # 3. Structure Implementation (Strict)
    
    # H1
    html_gen.add_h1(f"Guía Completa: {query.title()} (Actualización 2026)")
    
    # Intro (2 paragraphs)
    intro_p1 = analyzer.get_narrative_block(full_corpus[:len(full_corpus)//4], 10)
    intro_p2 = analyzer.get_narrative_block(full_corpus[len(full_corpus)//4:], 10)
    html_gen.add_intro([intro_p1, intro_p2])
    
    # Core Content (4 Sections)
    subtopics = ["Beneficios Clave", "Análisis Técnico", "Revisión Comparativa", "Perspectiva Futura"]
    
    # Chunk corpus roughly
    chunk_size = len(full_corpus) // 5
    for i, topic in enumerate(subtopics):
        chunk = full_corpus[i*chunk_size : (i+1)*chunk_size]
        content = analyzer.get_narrative_block(chunk, 15)
        # Pricing check for section 3 (index 2)
        is_pricing = (i == 2)
        html_gen.add_core_section(f"{i+1}. {topic}", content, is_pricing)

    # FAQ
    faqs = {
        f"¿Qué es {query}?": analyzer.get_narrative_block(full_corpus, 5),
        f"How does {query} work?": analyzer.get_narrative_block(full_corpus, 5),
        f"Is {query} safe?": analyzer.get_narrative_block(full_corpus, 5),
        f"Cost of {query}?": analyzer.get_narrative_block(full_corpus, 5),
        f"Best alternative to {query}?": analyzer.get_narrative_block(full_corpus, 5)
    }
    html_gen.add_faq(faqs)
    
    # Conclusion
    html_gen.add_conclusion(f"Final thoughts on {query} and why it matters.")
    
    # CTA & Meta
    html_gen.add_cta("https://example.com/contact", "My Agency GBP")
    html_gen.add_metadata(query.lower().replace(" ", "-"), f"Best {query} Guide", f"Learn everything about {query}.")

    # Save outputs
    base_name = f"SEO_Article_{query.replace(' ', '_')}"
    
    # Save HTML (Primary Deliverable per spec)
    html_filename = os.path.join("smart-research-assistant", "reports", base_name + ".html")
    html_gen.save_html(html_filename)
    
    # Save PDF (Visual Representation)
    pdf_filename = os.path.join("smart-research-assistant", "reports", base_name + ".pdf")
    
    # Simple PDF render of the HTML text content
    pdf = ReportGenerator(query, pdf_filename)
    pdf.create_cover_page()
    pdf.add_chapter_title("HTML Source Content Render")
    # We just dump the raw text structure for PDF compliance
    pdf.add_narrative_section("Full Article Body", "Generated HTML", html_gen.get_full_html())
    pdf.save()

    print("\n[ok] SEO Content Generated (HTML + PDF)")

if __name__ == "__main__":
    main()
