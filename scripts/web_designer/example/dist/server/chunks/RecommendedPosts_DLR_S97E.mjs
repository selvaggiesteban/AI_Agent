globalThis.process ??= {};
globalThis.process.env ??= {};
import { c as createComponent } from "./astro-component_D8bTRbmq.mjs";
import { v as maybeRenderHead, a0 as addAttribute, K as renderTemplate } from "./sequence_BvoC4k2m.mjs";
import { r as renderScript, g as getLocaleFromUrl, t } from "./global_tQVAIOUq.mjs";
import { r as renderComponent } from "./worker-entry_tgSJjYop.mjs";
import { $ as $$Section } from "./Section_X3fkqAep.mjs";
import { g as getCollection } from "./_astro_content_DL4dQ2_T.mjs";
const $$ProjectCarousel = createComponent(($$result, $$props, $$slots) => {
  const carouselItems = [
    { href: "https://centraldeturbos.com/", src: "/assets/carousel/centraldeturbos.webp" },
    { href: "https://alquiriasolutions.com/", src: "/assets/carousel/alquiriasolutions.webp" },
    { href: "https://acuatika25.com.ar/", src: "/assets/carousel/acuatika.webp" },
    { href: "https://ntkic.com/", src: "/assets/carousel/ntkic.webp" },
    { href: "https://depaoli.com.ar/", src: "/assets/carousel/depaoli.webp" },
    { href: "https://consulting-21.com/", src: "/assets/carousel/consulting-21.webp" },
    { href: "https://saute.es/", src: "/assets/carousel/saute.webp" },
    { href: "https://matiasgarcetesuarez.com.ar/", src: "/assets/carousel/matiasgarcetesuarez.webp" },
    { href: "https://talaiotaudio.com/", src: "/assets/carousel/talaiotaudio.webp" },
    { href: "https://alphatelservices.com/", src: "/assets/carousel/alphatelservices.webp" },
    { href: "https://draandreamamani.com/", src: "/assets/carousel/draandreamamani.webp" },
    { href: "https://cvela2017.com/", src: "/assets/carousel/cvela2017.webp" },
    { href: "https://piscinasluciano.com.ar/", src: "/assets/carousel/piscinasluciano.webp" },
    { href: "https://petruscigars.com/", src: "/assets/carousel/petruscigars.webp" },
    { href: "https://yourdream.ae/", src: "/assets/carousel/yourdream.webp" },
    { href: "https://watervan.com.ar/", src: "/assets/carousel/watervan.webp" },
    { href: "https://pescaolidvalladolid.com/", src: "/assets/carousel/pescaolidvalladolid.webp" },
    { href: "https://rocadeguiapsicologia.es/", src: "/assets/carousel/rocadeguiapsicologia.webp" },
    { href: "https://semikongarden.com.ar/", src: "/assets/carousel/semikongarden.webp" },
    { href: "https://semikon.com.ar/", src: "/assets/carousel/semikon.webp" },
    { href: "https://seararefrigeracion.com.ar/", src: "/assets/carousel/seararefrigeracion.webp" }
  ];
  const extendedItems = [...carouselItems, ...carouselItems, ...carouselItems];
  return renderTemplate`${maybeRenderHead()}<div class="relative overflow-hidden w-full py-xl group" data-astro-cid-n2fcsbob> <div id="project-track" class="flex gap-lg overflow-x-auto scrollbar-hide px-lg md:px-xxl cursor-grab active:cursor-grabbing select-none" data-astro-cid-n2fcsbob> ${extendedItems.map((item) => renderTemplate`<a${addAttribute(item.href, "href")} target="_blank" rel="noopener noreferrer" class="flex-shrink-0 w-[350px] aspect-video overflow-hidden transition-all duration-500 hover:scale-[1.02]" data-astro-cid-n2fcsbob> <img${addAttribute(item.src, "src")} alt="Proyecto de diseño web" class="w-full h-full object-contain opacity-70 hover:opacity-100 transition-opacity duration-500 pointer-events-none" loading="lazy" data-astro-cid-n2fcsbob> </a>`)} </div> </div>  ${renderScript($$result, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/ProjectCarousel.astro?astro&type=script&index=0&lang.ts")}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/ProjectCarousel.astro", void 0);
const $$SkillsSection = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$SkillsSection;
  const locale = getLocaleFromUrl(Astro2.url);
  const lang = locale;
  const skillCategories = [
    {
      titleKey: "skills.categories.frontend",
      skills: [
        { name: "React", icon: "/assets/skills/react.svg" },
        { name: "Vue.js", icon: "/assets/skills/vue.svg" },
        { name: "Next.js", icon: "/assets/skills/nextjs.svg" },
        { name: "TypeScript", icon: "/assets/skills/typescript.svg" },
        { name: "JavaScript", icon: "/assets/skills/js.svg" },
        { name: "HTML5", icon: "/assets/skills/html5.svg" },
        { name: "CSS3", icon: "/assets/skills/css3.svg" },
        { name: "Sass", icon: "/assets/skills/sass.svg" },
        { name: "Vite", icon: "/assets/skills/vite.webp" },
        { name: "Bootstrap", icon: "/assets/skills/bootstrap.webp" },
        { name: "Astro", icon: "/assets/skills/astro.svg" },
        { name: "Tailwind CSS", icon: "https://upload.wikimedia.org/wikipedia/commons/d/d5/Tailwind_CSS_Logo.svg" }
      ]
    },
    {
      titleKey: "skills.categories.backend",
      skills: [
        { name: "PHP", icon: "/assets/skills/php.svg" },
        { name: "Laravel", icon: "/assets/skills/laravel.svg" },
        { name: "CodeIgniter", icon: "/assets/skills/codeigniter.svg" },
        { name: "Composer", icon: "/assets/skills/composer.png" },
        { name: "Python", icon: "/assets/skills/python.svg" },
        { name: "Firebase", icon: "/assets/skills/firebase.svg" }
      ]
    },
    {
      titleKey: "skills.categories.apis",
      skills: [
        { name: "REST API", icon: "/assets/skills/fastapi.svg" },
        { name: "GraphQL", icon: "/assets/skills/graphql.svg" },
        { name: "Stripe", icon: "/assets/skills/stripe.svg" },
        { name: "Mercado Pago", icon: "/assets/skills/mercadopago.webp" },
        { name: "WhatsApp API", icon: "/assets/skills/whatsapp.webp" },
        { name: "Resend", icon: "/assets/skills/resend.svg" }
      ]
    },
    {
      titleKey: "skills.categories.databases",
      skills: [
        { name: "MySQL", icon: "/assets/skills/mysql.svg" },
        { name: "SQLite", icon: "/assets/skills/sqlite.webp" },
        { name: "PostgreSQL", icon: "/assets/skills/postgresql.svg" },
        { name: "MongoDB", icon: "/assets/skills/mongodb.svg" }
      ]
    },
    {
      titleKey: "skills.categories.infra",
      skills: [
        { name: "AWS", icon: "/assets/skills/aws.png" },
        { name: "Azure", icon: "/assets/skills/azure.svg" },
        { name: "Google Cloud", icon: "/assets/skills/googlecloud.svg" },
        { name: "Cloudflare", icon: "/assets/skills/cloudflare.svg" },
        { name: "Docker", icon: "/assets/skills/docker.svg" },
        { name: "GitHub", icon: "/assets/skills/github.png" },
        { name: "GitHub Actions", icon: "/assets/skills/githubactions.svg" },
        { name: "Nginx", icon: "/assets/skills/nginx.svg" },
        { name: "Plesk", icon: "/assets/skills/plesk.svg" },
        { name: "VPS Linux", icon: "/assets/skills/linux.svg" },
        { name: "Node.js", icon: "/assets/skills/node.webp" }
      ]
    },
    {
      titleKey: "skills.categories.ai",
      skills: [
        { name: "OpenAI", icon: "/assets/skills/openai.svg" },
        { name: "Gemini", icon: "/assets/skills/gemini.png" },
        { name: "Claude", icon: "/assets/skills/claude.webp" },
        { name: "Ollama", icon: "/assets/skills/ollama.webp" },
        { name: "n8n", icon: "/assets/skills/n8n.svg" }
      ]
    },
    {
      titleKey: "skills.categories.productivity",
      skills: [
        { name: "VS Code", icon: "/assets/skills/vscode.webp" },
        { name: "Trello", icon: "/assets/skills/trello.webp" },
        { name: "Monday", icon: "/assets/skills/monday.svg" },
        { name: "ClickUp", icon: "/assets/skills/clickup.webp" }
      ]
    },
    {
      titleKey: "skills.categories.cms",
      skills: [
        { name: "WordPress", icon: "/assets/skills/wordpress.webp" },
        { name: "Elementor", icon: "/assets/skills/elementor.webp" },
        { name: "WooCommerce", icon: "/assets/skills/woocommerce.svg" },
        { name: "PrestaShop", icon: "/assets/skills/prestashop.webp" },
        { name: "Tienda Nube", icon: "/assets/skills/tiendanube.jpeg" },
        { name: "Shopify", icon: "/assets/skills/shopify.svg" }
      ]
    },
    {
      titleKey: "skills.categories.seo",
      skills: [
        { name: "Google Analytics", icon: "/assets/skills/analytics.svg" },
        { name: "Search Console", icon: "/assets/skills/searchconsole.svg" },
        { name: "Tag Manager", icon: "/assets/skills/tagmanager.svg" },
        { name: "PageSpeed", icon: "/assets/skills/pagespeed.svg" },
        { name: "Looker Studio", icon: "https://cdn.worldvectorlogo.com/logos/looker-1.svg" }
      ]
    }
  ];
  return renderTemplate`${renderComponent($$result, "Section", $$Section, { "variant": "white", "id": "skills" }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="text-center mb-16"> <h2 class="display-lg mb-4">${t(lang, "skills.heading")}</h2> <p class="text-xl text-ink/60">${t(lang, "skills.subtitle")}</p> </div> <div class="grid grid-cols-1 md:grid-cols-3 gap-lg md:gap-xl"> ${skillCategories.map((category) => renderTemplate`<div class="bg-[#ffffff] p-lg rounded-[5px] border border-hairline flex flex-col h-full"> <h3 class="font-mono text-xs uppercase tracking-widest text-ink/40 mb-lg border-b border-hairline pb-4 text-center">${t(lang, category.titleKey)}</h3> <div class="flex flex-wrap gap-md items-center justify-start py-4"> ${category.skills.map((skill) => renderTemplate`<div class="flex flex-col items-center gap-xs group w-[calc(33.333%-1rem)] min-w-[70px]"> <div class="w-[57px] h-[57px] flex items-center justify-center bg-canvas rounded-[5px] border border-hairline transition-colors p-[4.5px]"> <img${addAttribute(skill.icon, "src")}${addAttribute(skill.name, "alt")} class="w-[48px] h-[48px] object-contain filter grayscale group-hover:grayscale-0 transition-all"> </div> <span class="text-[10px] font-medium text-ink/60 text-center line-clamp-1">${skill.name}</span> </div>`)} </div> </div>`)} </div> ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/SkillsSection.astro", void 0);
const $$ReviewsCarousel = createComponent(($$result, $$props, $$slots) => {
  const reviews = [
    {
      name: "Gian Serrudo",
      rating: 5,
      color: "bg-block-lime",
      text: "Super profesional! Y super atento. Su conocimiento y experiencia con páginas web lo hace alguien super recomendable. Me ayudo a diseñar páginas web para mi negocio y configurarlas desde 0. Si necesitan a alguien para esto llamen a Esteban."
    },
    {
      name: "Aurelia Mood",
      rating: 5,
      color: "bg-block-lilac",
      text: "Tuve la oportunidad de trabajar con Esteban para el diseño y optimización de mi tienda online, y no podría estar más satisfecha con el resultado. Desde el primer momento, la atención fue excepcional. Se tomó el tiempo necesario para entender mis necesidades y objetivos, demostrando una paciencia y dedicación admirables. Los resultados fueron magníficos, gracias!"
    },
    {
      name: "Gabriel Cantero Martínez",
      rating: 5,
      color: "bg-block-mint",
      text: "Contacté a Esteban porque no sabía muy bien cómo desarrollar mi web, y en todo momento demostró ser súper paciente y profesional. Debo de agradecerle lo bien que me ha orientado y explicado cada paso que ha ido dando en el proyecto. Recomendable 100%"
    },
    {
      name: "Carol Venice",
      rating: 5,
      color: "bg-block-cream",
      text: "Contar con Esteban en NICE Diseño y Comunicación, nos permite asegurar que los desarrollos web de nuestros clientes lograrán su máximo cometido a través de un proceso de trabajo súper transparente, respetuoso y profesional. Además Esteban siempre está un paso adelante de las nuevas tecnologías y aplicaciones, dándonos la posibilidad de mejorar en forma contínua nuestros servicios."
    },
    {
      name: "Arlet Lizana",
      rating: 5,
      color: "bg-block-pink",
      text: "Contacté a Esteban ya que necesitaba mejorar y terminar el diseño web de mi tienda que otra persona dejó a medias, Esteban lo solucionó y todo perfecto. Rapidez, responsabilidad y confianza."
    },
    {
      name: "Mario Falcón Suárez",
      rating: 5,
      color: "bg-block-coral",
      text: "Esteban es un profesional de 10! Desarrolló mi web en 5 días con todas las funcionalidades y muchas mejoras más que no teníamos previstas que nos ofreció y son geniales. Muy recomendables sus servicios 💯"
    },
    {
      name: "Yanira Rodríguez Santana",
      rating: 5,
      color: "bg-block-lime",
      text: "Esteban es un profesional de 10! Estaba estancada con mi página web y en tres días me presentó una solución súper práctica y rápida. Sin duda va a ir de la mano en todo el proyecto. Gracias!"
    },
    {
      name: "Matias Dominguez",
      rating: 5,
      color: "bg-block-lilac",
      text: "Un genio Esteban. Me hizo mi primer página, me aumentaron las ventas y la confianza del cliente. Accedió siempre bien a mis cambios y solicitudes y respondió rápido a los problemas que se presentaron"
    },
    {
      name: "Javi",
      rating: 5,
      color: "bg-block-mint",
      text: "Contactó con mi agencia de marketing a través de email ofreciendo sus servicios como programador web. Decidí darle una oportunidad y poder valorar su trabajo. La verdad que no puedo estar más satisfecho, tanto con el trabajo realizado como con su implicación. Recomiendo trabajar con el."
    },
    {
      name: "Milena Gimenez",
      rating: 5,
      color: "bg-block-cream",
      text: "El desarrollo de mi tienda web fue impecable. Muy buena atención se nota que es un experto en el tema. Siempre dispuesto a ayudar y resolver problemas. Gracias!!"
    },
    {
      name: "Alfredo Godoy",
      rating: 5,
      color: "bg-block-pink",
      text: "Excelente trabajo con proyecto de mi tienda online. A tiempo, responsable y muy cordial. Recomiendo totalmente. Muchas gracias"
    },
    {
      name: "Juani Márquez",
      rating: 5,
      color: "bg-block-coral",
      text: "Un servicio impecable, respondio todas mis dudas y me ayudo a crecer en mi emprendimiento :)"
    },
    {
      name: "Roger Caruci",
      rating: 5,
      color: "bg-block-lime",
      text: "Esteban se encargó de optimizar un sitio web para mejorar el posicionamiento SEO con resultados notables en las búsquedas de Google y demostrando su experiencia con excelente atención y profesionalismo"
    },
    {
      name: "Usberto Ayma Ayma",
      rating: 5,
      color: "bg-block-lilac",
      text: "Excelente diseñador web. Me ayudo en varios proyectos. Siempre con buena predisposición y soluciones web robustas."
    },
    {
      name: "Martin",
      rating: 5,
      color: "bg-block-mint",
      text: "Excelente servicio, pudo potenciar mi negocio y llevarlo a otro nivel, totalmente satisfecho!!"
    },
    {
      name: "Valeria Risatti",
      rating: 5,
      color: "bg-block-cream",
      text: "Excelente Profesional! Hemos trabajado juntos el desarrollo y mantenimiento de varios e-commerce y websites."
    },
    {
      name: "Fernando Ybarra",
      rating: 5,
      color: "bg-block-pink",
      text: "Buscaba un diseñador WordPress para terminar un proyecto y di en la tecla. Felicitaciones, excelente trabajo."
    },
    {
      name: "Francisco Lee",
      rating: 5,
      color: "bg-block-coral",
      text: "Contraté a Esteban para el desarrollo de un sitio e-commerce y todo perfecto 💯"
    },
    {
      name: "Ciro Alejandro Querol",
      rating: 5,
      color: "bg-block-lime",
      text: "Excelente Profesional! Muy buen trabajo con calidad. Lo recomiendo."
    },
    {
      name: "Nadia Quetglas",
      rating: 5,
      color: "bg-block-lilac",
      text: "Supo resolver bien varios proyectos web. Seguiremos trabajando juntos 😀"
    },
    {
      name: "Alexander Caruci",
      rating: 5,
      color: "bg-block-mint",
      text: "Todo perfecto en su servicio, cumplió con todo lo deseado, muy contento con su servicio"
    },
    {
      name: "TRANKA PALANKA DOS",
      rating: 5,
      color: "bg-block-cream",
      text: "Esteban un genio. Destaco su compromiso y responsabilidad. Gracias 👌"
    },
    {
      name: "Alejandra Venturelli",
      rating: 5,
      color: "bg-block-pink",
      text: "Excelente profesional!!! Muy recomendable!!!"
    },
    {
      name: "Bruno",
      rating: 5,
      color: "bg-block-coral",
      text: "Excelente trabajo, muy recomendable!!!"
    },
    {
      name: "Pablo",
      rating: 5,
      color: "bg-block-lime",
      text: "Excelente trabajo Lo Recomiendo"
    },
    {
      name: "Abimael Baez",
      rating: 5,
      color: "bg-block-lilac",
      text: "Muy eficiente y siempre tiene una solución"
    },
    {
      name: "Yamila Diego",
      rating: 5,
      color: "bg-block-mint",
      text: "Excelente atención"
    },
    {
      name: "Joaquín Seara",
      rating: 5,
      color: "bg-block-cream",
      text: "Buen servicio de atención, cumplió mis expectativas."
    },
    {
      name: "Joaquin Villarreal",
      rating: 5,
      color: "bg-block-pink",
      text: "Servicio impecable y resultados profesionales."
    }
  ];
  const extendedReviews = [...reviews, ...reviews, ...reviews];
  return renderTemplate`${renderComponent($$result, "Section", $$Section, { "variant": "white", "id": "reviews", "class": "overflow-hidden py-20 relative !py-12", "fullWidth": true, "data-astro-cid-rmfhop62": true }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="px-lg md:px-xxl mb-12 reveal" data-astro-cid-rmfhop62> <h2 class="display-lg mb-4 text-center" data-astro-cid-rmfhop62>Reseñas de clientes</h2> <p class="text-xl text-ink/60 mb-8 text-center max-w-2xl mx-auto" data-astro-cid-rmfhop62>Lo que dicen quienes ya confían en mi ingeniería de excelencia.</p> </div> <div class="relative group" data-astro-cid-rmfhop62> <!-- Botones de Navegación --> <button id="prev-review" class="absolute left-8 top-1/2 -translate-y-1/2 z-30 bg-white/90 border border-hairline p-4 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white active:scale-95" aria-label="Anterior" data-astro-cid-rmfhop62> <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-astro-cid-rmfhop62><path d="m15 18-6-6 6-6" data-astro-cid-rmfhop62></path></svg> </button> <button id="next-review" class="absolute right-8 top-1/2 -translate-y-1/2 z-30 bg-white/90 border border-hairline p-4 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white active:scale-95" aria-label="Siguiente" data-astro-cid-rmfhop62> <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-astro-cid-rmfhop62><path d="m9 18 6-6-6-6" data-astro-cid-rmfhop62></path></svg> </button> <div id="review-track" class="flex gap-4 overflow-x-auto snap-x snap-mandatory scrollbar-hide py-4 px-lg md:px-xxl cursor-grab active:cursor-grabbing select-none" style="scroll-behavior: smooth;" data-astro-cid-rmfhop62> ${extendedReviews.map((review) => {
    const isLong = review.text.length > 130;
    const displayText = isLong ? review.text.substring(0, 130) + "..." : review.text + '"';
    return renderTemplate`<div class="w-[280px] lg:w-[calc(20%-1rem)] h-[300px] flex-shrink-0 bg-white p-5 rounded-3xl border border-gray-100 shadow-[0_10px_40px_-15px_rgba(0,0,0,0.05)] snap-center transition-transform duration-300 relative flex flex-col" data-astro-cid-rmfhop62> <img src="/assets/skills/google-icon.svg" alt="Google Review" class="absolute top-5 right-5 w-4 h-4 opacity-80" data-astro-cid-rmfhop62> <div class="flex items-center gap-3 mb-4" data-astro-cid-rmfhop62> <div${addAttribute(["w-10 h-10 rounded-full overflow-hidden flex items-center justify-center font-bold text-base shadow-sm border border-gray-100", review.color], "class:list")} data-astro-cid-rmfhop62> <img${addAttribute(`/assets/reviews/${review.name.toLowerCase().replace(/\s+/g, "-")}.webp`, "src")}${addAttribute(review.name, "alt")} class="w-full h-full object-cover" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" data-astro-cid-rmfhop62> <span class="hidden items-center justify-center w-full h-full text-white/90" data-astro-cid-rmfhop62> ${review.name.charAt(0)} </span> </div> <div data-astro-cid-rmfhop62> <span class="font-bold text-gray-900 block leading-tight text-sm" data-astro-cid-rmfhop62>${review.name}</span> <div class="flex gap-0.5 mt-1" data-astro-cid-rmfhop62> ${[...Array(review.rating)].map((_, i) => renderTemplate`<svg xmlns="http://www.w3.org/2000/svg" width="10" height="12" viewBox="0 0 24 24" fill="#fbbf24" stroke="#fbbf24" class="lucide lucide-star" data-astro-cid-rmfhop62><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" data-astro-cid-rmfhop62></polygon></svg>`)} </div> </div> </div> <div class="flex-grow overflow-hidden relative" data-astro-cid-rmfhop62> <p class="text-[13px] text-gray-600 leading-relaxed" data-astro-cid-rmfhop62>
"${displayText} </p> ${isLong && renderTemplate`<a href="https://share.google/1LpGxeLM3Wan7iCuY" target="_blank" rel="noopener noreferrer" class="text-[10px] font-medium text-primary mt-2 inline-block hover:underline" data-astro-cid-rmfhop62>
Leer más en Google
</a>`} </div> </div>`;
  })} </div> </div> ` })}  ${renderScript($$result, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/ReviewsCarousel.astro?astro&type=script&index=0&lang.ts")}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/ReviewsCarousel.astro", void 0);
const $$RecentPosts = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$RecentPosts;
  const locale = getLocaleFromUrl(Astro2.url);
  const lang = locale;
  const repos = [
    {
      name: "30_days_coding",
      url: "https://github.com/selvaggiesteban/30_days_coding",
      descKey: "recent.repos.30_days_coding",
      language: "TypeScript",
      stars: 0
    },
    {
      name: "spec-driven_development",
      url: "https://github.com/selvaggiesteban/spec-driven_development",
      descKey: "recent.repos.spec-driven",
      language: "Python",
      stars: 0
    },
    {
      name: "hands-on-ai",
      url: "https://github.com/selvaggiesteban/hands-on-ai",
      descKey: "recent.repos.hands-on-ai",
      language: "Jupyter Notebook",
      stars: 0
    }
  ];
  return renderTemplate`${renderComponent($$result, "Section", $$Section, { "variant": "white", "id": "recent-posts", "class": "reveal" }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="grid lg:grid-cols-12 gap-xl items-start"> <div class="lg:col-span-4 text-center lg:text-left"> <h2 class="display-lg mb-md">${t(lang, "recent.heading")}</h2> <p class="text-xl text-ink/60 mb-6">${t(lang, "recent.description")}</p> </div> <div class="lg:col-span-8 space-y-6"> ${repos.map((repo) => renderTemplate`<a${addAttribute(repo.url, "href")} target="_blank" class="block bg-[#f9f9f9] p-lg rounded-[9px] border border-hairline hover:border-ink/20 transition-all shadow-sm"> <div class="flex items-center gap-3 mb-4"> <div class="w-10 h-10 rounded-full bg-ink flex items-center justify-center text-white"> <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.24c3-.3 6-1.5 6-6.3 0-1.4-.5-2.5-1.4-3.4.1-.3.6-1.6-.1-3.4 0 0-1.2-.4-3.9 1.8a12.3 12.3 0 0 0-7 0C3.9 2.2 2.7 2.6 2.7 2.6c-.7 1.8-.2 3.1-.1 3.4-.9.9-1.4 2-1.4 3.4 0 4.8 3 6 6 6.3-.3.3-.5.7-.5 1.5v4"></path><path d="M9 18c-4.5 1-5-2.5-7-3"></path></svg> </div> <div> <span class="font-bold text-sm block text-primary">${repo.name}</span> <span class="text-xs text-ink/40">${t(lang, "recent.githubRepo")}</span> </div> </div> <p class="text-sm text-ink/80 leading-relaxed mb-4"> ${t(lang, repo.descKey)} </p> <div class="flex items-center justify-between pt-4 border-t border-hairline-soft text-xs text-ink/60 font-medium"> <div class="flex items-center gap-4"> <span class="flex items-center gap-1"> <span class="w-3 h-3 rounded-full bg-primary/20 border border-primary/50"></span> ${repo.language} </span> <span class="flex items-center gap-1"> <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg> ${repo.stars} </span> </div> <span class="hover:underline text-primary">${t(lang, "recent.viewCode")}</span> </div> </a>`)} </div> </div> ` })}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/RecentPosts.astro", void 0);
const $$RecommendedPosts = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$RecommendedPosts;
  const locale = getLocaleFromUrl(Astro2.url);
  const lang = locale;
  const allPosts = await getCollection("blog");
  const localeFilter = locale === "en" ? (id) => id.startsWith("en/") : (id) => !id.startsWith("en/");
  const recommendedPosts = allPosts.filter((p) => localeFilter(p.id)).sort((a, b) => {
    const dateA = a.data.pubDate ? new Date(a.data.pubDate).valueOf() : 0;
    const dateB = b.data.pubDate ? new Date(b.data.pubDate).valueOf() : 0;
    return dateB - dateA;
  });
  [...recommendedPosts, ...recommendedPosts];
  return renderTemplate`${renderComponent($$result, "Section", $$Section, { "variant": "white", "id": "recommended", "class": "reveal !py-12 overflow-hidden", "fullWidth": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="px-lg md:px-xxl mb-8 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4"> <div class="text-center sm:text-left"> <h2 class="display-lg mb-2">${t(lang, "recommended.heading")}</h2> <div class="w-20 h-1 bg-primary mx-auto sm:mx-0"></div> </div> <div class="flex gap-2 justify-center sm:justify-end flex-shrink-0"> <button id="carousel-prev" class="p-2 bg-surface-soft border border-hairline rounded-full hover:bg-ink hover:text-white transition-colors text-ink"${addAttribute(t(lang, "recommended.prev"), "aria-label")}> <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"></path></svg> </button> <button id="carousel-next" class="p-2 bg-surface-soft border border-hairline rounded-full hover:bg-ink hover:text-white transition-colors text-ink"${addAttribute(t(lang, "recommended.next"), "aria-label")}> <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"></path></svg> </button> </div> </div> <div id="carousel-viewport" class="relative w-full overflow-hidden"> <div class="absolute left-0 top-0 bottom-0 w-16 md:w-24 bg-gradient-to-r from-white to-transparent z-10 pointer-events-none"></div> <div class="absolute right-0 top-0 bottom-0 w-16 md:w-24 bg-gradient-to-l from-white to-transparent z-10 pointer-events-none"></div> <div id="carousel-track" class="flex"> ${recommendedPosts.map((post) => {
    const slug = post.id.replace(/^(en|es)\//, "");
    const postUrl = locale === "en" ? `/en/blog/${slug}` : `/es/blog/${slug}`;
    return renderTemplate`<a${addAttribute(postUrl, "href")} class="carousel-card w-[300px] md:w-[400px] mx-3 flex-shrink-0 flex flex-col bg-[#f9f9f9] rounded-[9px] border border-hairline overflow-hidden shadow-sm hover:shadow-md transition-all duration-300"> <div class="aspect-video overflow-hidden bg-surface-soft relative"> <span class="absolute top-4 left-4 z-10 bg-primary text-white text-[10px] font-bold px-2 py-1 uppercase tracking-widest rounded-[2px]"> ${t(lang, "recommended.badge")} </span> ${post.data.heroImage ? renderTemplate`<img${addAttribute(post.data.heroImage, "src")}${addAttribute(post.data.title, "alt")} class="w-full h-full object-cover hover:scale-105 transition-transform duration-500" loading="lazy">` : renderTemplate`<div class="w-full h-full flex items-center justify-center text-ink/20 font-mono text-[10px] uppercase tracking-widest bg-gradient-to-br from-surface-soft to-gray-100"> ${t(lang, "recommended.placeholder")} </div>`} </div> <div class="p-6 flex flex-col flex-grow"> <h3 class="text-lg font-bold mb-3 line-clamp-2 leading-tight hover:text-primary transition-colors"> ${post.data.title} </h3> <p class="text-xs text-ink/60 line-clamp-3 mb-6 flex-grow"> ${post.data.description} </p> <div class="flex items-center text-[10px] font-bold uppercase tracking-widest text-primary"> ${t(lang, "recommended.leerMas")} <span class="ml-1">→</span> </div> </div> </a>`;
  })} </div> </div> ` })} ${renderScript($$result, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/RecommendedPosts.astro?astro&type=script&index=0&lang.ts")}`;
}, "C:/Users/Esteban Selvaggi/Desktop/subagent-driven_development/scripts/web_designer/example/src/components/RecommendedPosts.astro", void 0);
export {
  $$ProjectCarousel as $,
  $$SkillsSection as a,
  $$ReviewsCarousel as b,
  $$RecentPosts as c,
  $$RecommendedPosts as d
};
