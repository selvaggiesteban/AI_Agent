import html

class HTMLArticleGenerator:
    def __init__(self, main_keyword):
        self.keyword = main_keyword
        self.content_parts = []
        
    def _inject_keyword(self, text):
        # Naive injection: bold the keyword if present, or force inject if not (simple version)
        # The spec says: Main Keyword in <strong> tags in EVERY paragraph.
        lower_text = text.lower()
        lower_kw = self.keyword.lower()
        
        if lower_kw in lower_text:
            # Case insensitive replace maintaining original case is hard with simple replace.
            # We will assume we can replace the first occurrence found
            start = lower_text.find(lower_kw)
            if start != -1:
                original_kw = text[start:start+len(lower_kw)]
                return text[:start] + f"<strong>{original_kw}</strong>" + text[start+len(lower_kw):]
        
        # If not present, append it naturally (simulated)
        return text + f" This is why <strong>{self.keyword}</strong> is crucial."

    def add_h1(self, title):
        self.content_parts.append(f"<h1>{html.escape(title)}</h1>")

    def add_intro(self, paragraphs):
        # Paragraphs must be 100-200 words
        for p in paragraphs:
            processed = self._inject_keyword(p)
            self.content_parts.append(f"<p>{processed}</p>")

    def add_core_section(self, h2_title, content, is_pricing=False, pricing_data=None):
        self.content_parts.append(f"<h2>{html.escape(h2_title)}</h2>")
        processed = self._inject_keyword(content)
        self.content_parts.append(f"<p>{processed}</p>")
        
        if is_pricing and pricing_data:
            table = "<table><thead><tr><th>Item</th><th>Price</th></tr></thead><tbody>"
            for k, v in pricing_data.items():
                table += f"<tr><td>{k}</td><td>{v}</td></tr>"
            table += "</tbody></table>"
            self.content_parts.append(table)

    def add_faq(self, faqs):
        self.content_parts.append("<h2>Preguntas Frecuentes</h2>")
        for q, a in faqs.items():
            self.content_parts.append(f"<h3>{html.escape(q)}</h3>")
            processed = self._inject_keyword(a)
            self.content_parts.append(f"<p>{processed}</p>")

    def add_conclusion(self, text):
        self.content_parts.append("<h2>Conclusión</h2>")
        processed = self._inject_keyword(text)
        self.content_parts.append(f"<p>{processed}</p>")

    def add_cta(self, contact_url, gbp_name):
        section = f"""
        <section>
            <p>¿Listo para avanzar? <a href="{contact_url}" rel="nofollow" target="_blank">Solicitar Presupuesto</a></p>
            <p>Visitá nuestro perfil en <a href="#" rel="nofollow" target="_blank">{gbp_name}</a></p>
        </section>
        """
        self.content_parts.append(section)

    def add_metadata(self, slug, title, description):
        meta = f"""
        <!--
        Slug: {slug}
        Meta Title: {title}
        Meta Description: {description}
        -->
        """
        self.content_parts.append(meta)

    def get_full_html(self):
        return "\n".join(self.content_parts)

    def save_html(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.get_full_html())
        print(f"[*] HTML Article saved: {filename}")
