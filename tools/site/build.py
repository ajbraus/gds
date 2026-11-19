"""Generate GDS inner pages (blog, FAQ, about, sitemap) into the repo.

Usage: python3 -I tools/site/build.py .
The homepage (index.html) is edited by hand; keep its header/footer in sync with layout.py."""
import os, sys, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import page, ORG, SITE, ELTON, breadcrumbs_ld, breadcrumbs_html
from posts import POSTS, DATE, DATE_H, ELTON_CTA

REPO = sys.argv[1]


def write(rel, content):
    path = os.path.join(REPO, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print("wrote", rel)


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


# ---------------------------------------------------------------- blog posts
for p in POSTS:
    path = f"/blog/{p['slug']}/"
    trail = [("Home", "/"), ("Blog", "/blog/"), (p["title"], path)]
    graph = [
        ORG,
        {
            "@type": "BlogPosting",
            "@id": SITE + path + "#article",
            "headline": p["title"],
            "description": p["description"],
            "image": [SITE + p["og"], SITE + p["image"]],
            "datePublished": DATE,
            "dateModified": DATE,
            "author": {"@id": SITE + "/#org"},
            "publisher": {"@id": SITE + "/#org"},
            "mainEntityOfPage": SITE + path,
            "inLanguage": "en",
            "wordCount": len(strip_tags(p["body"]).split()),
        },
        breadcrumbs_ld(trail),
    ]
    sources = "\n".join(
        f'                    <li id="s{i}">{t}' + (f' <a href="{u}" target="_blank" rel="noopener">{html.escape(u)}</a>' if u else "") + "</li>"
        for i, (t, u) in enumerate(p["sources"], 1)
    )
    body = f'''        <article>
            <header class="page-hero">
                <div class="container">
                    {breadcrumbs_html(trail)}
                    <p class="eyebrow">{p["tag"]}</p>
                    <h1>{p["title"]}</h1>
                    <p class="page-lead">{p["excerpt"]}</p>
                    <p class="meta">By the Gross Domestic Suffering team at Elton University · <time datetime="{DATE}">{DATE_H}</time> · {p["read"]}</p>
                </div>
            </header>
            <div class="prose">
            <figure style="margin-top:0">
                <img src="{p["image"]}" alt="{p["image_alt"]}" width="{p["image_w"]}" height="{p["image_h"]}" fetchpriority="high">
                <figcaption>{p["credit"]}</figcaption>
            </figure>
{p["body"]}
{ELTON_CTA}
            <section class="sources" aria-labelledby="sources-title">
                <h2 id="sources-title">Sources</h2>
                <ol>
{sources}
                </ol>
            </section>
            </div>
        </article>'''
    meta = f'''
    <meta property="article:published_time" content="{DATE}">
    <meta property="article:section" content="{p["tag"]}">'''
    write(f"blog/{p['slug']}/index.html",
          page(f"{p['seo_title']} | GDS", p["description"], path, graph, body, "blog",
               og_image=p["og"], og_type="article", preload=p["image"], extra_meta=meta))


# ---------------------------------------------------------------- blog index
def card(p, level="h2"):
    return f'''                <a class="post-card" href="/blog/{p["slug"]}/">
                    <img src="{p["image"]}" alt="{p["image_alt"]}" width="{p["image_w"]}" height="{p["image_h"]}" loading="lazy">
                    <div class="post-card-body">
                        <span class="tag">{p["tag"]}</span>
                        <{level}>{p["title"]}</{level}>
                        <p>{p["excerpt"]}</p>
                        <span class="read">Read the article →</span>
                    </div>
                </a>'''

trail = [("Home", "/"), ("Blog", "/blog/")]
graph = [
    ORG,
    {
        "@type": "Blog",
        "@id": SITE + "/blog/#blog",
        "name": "Gross Domestic Suffering Blog",
        "description": "Essays on alternatives to GDP, the limitations of GDP and how to measure suffering.",
        "url": SITE + "/blog/",
        "publisher": {"@id": SITE + "/#org"},
        "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}/", "datePublished": DATE} for p in POSTS],
    },
    breadcrumbs_ld(trail),
]
body = f'''        <section class="page-hero">
            <div class="container">
                {breadcrumbs_html(trail)}
                <p class="eyebrow">Blog</p>
                <h1>Beyond GDP: essays on measuring what matters</h1>
                <p class="page-lead">Plain-language guides to the alternatives to GDP, what economic statistics leave out, and how we can measure, and reduce, preventable suffering.</p>
            </div>
        </section>
        <section class="section">
            <div class="container">
                <div class="post-grid">
{chr(10).join(card(p) for p in POSTS)}
                </div>
            </div>
        </section>'''
write("blog/index.html", page("Blog: Alternatives to GDP and Measuring Suffering | GDS",
      "Guides to the best alternative to GDP, the limitations of GDP, the misery index and how the Gross Domestic Suffering index measures preventable suffering.",
      "/blog/", graph, body, "blog"))


# ---------------------------------------------------------------- FAQ
FAQ = [
    ("The basics", [
        ("What is Gross Domestic Suffering?",
         "Gross Domestic Suffering (GDS) is an open index that ranks countries by the preventable suffering their people and animals experience. It combines nine indicators in six pillars (illness, gender inequality, violence, unfreedom, deprivation and animal suffering) into one score from 0 to 100. Higher means more suffering."),
        ("Is GDS an alternative to GDP?",
         'Yes. GDS is an alternative to GDP for judging national success. GDP measures what a country produces; GDS measures the suffering that production fails to prevent. We see it as a complement to GDP, not a replacement for economic statistics. <a href="/blog/alternative-to-gdp/">Compare GDS with other alternatives to GDP</a>.'),
        ("What are the limitations of GDP?",
         'GDP ignores unpaid and household work, counts harmful spending (pollution clean-up, prisons, treating preventable disease) as growth, hides inequality, ignores the depletion of nature, and says nothing about illness, despair or suffering. <a href="/blog/limitations-of-gdp/">Read the 8 limitations of GDP</a>.'),
        ("How is GDS different from the misery index?",
         'The economic misery index, created by Arthur Okun, adds the inflation rate to the unemployment rate. GDS measures suffering directly across illness, gender inequality, violence, unfreedom, deprivation and animal suffering, rather than through two macroeconomic proxies. <a href="/blog/misery-index/">Learn more about the misery index</a>.'),
        ("Is GDS the opposite of Gross National Happiness?",
         "They are complementary. Bhutan's Gross National Happiness and the World Happiness Report ask how good life is. GDS asks how much preventable suffering remains, on the view that ending misery is the most urgent and most widely shared goal of public policy."),
    ]),
    ("The methodology", [
        ("Which indicators does GDS use?",
         'The current framework has nine indicators in six pillars, each framed as suffering. Illness: healthy life years lost to disease, despair and early death, and infant mortality. Gender inequality: the UNDP Gender Inequality Index. Violence: homicides plus deaths in war. Unfreedom: prisoners plus people in modern slavery. Deprivation: undernourishment, extreme poverty and forced displacement. Animal suffering: land animals slaughtered per person, adjusted for weak protection laws. Suicide, depression and addiction are counted inside illness, so they aren’t added twice. <a href="/#framework">See the framework</a>.'),
        ("Where does the data come from?",
         "From public, internationally comparable primary sources: the World Health Organization, World Bank, UN Development Programme, UN Office on Drugs and Crime, Uppsala Conflict Data Program, World Prison Brief, Walk Free, the UN Food and Agriculture Organization, UNHCR and World Animal Protection. The full dataset and code are open on GitHub."),
        ("Why does GDS include animal suffering?",
         "Tens of billions of animals are raised and killed each year in conditions shaped by national laws and markets. Suffering does not stop at the species line. Animal suffering is one of the six pillars of every GDS score. It counts land animals slaughtered per person, adjusted for how weak a country's animal protection laws are."),
        ("How are the indicators weighted?",
         "Each indicator is scaled from 0 to 100 against fixed goalposts that never change between years, so scores can be compared across countries and over time. The six pillars are weighted equally. We also test 1,000 random weightings and publish the range of ranks each country could receive."),
        ("Where does the United States rank?",
         "In 2023 the United States ranked 82nd of 185 countries, behind countries with a fraction of its GDP, such as China, Cuba, Vietnam and Sri Lanka. Its worst pillars are unfreedom (872 people per 100,000 in prison or modern slavery) and animal suffering."),
        ("Which countries have the least suffering?",
         "In 2023, Japan, Switzerland, Germany, Norway and Sweden had the lowest suffering scores. South Sudan, Ukraine, Haiti, Somalia and Nigeria had the highest."),
    ]),
    ("The project", [
        ("Who runs Gross Domestic Suffering?",
         f'GDS is a research project of <a href="{ELTON}" target="_blank" rel="noopener">Elton University</a>, a 501(c)(3) nonprofit university based in the United States. <a href="/about/">Read more about the project</a>.'),
        ("When will the full rankings be published?",
         'A revised, fully documented methodology and open dataset are in development. Follow the project on <a href="https://github.com/ajbraus/gds" target="_blank" rel="noopener">GitHub</a> to be notified of releases.'),
        ("Can I contribute or suggest an indicator?",
         'Yes. The methodology and code are open. You can <a href="https://github.com/ajbraus/gds/issues" target="_blank" rel="noopener">open an issue on GitHub</a> to suggest an indicator, a data source or a correction.'),
        ("Can I use GDS data in my research or reporting?",
         "Yes. Please cite Gross Domestic Suffering, Elton University, and the version of the index you used. Once the dataset is published, we plan to release it under an open license."),
        ("Can I study these questions at Elton University?",
         f'Yes. Elton University offers a master\'s in <a href="{ELTON}/economics" target="_blank" rel="noopener">Heterodox Economics</a>, taught one-on-one by expert professors, fully online.'),
    ]),
]

trail = [("Home", "/"), ("FAQ", "/faq/")]
graph = [
    ORG,
    {
        "@type": "FAQPage",
        "@id": SITE + "/faq/#faq",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for _, qs in FAQ for q, a in qs
        ],
    },
    breadcrumbs_ld(trail),
]
groups = []
for name, qs in FAQ:
    items = "\n".join(f'''                        <details>
                            <summary>{q}</summary>
                            <p>{a}</p>
                        </details>''' for q, a in qs)
    groups.append(f'''                <section class="faq-group">
                    <h2>{name}</h2>
                    <div class="faq">
{items}
                    </div>
                </section>''')
body = f'''        <section class="page-hero">
            <div class="container">
                {breadcrumbs_html(trail)}
                <p class="eyebrow">FAQ</p>
                <h1>Frequently asked questions</h1>
                <p class="page-lead">What Gross Domestic Suffering measures, how it works as an alternative to GDP, and how you can get involved.</p>
            </div>
        </section>
        <section class="section">
            <div class="container narrow">
{chr(10).join(groups)}
                <p class="center">Still have a question? <a href="https://github.com/ajbraus/gds/issues" target="_blank" rel="noopener">Ask us on GitHub</a>.</p>
            </div>
        </section>'''
write("faq/index.html", page("FAQ: Gross Domestic Suffering, an Alternative to GDP | GDS",
      "Answers about Gross Domestic Suffering: what it measures, how it differs from GDP and the misery index, its indicators, data sources and rankings.",
      "/faq/", graph, body, "faq"))


# ---------------------------------------------------------------- About
trail = [("Home", "/"), ("About", "/about/")]
graph = [
    ORG,
    {
        "@type": "AboutPage",
        "@id": SITE + "/about/#page",
        "url": SITE + "/about/",
        "name": "About Gross Domestic Suffering",
        "about": {"@id": SITE + "/#org"},
    },
    {
        "@type": "Person",
        "@id": SITE + "/about/#adam-braus",
        "name": "Adam Braus",
        "jobTitle": "Founder",
        "worksFor": {"@type": "CollegeOrUniversity", "name": "Elton University", "url": ELTON},
    },
    {
        "@type": "Book",
        "name": "The Future of Good: How to Tell Good from Evil in an Age of Distraction, Polarization, and Crisis",
        "author": {"@id": SITE + "/about/#adam-braus"},
        "publisher": {"@type": "Organization", "name": "Peripatetic Press"},
        "datePublished": "2022",
        "isbn": "9798986640549",
        "url": "https://www.amazon.com/dp/B0B7KF4VPS",
    },
    breadcrumbs_ld(trail),
]
body = f'''        <section class="page-hero">
            <div class="container">
                {breadcrumbs_html(trail)}
                <p class="eyebrow">About</p>
                <h1>A project of Elton University</h1>
                <p class="page-lead">Gross Domestic Suffering is an open research project of Elton University, a nonprofit university, building a better alternative to GDP: a measure of the preventable suffering we can work together to end.</p>
            </div>
        </section>
        <div class="prose">
            <h2>Our mission</h2>
            <p>We believe the success of a nation should be judged by how much avoidable suffering its people and animals endure, not only by how much it produces. Our mission is to measure that suffering openly and rigorously, so citizens, researchers and governments can see it, compare it and reduce it.</p>
            <div class="facts">
                <div><strong>185</strong><span>countries scored every year, 2000–2023</span></div>
                <div><strong>6</strong><span>pillars of preventable suffering</span></div>
                <div><strong>100% open</strong><span>methodology, data and code</span></div>
            </div>

            <h2>Based at Elton University</h2>
            <p><a href="{ELTON}" target="_blank" rel="noopener">Elton University</a> is a 501(c)(3) nonprofit university based in the United States, with students studying online from anywhere or in person in San Francisco. Its mission is "to provide the highest possible quality education for everyone." Educator and researcher Adam Braus founded Elton in 2021 to build a university on what the evidence says about how people learn, with personalized degrees taught one-on-one by expert professors.</p>
            <p>Gross Domestic Suffering fits Elton's commitment to serving students, the country and the world. The project connects to Elton's master's program in <a href="{ELTON}/economics" target="_blank" rel="noopener">Heterodox Economics</a>, where students question conventional economic measures and build better ones.</p>

            <h2>Created by Adam Braus</h2>
            <p>Gross Domestic Suffering was created by Adam Braus, an educator, writer and the founder of Elton University. It began with a simple question: if GDP measures everything except what makes life worthwhile, what would it look like to measure the opposite?</p>
            <p>Leading economists have asked the same question. In September 2020, Nobel laureate Paul Krugman warned in <a href="https://www.nytimes.com/2020/09/07/opinion/trump-economy-jobs.html" target="_blank" rel="noopener"><em>The New York Times</em></a> that "despite job gains we're in the midst of a huge increase in national misery." Gross Domestic Suffering measures that misery directly.</p>
            <p>The answer is an index of preventable suffering across illness, gender inequality, violence, unfreedom, deprivation and animal suffering. It scores 185 countries for every year since 2000. Japan, Switzerland and Germany suffer least. The United States, the world's largest economy, ranks 82nd, behind China, Cuba, Vietnam and Sri Lanka.</p>

            <aside class="callout book">
                <p class="eyebrow eyebrow-dark">The book</p>
                <h3><a href="https://www.amazon.com/dp/B0B7KF4VPS" target="_blank" rel="noopener"><em>The Future of Good</em></a></h3>
                <p><strong>How to Tell Good from Evil in an Age of Distraction, Polarization, and Crisis</strong></p>
                <p>In <em>The Future of Good</em> (Peripatetic Press, 2022), Adam Braus revives a century-old theory of good and evil and applies it to today's moral challenges, drawing on history, philosophy, psychology and neuro- and evolutionary biology. The book shows how to build good institutions, recognize good leaders and live as good people. Gross Domestic Suffering asks the same kind of question of whole countries: how much preventable suffering do they allow?</p>
                <a class="btn btn-primary" href="https://www.amazon.com/dp/B0B7KF4VPS" target="_blank" rel="noopener">Get the book on Amazon</a>
            </aside>

            <h2>Our principles</h2>
            <ul>
                <li><strong>Measure outcomes.</strong> We count suffering that happens, such as deaths, disease, violence and imprisonment, rather than policies or intentions.</li>
                <li><strong>Focus on what's preventable.</strong> Every indicator tracks harm that some countries have already reduced, which shows it can be reduced.</li>
                <li><strong>Work in the open.</strong> Our methods, data and code are public, and we welcome criticism.</li>
                <li><strong>Include all who suffer.</strong> We measure human-caused animal suffering alongside human suffering.</li>
            </ul>

            <h2>Get involved</h2>
            <p>We welcome researchers, students, journalists and policymakers. Review the methodology and suggest indicators on <a href="https://github.com/ajbraus/gds" target="_blank" rel="noopener">GitHub</a>, read our <a href="/blog/">blog</a> and <a href="/faq/">FAQ</a>, or <a href="{ELTON}/donate" target="_blank" rel="noopener">support Elton University's nonprofit mission</a>.</p>

            <aside class="post-cta">
                <h2>Study economics that measures what matters</h2>
                <p>Elton University's master's in Heterodox Economics is taught one-on-one by expert professors and is fully online.</p>
                <a class="btn btn-primary" href="{ELTON}/economics" target="_blank" rel="noopener">Explore the program</a>
                <a class="btn btn-ghost" href="/#framework">See the GDS framework</a>
            </aside>

            <section class="sources" id="credits" aria-labelledby="credits-title">
                <h2 id="credits-title">Image credits</h2>
                <ul class="credits-list">
                    <li>Earth's City Lights: NASA Goddard Space Flight Center / NOAA DMSP data, <a href="https://commons.wikimedia.org/wiki/File:Earth%27s_City_Lights_by_DMSP,_1994-1995_(large).jpg" target="_blank" rel="noopener">public domain</a></li>
                    <li>Robert F. Kennedy, 1968 campaign photo, <a href="https://commons.wikimedia.org/wiki/File:1968_ROBERT_F._KENNEDY_glossy_photo_handout_(cropped).jpg" target="_blank" rel="noopener">public domain</a></li>
                    <li>Homeless encampment under bridge in Chicago: Grendelkhan, <a href="https://commons.wikimedia.org/wiki/File:Homeless_encampment_under_bridge_in_Chicago.jpg" target="_blank" rel="noopener">CC BY-SA 4.0</a></li>
                    <li>Hospital corridor, NÄL hospital: W.carter, <a href="https://commons.wikimedia.org/wiki/File:Corridor_on_the_second_level_-_N%C3%84L_hospital_1.jpg" target="_blank" rel="noopener">CC0</a></li>
                    <li>Moyamensing Prison: Historic American Buildings Survey, Library of Congress, <a href="https://commons.wikimedia.org/wiki/File:Philadelphia_County_Prison_(Moyamensing_Prison)_Philadelphia_PA_(7)_139920pu.jpg" target="_blank" rel="noopener">public domain</a></li>
                    <li>Hens in battery cages: Lever Foundation, <a href="https://commons.wikimedia.org/wiki/File:Subway_egg_supplier_investigation_-_birds_crammed_in_cages.jpg" target="_blank" rel="noopener">CC0</a></li>
                    <li>Air pollution in São Paulo: Wilfredor, <a href="https://commons.wikimedia.org/wiki/File:Panoramic_view_of_air_pollution_in_S%C3%A3o_Paulo_city,_Brazil.jpg" target="_blank" rel="noopener">CC0</a></li>
                </ul>
            </section>
        </div>'''
write("about/index.html", page("About GDS: A Project of Elton University",
      "Gross Domestic Suffering, created by Adam Braus, author of The Future of Good, is an open project of Elton University measuring preventable suffering as an alternative to GDP.",
      "/about/", graph, body, "about"))


# ---------------------------------------------------------------- home "from the blog" cards
with open(os.path.join(REPO, "_blog_cards.tmp"), "w") as f:  # for pasting into index.html; delete after use
    f.write("\n".join(card(p, "h3") for p in POSTS))

# ---------------------------------------------------------------- sitemap
urls = [("/", "1.0"), ("/about/", "0.7"), ("/faq/", "0.7"), ("/blog/", "0.8")] + \
       [(f"/blog/{p['slug']}/", "0.8") for p in POSTS]
sm = "\n".join(f"  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{DATE}</lastmod>\n    <priority>{pr}</priority>\n  </url>" for u, pr in urls)
write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
