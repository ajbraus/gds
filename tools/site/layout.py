"""Shared head/header/footer for grossdomesticsuffering.org static pages."""
import json, html

SITE = "https://grossdomesticsuffering.org"
ELTON = "https://elton.university"

NAV = [
    ("/#framework", "The index", "index"),
    ("/#prototype", "Findings", "findings"),
    ("/blog/", "Blog", "blog"),
    ("/faq/", "FAQ", "faq"),
    ("/about/", "About", "about"),
]

ORG = {
    "@type": "Organization",
    "@id": SITE + "/#org",
    "name": "Gross Domestic Suffering Initiative",
    "alternateName": "GDS",
    "url": SITE + "/",
    "logo": SITE + "/favicon.svg",
    "parentOrganization": {
        "@type": "CollegeOrUniversity",
        "@id": ELTON + "/#org",
        "name": "Elton University",
        "url": ELTON,
        "nonprofitStatus": "Nonprofit501c3",
    },
    "sameAs": ["https://github.com/ajbraus/gds"],
}


def header(active):
    items = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == active else ""
        items.append(f'                <li><a href="{href}"{cur}>{label}</a></li>')
    items.append('                <li><a class="nav-cta" href="/#join">Get involved</a></li>')
    return f'''    <a class="skip-link" href="#main">Skip to content</a>

    <header class="site-header" id="top">
        <nav class="nav container" aria-label="Main">
            <a class="brand" href="/" aria-label="Gross Domestic Suffering home">
                <svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="14" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M6 19c4-6 7 3 10-3s6 4 10-2" fill="none" stroke="#f0a73b" stroke-width="2.5" stroke-linecap="round"/></svg>
                <span>Gross Domestic Suffering</span>
            </a>
            <button class="nav-toggle" aria-expanded="false" aria-controls="nav-links" aria-label="Open menu">
                <span></span><span></span><span></span>
            </button>
            <ul class="nav-links" id="nav-links">
{chr(10).join(items)}
            </ul>
        </nav>
    </header>
'''


FOOTER = f'''    <footer class="site-footer">
        <div class="container footer-inner">
            <div>
                <p class="footer-brand">Gross Domestic Suffering</p>
                <p class="footer-note">A project of <a href="{ELTON}" target="_blank" rel="noopener">Elton University</a>, a 501(c)(3) nonprofit university.</p>
                <p class="footer-note">&copy; 2026 Gross Domestic Suffering Initiative.</p>
            </div>
            <ul class="footer-links" aria-label="Footer">
                <li><a href="/">Home</a></li>
                <li><a href="/about/">About</a></li>
                <li><a href="/blog/">Blog</a></li>
                <li><a href="/faq/">FAQ</a></li>
                <li><a href="/blog/alternative-to-gdp/">Alternatives to GDP</a></li>
                <li><a href="/blog/limitations-of-gdp/">Limitations of GDP</a></li>
                <li><a href="/blog/misery-index/">Misery index</a></li>
                <li><a href="https://github.com/ajbraus/gds" target="_blank" rel="noopener">GitHub</a></li>
                <li><a href="/about/#credits">Image credits</a></li>
            </ul>
            <a class="to-top" href="#top">Back to top ↑</a>
        </div>
    </footer>

    <script>
        const toggle = document.querySelector('.nav-toggle');
        const links = document.getElementById('nav-links');
        toggle.addEventListener('click', () => {{
            const open = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', String(!open));
            links.classList.toggle('open', !open);
        }});
        links.addEventListener('click', e => {{
            if (e.target.tagName === 'A') {{
                toggle.setAttribute('aria-expanded', 'false');
                links.classList.remove('open');
            }}
        }});
    </script>
'''


def head(title, description, path, graph, og_image="/images/og-image.jpg",
         og_type="website", preload=None, extra_meta=""):
    url = SITE + path
    e = html.escape
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
    ld = "\n".join("    " + line for line in ld.splitlines())
    pre = f'\n    <link rel="preload" as="image" href="{preload}" fetchpriority="high">' if preload else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}">
    <link rel="canonical" href="{url}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <meta name="theme-color" content="#0b1020">

    <meta property="og:type" content="{og_type}">
    <meta property="og:site_name" content="Gross Domestic Suffering">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{SITE}{og_image}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{e(title)}">
    <meta name="twitter:description" content="{e(description)}">
    <meta name="twitter:image" content="{SITE}{og_image}">{extra_meta}

    <link rel="icon" href="/favicon.svg" type="image/svg+xml">{pre}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="/styles.css" rel="stylesheet">

    <script type="application/ld+json">
{ld}
    </script>
</head>
<body>
'''


def breadcrumbs_ld(trail):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + path}
            for i, (name, path) in enumerate(trail)
        ],
    }


def breadcrumbs_html(trail):
    lis = []
    for i, (name, path) in enumerate(trail):
        if i == len(trail) - 1:
            lis.append(f'<li aria-current="page">{name}</li>')
        else:
            lis.append(f'<li><a href="{path}">{name}</a></li>')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'


def page(title, description, path, graph, body, active, **kw):
    return head(title, description, path, graph, **kw) + header(active) + "\n    <main id=\"main\">\n" + body + "\n    </main>\n\n" + FOOTER + "</body>\n</html>\n"
