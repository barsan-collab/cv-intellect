"""
CV Intellect — Advanced Resume Parsing Engine v2
Features: multi-dimensional scoring, archetype detection, seniority classification,
certifications, soft skills, human languages, career gap detection, ATS scoring,
red flags, actionable recommendations, completeness scoring, and more.
No external API required — pure Python.
"""

import re
from dataclasses import dataclass, field
from collections import Counter


# ════════════════════════════════════════════════════════════
#  KNOWLEDGE BASES
# ════════════════════════════════════════════════════════════

SKILLS_DB = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang",
        "rust", "php", "ruby", "swift", "kotlin", "scala", "r", "perl", "bash", "shell",
        "powershell", "dart", "lua", "haskell", "matlab", "assembly", "vba", "groovy",
        "elixir", "clojure", "f#", "ocaml", "fortran", "cobol", "solidity",
    ],
    "Web & Frontend": [
        "react", "angular", "vue", "next.js", "nuxt", "svelte", "sveltekit", "html", "css",
        "sass", "less", "tailwind", "bootstrap", "jquery", "redux", "zustand", "graphql",
        "webpack", "vite", "parcel", "rollup", "web components", "pwa", "webassembly",
        "three.js", "d3.js", "chartjs", "gsap", "framer motion", "storybook",
    ],
    "Backend & Frameworks": [
        "node.js", "express", "django", "flask", "fastapi", "spring", "spring boot",
        "laravel", "rails", "asp.net", ".net core", "nestjs", "gin", "fiber", "actix",
        "rocket", "phoenix", "tornado", "aiohttp", "hapi", "koa", "strapi", "supabase",
        "pocketbase", "appwrite", "grpc", "graphql", "rest api", "soap",
    ],
    "Data & AI / ML": [
        "machine learning", "deep learning", "neural network", "nlp",
        "natural language processing", "computer vision", "reinforcement learning",
        "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost", "lightgbm",
        "pandas", "numpy", "matplotlib", "seaborn", "plotly", "opencv", "pillow",
        "hugging face", "transformers", "langchain", "llm", "rag", "vector database",
        "data science", "data engineering", "statistics", "a/b testing",
        "spark", "pyspark", "hadoop", "kafka", "airflow", "prefect", "dbt", "flink",
        # BI tools intentionally kept but in Finance & Business too — weight kept low
        "tableau", "power bi", "looker", "metabase", "superset", "data analysis",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "alibaba cloud", "digitalocean", "heroku",
        "docker", "kubernetes", "k8s", "openshift", "rancher",
        "terraform", "ansible", "puppet", "chef", "pulumi",
        "jenkins", "github actions", "gitlab ci", "circle ci", "travis ci", "argocd",
        "ci/cd", "devops", "sre", "microservices", "serverless", "lambda",
        "ec2", "s3", "rds", "ecs", "eks", "cloudformation", "cdk",
        "helm", "istio", "envoy", "nginx", "apache",
        "prometheus", "grafana", "datadog", "new relic", "splunk", "elk", "loki",
    ],
    "Databases": [
        "mysql", "postgresql", "postgres", "mongodb", "redis", "sqlite", "cassandra",
        "dynamodb", "firebase", "supabase", "oracle", "sql server", "mariadb",
        "neo4j", "influxdb", "timescaledb", "cockroachdb", "planetscale",
        "elasticsearch", "opensearch", "solr", "pinecone", "weaviate", "chroma",
        "snowflake", "bigquery", "redshift", "databricks", "delta lake",
    ],
    "Tools & Practices": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "notion",
        "agile", "scrum", "kanban", "tdd", "bdd", "ddd", "solid",
        "unit testing", "integration testing", "e2e testing",
        "jest", "pytest", "junit", "mocha", "vitest", "cypress", "playwright", "selenium",
        "postman", "insomnia", "swagger", "openapi", "grpc",
        "figma", "sketch", "adobe xd", "invision", "zeplin",
        "linux", "unix", "bash scripting", "makefile", "gradle", "maven", "npm", "yarn", "pnpm",
    ],
    "Security": [
        "cybersecurity", "penetration testing", "ethical hacking", "vulnerability assessment",
        "owasp", "ssl", "tls", "oauth", "jwt", "authentication", "authorization",
        "sast", "dast", "soc", "siem", "iam", "zero trust",
        "burp suite", "metasploit", "nmap", "wireshark", "kali linux",
    ],
    "Mobile": [
        "android", "ios", "react native", "flutter", "xamarin", "ionic", "expo",
        "swift", "objective-c", "kotlin", "jetpack compose", "swiftui",
        "mobile development", "cross-platform",
    ],
    "Blockchain & Web3": [
        "blockchain", "ethereum", "solidity", "web3", "smart contract",
        "defi", "nft", "polygon", "solana", "hyperledger", "ipfs",
    ],
    "Finance & Business": [
        "financial analysis", "financial reporting", "financial planning",
        "financial management", "financial modelling", "financial statements",
        "gaap", "ifrs", "us gaap", "sox", "sarbanes",
        "sap erp", "oracle erp", "sap", "blackline", "hyperion",
        "record-to-report", "rtr", "procure-to-pay", "order-to-cash",
        "accounts payable", "accounts receivable", "general ledger",
        "journal entries", "accruals", "reconciliation", "bank reconciliation",
        "variance analysis", "flux analysis", "income statement", "balance sheet",
        "cash flow", "budgeting", "forecasting", "audit", "internal audit",
        "external audit", "compliance", "internal controls", "sox compliance",
        "treasury", "cash management", "working capital",
        "erp", "quickbooks", "xero", "netsuite", "sage",
        "financial analyst", "cfa", "cpa", "cma", "acca", "ca",
        "investment", "equity", "derivatives", "portfolio", "valuation",
        "tax", "vat", "gst", "payroll",
    ],
}

CERTIFICATIONS_DB = [
    # AWS
    "aws certified solutions architect", "aws solutions architect",
    "aws certified developer", "aws certified sysops", "aws certified devops",
    "aws cloud practitioner", "aws certified", "aws associate", "aws professional",
    # GCP
    "google cloud certified", "google cloud professional", "gcp professional",
    "google associate cloud engineer", "google professional cloud architect",
    # Azure
    "microsoft certified", "azure administrator", "azure developer",
    "azure solutions architect", "azure devops engineer", "azure fundamentals",
    "az-900", "az-104", "az-204", "az-305",
    # Kubernetes / DevOps
    "certified kubernetes administrator", "cka", "ckad", "cks",
    "docker certified associate", "dca",
    "terraform certified", "hashicorp certified terraform",
    # Project / Process
    "pmp", "prince2", "certified scrum master", "csm", "psm i", "psm ii",
    "safe agilist", "safe practitioner", "itil foundation", "itil v4",
    "six sigma", "green belt", "black belt", "lean six sigma",
    # Security
    "cissp", "ceh", "certified ethical hacker", "oscp",
    "comptia security+", "comptia network+", "comptia a+", "comptia pentest+",
    "cism", "cisa", "crisc",
    # Data / Analytics
    "databricks certified", "snowflake certified", "snowpro",
    "tableau certified", "power bi certified", "microsoft power bi",
    "google data analytics", "ibm data science",
    # Dev specific
    "oracle certified professional", "oracle certified associate",
    "java certified", "spring professional",
    "red hat certified engineer", "rhce", "rhcsa",
    "lpic", "linux professional",
    "tensorflow developer certificate",
    # Misc
    "certified information systems auditor",
    "cisco ccna", "cisco ccnp", "cisco ccsp",
]

SOFT_SKILLS_DB = [
    "leadership", "communication", "teamwork", "collaboration", "problem-solving",
    "problem solving", "analytical thinking", "critical thinking", "strategic thinking",
    "time management", "project management", "stakeholder management",
    "decision making", "decision-making", "conflict resolution",
    "mentoring", "coaching", "people management", "cross-functional",
    "adaptability", "flexibility", "creativity", "innovation",
    "attention to detail", "multitasking", "self-motivated", "proactive",
    "presentation skills", "public speaking", "negotiation",
    "customer service", "client management", "emotional intelligence",
    "organizational skills", "planning", "prioritization",
]

HUMAN_LANGUAGES_DB = [
    "english", "spanish", "french", "german", "mandarin", "chinese", "cantonese",
    "japanese", "arabic", "portuguese", "hindi", "russian", "italian", "korean",
    "dutch", "swedish", "norwegian", "danish", "polish", "turkish",
    "thai", "vietnamese", "indonesian", "malay", "bengali", "urdu",
    "greek", "hebrew", "persian", "farsi", "swahili", "tagalog",
]

DEGREE_LEVELS = {
    "phd": 5, "ph.d": 5, "ph.d.": 5, "doctorate": 5, "doctoral": 5,
    "master": 4, "masters": 4, "m.sc": 4, "m.s.": 4, "m.s ": 4,
    "m.tech": 4, "m.e.": 4, "mba": 4, "m.b.a": 4, "mca": 4, "m.ca": 4,
    "bachelor": 3, "bachelors": 3, "b.sc": 3, "b.s.": 3, "b.s ": 3,
    "b.tech": 3, "b.e.": 3, "b.a.": 3, "b.com": 3, "b.eng": 3,
    "associate": 2, "a.s.": 2, "a.a.": 2,
    "diploma": 1, "certificate": 1, "certification": 1,
    "high school": 0, "secondary school": 0,
}

SENIORITY_MAP = {
    "executive": [
        "chief executive", "chief technology", "chief operating", "chief financial",
        "chief product", "chief information", "cto", "ceo", "coo", "cfo", "cpo", "ciso",
        "vice president", "vp of engineering", "svp", "evp",
    ],
    "director": [
        "director of engineering", "director of technology", "engineering director",
        "technical director", "head of engineering", "head of technology",
        "head of product", "head of data", "head of design", "head of",
        "senior director",
    ],
    "principal": [
        "principal engineer", "principal architect", "staff engineer", "staff scientist",
        "distinguished engineer", "fellow", "principal software", "principal data",
    ],
    "senior": [
        "senior software", "senior engineer", "senior developer", "senior architect",
        "senior manager", "senior consultant", "senior analyst", "senior scientist",
        "senior data", "senior product", "senior designer", "tech lead", "technical lead",
        "team lead", "lead engineer", "lead developer", "lead architect",
        "engineering manager", "product manager",
    ],
    "mid": [
        "software engineer", "software developer", "full stack", "backend engineer",
        "frontend engineer", "mobile developer", "data engineer", "data analyst",
        "machine learning engineer", "ml engineer", "devops engineer", "sre",
        "cloud engineer", "systems engineer", "product designer", "ux designer",
        "security engineer", "qa engineer", "test engineer",
    ],
    "junior": [
        "junior", "jr.", "associate engineer", "associate developer",
        "intern", "trainee", "graduate", "entry level", "entry-level", "fresher",
        "apprentice",
    ],
}

SECTION_KEYWORDS = {
    "summary":      ["summary", "professional summary", "objective", "career objective",
                     "profile", "about me", "overview", "about", "bio", "introduction"],
    "experience":   ["experience", "work history", "employment history", "career history",
                     "work experience", "professional experience", "professional background",
                     "positions held", "employment", "roles"],
    "education":    ["education", "academic background", "academic qualification",
                     "qualification", "academic", "schooling", "degree", "university"],
    "skills":       ["skills", "technical skills", "core competencies", "competencies",
                     "expertise", "technologies", "tech stack", "tools", "proficiencies",
                     "languages", "frameworks"],
    "projects":     ["projects", "personal projects", "portfolio", "key projects",
                     "notable projects", "open source", "side projects", "work samples"],
    "achievements": ["achievements", "accomplishments", "awards", "certifications",
                     "honors", "recognition", "publications", "patents", "accolades"],
    "languages":    ["languages", "spoken languages", "language proficiency"],
    "interests":    ["interests", "hobbies", "activities", "volunteer"],
    "references":   ["references", "referees"],
}

ACTION_VERBS_STRONG = [
    "architected", "engineered", "spearheaded", "pioneered", "orchestrated",
    "transformed", "overhauled", "revamped", "revolutionized", "scaled",
    "automated", "optimized", "accelerated", "streamlined", "consolidated",
    "directed", "supervised", "mentored", "led", "managed",
]

ACTION_VERBS_STANDARD = [
    "developed", "built", "designed", "implemented", "created",
    "improved", "increased", "reduced", "achieved", "delivered",
    "deployed", "launched", "coordinated", "analyzed", "established",
    "collaborated", "integrated", "maintained", "migrated", "refactored",
    "configured", "monitored", "tested", "documented", "supported",
    "researched", "authored", "contributed", "presented",
]

WEAK_LANGUAGE = [
    "responsible for", "duties included", "helped with", "assisted in",
    "worked on", "involved in", "participated in", "tasked with",
    "was in charge of", "handled",
]

ARCHETYPE_WEIGHTS = {
    "Full Stack Developer": {
        "Web & Frontend": 1.5, "Backend & Frameworks": 1.5, "Databases": 1.0,
    },
    "Frontend Developer": {
        "Web & Frontend": 3.0, "Tools & Practices": 0.5,
    },
    "Backend Engineer": {
        "Backend & Frameworks": 2.5, "Databases": 1.5, "Tools & Practices": 0.5,
    },
    # Require strong programming signal to avoid misclassifying BI-tool finance users
    "Data Scientist / ML Engineer": {
        "Data & AI / ML": 3.0, "Programming Languages": 1.5,
    },
    "Data / BI Analyst": {
        "Data & AI / ML": 2.5, "Databases": 1.0,
    },
    "Data Engineer": {
        "Data & AI / ML": 2.0, "Databases": 1.5, "Cloud & DevOps": 1.0,
    },
    "DevOps / SRE Engineer": {
        "Cloud & DevOps": 3.0, "Tools & Practices": 1.5,
    },
    "Cloud Architect": {
        "Cloud & DevOps": 3.0, "Databases": 0.5, "Security": 0.5,
    },
    "Mobile Developer": {
        "Mobile": 4.0, "Programming Languages": 0.5,
    },
    "Security Engineer": {
        "Security": 4.0, "Tools & Practices": 0.5,
    },
    "Blockchain Developer": {
        "Blockchain & Web3": 4.0, "Programming Languages": 0.5,
    },
    # Finance/business gets its own archetype with dominant Finance & Business weight
    "Finance / Business Professional": {
        "Finance & Business": 4.0, "Data & AI / ML": 0.3,
    },
    "Software Engineer": {
        "Programming Languages": 2.0, "Tools & Practices": 1.0, "Databases": 0.5,
    },
}


# ════════════════════════════════════════════════════════════
#  DATA CONTAINER
# ════════════════════════════════════════════════════════════

@dataclass
class CVAnalysis:
    # ── Core (backward-compatible) ──────────────────────────
    name:    str = "Unknown Candidate"
    email:   str = "Not Provided"
    phone:   str = "Not Provided"
    rating:  int = 0
    verdict: str = ""
    pros:    list = field(default_factory=list)
    cons:    list = field(default_factory=list)

    # ── Identity ─────────────────────────────────────────────
    location:  str = ""
    linkedin:  str = ""
    github:    str = ""
    website:   str = ""

    # ── Professional profile ─────────────────────────────────
    job_title:  str = ""
    seniority:  str = "Unknown"
    archetype:  str = "Software Professional"
    industry:   str = ""
    years_exp:  int = 0
    companies:  list = field(default_factory=list)

    # ── Skills & credentials ─────────────────────────────────
    skills_by_category: dict = field(default_factory=dict)
    top_skills:         list = field(default_factory=list)
    soft_skills:        list = field(default_factory=list)
    certifications:     list = field(default_factory=list)
    languages_spoken:   list = field(default_factory=list)

    # ── Education ────────────────────────────────────────────
    degree_level: int = 0
    degree_name:  str = ""
    institution:  str = ""
    grad_year:    int = 0
    gpa:          str = ""

    # ── Multi-dimensional scores (0-100) ─────────────────────
    technical_score:    int = 0
    experience_score:   int = 0
    education_score:    int = 0
    presentation_score: int = 0
    impact_score:       int = 0
    ats_score:          int = 0
    completeness_pct:   int = 0

    # ── Quality metrics ──────────────────────────────────────
    word_count:       int = 0
    bullet_count:     int = 0
    action_verb_count:int = 0
    strong_verb_count:int = 0
    quant_count:      int = 0
    weak_lang_count:  int = 0
    sections_found:   list = field(default_factory=list)

    # ── Career analysis ──────────────────────────────────────
    career_gap_months: int = 0
    job_roles:         list = field(default_factory=list)  # [{title, company, years}]
    career_progression: str = ""  # ascending / lateral / unclear

    # ── Flags & guidance ────────────────────────────────────
    red_flags:       list = field(default_factory=list)
    recommendations: list = field(default_factory=list)


# ════════════════════════════════════════════════════════════
#  PARSER ENGINE
# ════════════════════════════════════════════════════════════

class CVParser:

    # ── Entry point ──────────────────────────────────────────

    def parse(self, raw_text: str) -> CVAnalysis:
        text  = self._clean(raw_text)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        lower = text.lower()

        a = CVAnalysis()

        # ── Extraction layer ─────────────────────────────
        a.name     = self._extract_name(lines)
        a.email    = self._extract_email(text)
        a.phone    = self._extract_phone(text)
        a.location = self._extract_location(text)
        a.linkedin = self._extract_linkedin(text)
        a.github   = self._extract_github(text)
        a.website  = self._extract_website(text)

        # ── Analysis passes ──────────────────────────────
        a.skills_by_category  = self._detect_skills(lower)
        a.top_skills          = self._top_skills(a.skills_by_category)
        a.soft_skills         = self._detect_soft_skills(lower)
        a.certifications      = self._detect_certifications(lower)
        a.languages_spoken    = self._detect_languages(lower)
        a.sections_found      = sorted(self._detect_sections(lower))

        a.degree_level, a.degree_name = self._detect_degree(lower)
        a.institution  = self._detect_institution(lines, lower)
        a.grad_year    = self._detect_grad_year(text)
        a.gpa          = self._detect_gpa(text)

        a.years_exp    = self._estimate_years(text)
        a.companies    = self._extract_companies(lines, lower)
        a.job_title    = self._extract_job_title(lines, lower)
        a.seniority    = self._detect_seniority(lower, a.years_exp, a.job_title)
        a.archetype    = self._detect_archetype(a.skills_by_category, lower)

        a.word_count        = len(text.split())
        a.bullet_count      = self._count_bullets(lines)
        a.action_verb_count = self._count_verbs(lower, ACTION_VERBS_STANDARD + ACTION_VERBS_STRONG)
        a.strong_verb_count = self._count_verbs(lower, ACTION_VERBS_STRONG)
        a.quant_count       = self._count_quantified(text)
        a.weak_lang_count   = self._count_weak_language(lower)

        a.career_gap_months, a.job_roles = self._analyze_career_timeline(text)
        a.career_progression = self._detect_progression(a.job_roles)

        # ── Multi-dimensional scoring ─────────────────────
        a.technical_score    = self._score_technical(a)
        a.experience_score   = self._score_experience(a)
        a.education_score    = self._score_education(a)
        a.presentation_score = self._score_presentation(a)
        a.impact_score       = self._score_impact(a)
        a.ats_score          = self._score_ats(a)
        a.completeness_pct   = self._score_completeness(a)

        a.rating = self._compute_overall(a)

        # ── Narrative generation ──────────────────────────
        a.red_flags      = self._find_red_flags(a)
        a.recommendations= self._generate_recommendations(a)
        a.pros, a.cons   = self._generate_insights(a)
        a.verdict        = self._generate_verdict(a)

        return a

    # ════════════════════════════════════════════════════════
    #  EXTRACTION LAYER
    # ════════════════════════════════════════════════════════

    def _clean(self, text: str) -> str:
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _extract_name(self, lines: list) -> str:
        skip = re.compile(r'[@\d/:|()\[\]{}#\\<>]')
        name_re = re.compile(r'^(?:Dr\.?\s+|Mr\.?\s+|Ms\.?\s+|Mrs\.?\s+|Prof\.?\s+)?'
                              r'[A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3}'
                              r'(?:\s+(?:Jr\.?|Sr\.?|III|II|IV))?$')
        for line in lines[:12]:
            clean = line.strip().strip('*|-_•')
            if len(clean) < 3 or skip.search(clean):
                continue
            if name_re.match(clean) and len(clean.split()) <= 5:
                return clean
        # Looser fallback
        for line in lines[:6]:
            words = line.strip().split()
            if 2 <= len(words) <= 4:
                if all(w[0].isupper() for w in words if w.isalpha() and len(w) > 1):
                    return line.strip()
        return "Unknown Candidate"

    def _extract_email(self, text: str) -> str:
        m = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
        return m.group(0).lower() if m else "Not Provided"

    def _extract_phone(self, text: str) -> str:
        patterns = [
            r'\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{3,5}[\s\-]?\d{3,5}',
            r'\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}',
            r'\d{5}[\s\-]?\d{5,6}',
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                raw = m.group(0).strip()
                if len(re.sub(r'\D', '', raw)) >= 9:
                    return raw
        return "Not Provided"

    def _extract_location(self, text: str) -> str:
        # City, State / City, Country patterns
        patterns = [
            r'[A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\s+\d{5}',      # City, ST 12345
            r'[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]{2,20}',  # City, Country
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                loc = m.group(0).strip()
                if len(loc) < 60:
                    return loc
        return ""

    def _extract_linkedin(self, text: str) -> str:
        m = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9\-_%]+)', text, re.IGNORECASE)
        if m:
            return f"linkedin.com/in/{m.group(1)}"
        if "linkedin" in text.lower():
            return "LinkedIn (URL not parsed)"
        return ""

    def _extract_github(self, text: str) -> str:
        m = re.search(r'(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9\-_]+)', text, re.IGNORECASE)
        if m:
            return f"github.com/{m.group(1)}"
        if "github" in text.lower():
            return "GitHub (URL not parsed)"
        return ""

    def _extract_website(self, text: str) -> str:
        m = re.search(
            r'https?://(?!(?:www\.)?(?:linkedin|github|twitter|facebook|instagram))[A-Za-z0-9\-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',
            text
        )
        return m.group(0) if m else ""

    # ════════════════════════════════════════════════════════
    #  SKILLS & CREDENTIALS
    # ════════════════════════════════════════════════════════

    def _detect_skills(self, lower: str) -> dict:
        found = {}
        for cat, skills in SKILLS_DB.items():
            hits = []
            for skill in skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', lower):
                    hits.append(skill)
            if hits:
                found[cat] = sorted(set(hits))
        return found

    def _top_skills(self, by_cat: dict, n: int = 8) -> list:
        """Return top N skills: prioritise categories with most hits."""
        all_skills = []
        for skills in by_cat.values():
            all_skills.extend(skills)
        return [s.title() for s in all_skills[:n]]

    def _detect_soft_skills(self, lower: str) -> list:
        found = []
        for skill in SOFT_SKILLS_DB:
            if re.search(r'\b' + re.escape(skill) + r'\b', lower):
                found.append(skill.title())
        return sorted(set(found))[:10]

    def _detect_certifications(self, lower: str) -> list:
        found = []
        for cert in CERTIFICATIONS_DB:
            if cert in lower:
                found.append(cert)
        # Remove shorter certs that are substrings of a longer detected cert
        deduped = [c for c in found
                   if not any(c != other and c in other for other in found)]
        return sorted({c.title() for c in deduped})

    def _detect_languages(self, lower: str) -> list:
        found = []
        for lang in HUMAN_LANGUAGES_DB:
            if re.search(r'\b' + lang + r'\b', lower):
                found.append(lang.title())
        return sorted(set(found))

    # ════════════════════════════════════════════════════════
    #  EDUCATION
    # ════════════════════════════════════════════════════════

    def _detect_degree(self, lower: str) -> tuple:
        best_level = 0
        best_name  = ""
        for token, level in DEGREE_LEVELS.items():
            # Strip trailing dots so word-boundary matches work (e.g. "b.s." → "b.s")
            core = token.rstrip('.')
            if re.search(r'\b' + re.escape(core) + r'\b', lower) and level > best_level:
                best_level = level
                m = re.search(r'\b' + re.escape(core) + r'[\w\s\'.]{0,60}', lower)
                best_name = m.group(0).strip().title() if m else token.title()
        return best_level, best_name

    def _detect_institution(self, lines: list, lower: str) -> str:
        markers = ["university", "college", "institute", "school of", "academy",
                   "polytechnic", "iit", "nit", "mit", "stanford", "harvard",
                   "oxford", "cambridge", "bits"]
        for line in lines:
            ll = line.lower()
            # Use word-boundary check to avoid matching "mit" inside "Smith"
            if any(re.search(r'\b' + re.escape(mk) + r'\b', ll) for mk in markers) and len(line) < 100:
                return line.strip()
        return ""

    def _detect_grad_year(self, text: str) -> int:
        m = re.search(r'(?:graduated|graduation|class of|batch of)\s*[:\-]?\s*(20\d{2}|19\d{2})', text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        years = re.findall(r'\b(20\d{2})\b', text)
        if years:
            return min(int(y) for y in years)
        return 0

    def _detect_gpa(self, text: str) -> str:
        patterns = [
            r'(?:gpa|cgpa|grade point)[:\s]+(\d+\.\d+)\s*/\s*(\d+\.?\d*)',
            r'(?:gpa|cgpa)[:\s]+(\d+\.\d+)',
            r'(\d+\.\d+)\s*/\s*(4\.0|5\.0|10\.0|10)',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                if m.lastindex >= 2:
                    return f"{m.group(1)} / {m.group(2)}"
                return m.group(1)
        return ""

    # ════════════════════════════════════════════════════════
    #  PROFESSIONAL PROFILE
    # ════════════════════════════════════════════════════════

    def _estimate_years(self, text: str) -> int:
        # 1. Explicit "N years of experience" statements take highest priority
        explicit_patterns = [
            r'(\d{1,2})\+?\s*years?\s+(?:of\s+)?(?:experience|exp\b)',
            r'(?:experience|employment)\s*[:\(]\s*(\d{1,2})\+?\s*years?',
            r'total\s+(?:work\s+|professional\s+)?experience[:\s]+(\d{1,2})',
            r'(\d{1,2})\+?\s*years?\s+(?:of\s+)?(?:work|professional|industry)',
            r'PROFESSIONAL\s+EXPERIENCE\s*[\(\[]\s*(\d{1,2})\s*(?:YEARS?|YRS?)',
        ]
        for pat in explicit_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return min(int(m.group(1)), 35)

        # 2. Isolate the professional experience section to exclude education date ranges
        exp_section = text
        exp_start = re.search(
            r'\n\s*(?:PROFESSIONAL\s+EXPERIENCE|WORK\s+EXPERIENCE|EMPLOYMENT\s+HISTORY|CAREER\s+HISTORY|EXPERIENCE)\b',
            text, re.IGNORECASE
        )
        if exp_start:
            exp_text = text[exp_start.start():]
            edu_stop = re.search(
                r'\n\s*(?:ACADEMIC|EDUCATION|EDUCATIONAL|QUALIFICATIONS?|SKILLS?|CERTIFICATIONS?|AWARDS?|REFERENCES?)\b',
                exp_text, re.IGNORECASE
            )
            exp_section = exp_text[:edu_stop.start()] if edu_stop else exp_text

        # 3. Calculate from date ranges within the experience section only
        spans = re.findall(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?(20\d{2}|19\d{2})'
            r'\s*[-–—]\s*'
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?(20\d{2}|19\d{2}|[Pp]resent|[Cc]urrent|[Nn]ow)',
            exp_section
        )
        if not spans:
            spans_simple = re.findall(
                r'(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|19\d{2}|[Pp]resent|[Cc]urrent)',
                exp_section
            )
            spans = [('', s, '', e) for s, e in spans_simple]

        year_pairs = []
        for _m1, start, _m2, end in spans:
            try:
                s = int(start)
                e = 2026 if str(end).lower() in ('present', 'current', 'now') else int(end)
                if 1980 <= s <= 2026 and s <= e:
                    year_pairs.append((s, e))
            except ValueError:
                pass

        if year_pairs:
            year_pairs.sort()
            merged_years = set()
            for s, e in year_pairs:
                merged_years.update(range(s, e + 1))
            return min(max(len(merged_years) - 1, 0), 35)
        return 0

    def _extract_companies(self, lines: list, lower: str) -> list:
        companies = []
        indicators = ["inc", "ltd", "llc", "corp", "pvt", "co.", "technologies",
                      "solutions", "systems", "software", "services", "group",
                      "consulting", "digital", "labs", "studio", "ventures"]
        for line in lines:
            l = line.lower()
            if any(ind in l for ind in indicators) and len(line) < 80:
                # Make sure it's not a section header
                if not any(sec in l for sec in ["experience", "education", "skills"]):
                    companies.append(line.strip())
        return list(dict.fromkeys(companies))[:6]  # deduplicate, max 6

    def _extract_job_title(self, lines: list, lower: str) -> str:
        title_keywords = [
            "engineer", "developer", "architect", "scientist", "analyst",
            "manager", "director", "designer", "consultant", "lead",
            "specialist", "officer", "executive", "intern", "associate",
        ]
        section_headers = {
            "executive summary", "professional summary", "career summary",
            "executive profile", "professional profile", "career objective",
            "professional experience", "work experience", "employment history",
            "key skills", "core skills", "technical skills", "skills summary",
            "academic qualifications", "education", "certifications",
            "awards", "references", "achievements", "projects",
        }
        for line in lines[:20]:
            ll = line.lower().strip()
            if ll in section_headers:
                continue
            if any(kw in ll for kw in title_keywords) and len(line) < 60:
                if not any(sec in ll for sec in ["experience", "education", "skills", "work"]):
                    clean = re.sub(r'^(?:designation|title|position|role)\s*:\s*', '', line.strip(), flags=re.IGNORECASE)
                    return clean.strip()
        return ""

    def _detect_seniority(self, lower: str, years_exp: int, job_title: str) -> str:
        title_lower = job_title.lower()
        for level, patterns in SENIORITY_MAP.items():
            if any(p in lower[:500] or p in title_lower for p in patterns):
                return level.title()

        # Fallback: use years of experience
        if years_exp >= 12: return "Executive"
        if years_exp >= 8:  return "Senior"
        if years_exp >= 4:  return "Mid-Level"
        if years_exp >= 1:  return "Junior"
        return "Entry Level"

    def _detect_archetype(self, skills_by_cat: dict, lower: str) -> str:
        scores = {}
        for archetype, weights in ARCHETYPE_WEIGHTS.items():
            score = 0.0
            for cat, weight in weights.items():
                count = len(skills_by_cat.get(cat, []))
                score += count * weight
            if score > 0:
                scores[archetype] = score
        if not scores:
            return "Software Professional"
        return max(scores, key=scores.get)

    # ════════════════════════════════════════════════════════
    #  QUALITY METRICS
    # ════════════════════════════════════════════════════════

    def _detect_sections(self, lower: str) -> set:
        found = set()
        for section, keywords in SECTION_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    found.add(section)
                    break
        return found

    def _count_bullets(self, lines: list) -> int:
        bullet_pat = re.compile(r'^[•‣◦⁃∙\-\*\+•▸►▶]\s')
        return sum(1 for l in lines if bullet_pat.match(l))

    def _count_verbs(self, lower: str, verbs: list) -> int:
        count = 0
        for v in verbs:
            if re.search(r'\b' + v + r'\b', lower):
                count += 1
        return count

    def _count_quantified(self, text: str) -> int:
        patterns = [
            r'\d+\s*%',
            r'\$\s*[\d,]+(?:\.\d+)?(?:\s*[kmb]illion|\s*[kmb])?',
            r'£\s*[\d,]+', r'€\s*[\d,]+',
            r'\d+[xX]\s+(?:faster|improvement|increase|reduction)',
            r'(?:increased?|reduced?|improved?|decreased?|grew?|cut|saved?)\s+(?:by\s+)?\d+',
            r'\d+(?:,\d{3})+\s+(?:users|customers|records|transactions|requests)',
            r'\d+\s*(?:users|customers|clients|employees|engineers|members|developers)',
            r'\d+\s*(?:projects?|products?|features?|services?|apps?|systems?)',
            r'\d+\s*(?:million|billion|thousand|k\b)',
            r'\d+\+?\s*years?\s+(?:of\s+)?(?:experience|exp)',
            r'\d+\s*(?:ms|milliseconds?|seconds?)\s+(?:latency|response)',
        ]
        matches = set()
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                matches.add(m.group(0).lower().strip())
        return len(matches)

    def _count_weak_language(self, lower: str) -> int:
        return sum(1 for phrase in WEAK_LANGUAGE if phrase in lower)

    def _analyze_career_timeline(self, text: str) -> tuple:
        """Returns (max_gap_months, job_roles list)."""
        # Extract all year ranges
        roles_raw = re.findall(
            r'([A-Za-z][A-Za-z\s/,\-]{5,60}?)\s*'
            r'(?:at|@|,|\|)?\s*'
            r'([A-Za-z][A-Za-z\s,\.]+?)?\s*'
            r'\(?\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?'
            r'(20\d{2}|19\d{2})\s*[-–—]\s*'
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?'
            r'(20\d{2}|19\d{2}|[Pp]resent|[Cc]urrent)\s*\)?',
            text
        )

        # Simpler: just extract year spans and compute gaps
        spans = re.findall(
            r'(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|19\d{2}|[Pp]resent|[Cc]urrent)',
            text
        )

        year_pairs = []
        for start, end in spans:
            try:
                s = int(start)
                e = 2025 if end.lower() in ('present', 'current') else int(end)
                if 1980 <= s <= 2025:
                    year_pairs.append((s, e))
            except ValueError:
                pass

        max_gap = 0
        if len(year_pairs) >= 2:
            year_pairs.sort(key=lambda x: x[0])
            for i in range(1, len(year_pairs)):
                prev_end   = year_pairs[i-1][1]
                curr_start = year_pairs[i][0]
                gap_years  = curr_start - prev_end
                if gap_years > 0:
                    max_gap = max(max_gap, gap_years * 12)

        job_roles = []
        for s, e in year_pairs:
            job_roles.append({"start": s, "end": e, "duration": e - s})

        return max_gap, job_roles

    def _detect_progression(self, job_roles: list) -> str:
        if len(job_roles) < 2:
            return "unclear"
        durations = [r["duration"] for r in job_roles]
        avg = sum(durations) / len(durations)
        # Too short average = job hopper signal
        if avg < 1:
            return "unstable"
        return "progressive"

    # ════════════════════════════════════════════════════════
    #  MULTI-DIMENSIONAL SCORING (each 0-100)
    # ════════════════════════════════════════════════════════

    def _score_technical(self, a: CVAnalysis) -> int:
        total = sum(len(v) for v in a.skills_by_category.values())
        cats  = len(a.skills_by_category)
        certs = len(a.certifications)

        score  = min(total * 3.5, 55)   # depth  (max 55)
        score += min(cats  * 6,   30)   # breadth (max 30)
        score += min(certs * 7.5, 15)   # certs   (max 15)
        return min(100, round(score))

    def _score_experience(self, a: CVAnalysis) -> int:
        score = 0.0
        # Years
        if a.years_exp >= 12: score += 45
        elif a.years_exp >= 8: score += 38
        elif a.years_exp >= 5: score += 30
        elif a.years_exp >= 3: score += 20
        elif a.years_exp >= 1: score += 12
        # Seniority
        seniority_pts = {"Executive":25,"Director":22,"Principal":20,
                         "Senior":16,"Mid-Level":10,"Junior":5,"Entry Level":2}
        score += seniority_pts.get(a.seniority, 5)
        # Progression
        if a.career_progression == "progressive": score += 10
        elif a.career_progression == "unstable":  score -= 5
        # Gap penalty
        if a.career_gap_months > 12: score -= 8
        elif a.career_gap_months > 6: score -= 4
        # Multiple companies = diverse experience
        score += min(len(a.companies) * 3, 15)
        return max(0, min(100, round(score)))

    def _score_education(self, a: CVAnalysis) -> int:
        score = {0: 0, 1: 20, 2: 35, 3: 55, 4: 75, 5: 90}.get(a.degree_level, 0)
        if a.institution: score += 5
        if a.gpa:
            try:
                val = float(re.sub(r'/.*', '', a.gpa).strip())
                if val >= 3.5 or val >= 8.5:   score += 8
                elif val >= 3.0 or val >= 7.0: score += 4
            except ValueError:
                pass
        if a.certifications: score += min(len(a.certifications) * 3, 10)
        return min(100, round(score))

    def _score_presentation(self, a: CVAnalysis) -> int:
        score = 0.0
        # Section completeness
        key_sections = {"summary", "experience", "education", "skills", "projects"}
        present = key_sections & set(a.sections_found)
        score += len(present) * 10              # max 50

        # Length
        if 450 <= a.word_count <= 1200:  score += 20
        elif 300 <= a.word_count < 450:  score += 12
        elif a.word_count > 1200:        score += 10
        else:                            score += 4

        # Bullet usage
        if a.bullet_count >= 15:  score += 15
        elif a.bullet_count >= 8: score += 10
        elif a.bullet_count >= 3: score += 5

        # Contact completeness
        if a.email != "Not Provided": score += 5
        if a.phone != "Not Provided": score += 5
        if a.linkedin:                score += 3
        if a.github:                  score += 2

        return min(100, round(score))

    def _score_impact(self, a: CVAnalysis) -> int:
        score = 0.0
        # Strong verbs
        score += min(a.strong_verb_count  * 7,  35)  # max 35
        # Standard verbs
        score += min(a.action_verb_count  * 2,  20)  # max 20
        # Quantified achievements
        score += min(a.quant_count        * 8,  40)  # max 40
        # Penalty for weak language
        score -= a.weak_lang_count * 5
        return max(0, min(100, round(score)))

    def _score_ats(self, a: CVAnalysis) -> int:
        score = 0.0
        # Contact info (ATS needs this)
        if a.email != "Not Provided": score += 10
        if a.phone != "Not Provided": score += 8

        # Standard section headers
        ats_sections = {"experience", "education", "skills"}
        score += len(ats_sections & set(a.sections_found)) * 10  # max 30

        # Keyword richness
        total_skills = sum(len(v) for v in a.skills_by_category.values())
        score += min(total_skills * 2, 25)  # max 25

        # Word count in ATS sweet spot
        if 400 <= a.word_count <= 1000: score += 10
        elif a.word_count >= 200:       score += 5

        # No certifications = less ATS signal
        if a.certifications: score += min(len(a.certifications) * 3, 10)

        # Penalise very short
        if a.word_count < 150: score -= 20

        return max(0, min(100, round(score)))

    def _score_completeness(self, a: CVAnalysis) -> int:
        checklist = [
            a.name != "Unknown Candidate",
            a.email != "Not Provided",
            a.phone != "Not Provided",
            "summary"     in a.sections_found,
            "experience"  in a.sections_found,
            "education"   in a.sections_found,
            "skills"      in a.sections_found,
            "projects"    in a.sections_found,
            bool(a.linkedin or a.github),
            "achievements" in a.sections_found or bool(a.certifications),
        ]
        return round(sum(checklist) / len(checklist) * 100)

    def _compute_overall(self, a: CVAnalysis) -> int:
        weighted = (
            a.technical_score    * 0.25 +
            a.experience_score   * 0.25 +
            a.education_score    * 0.15 +
            a.presentation_score * 0.15 +
            a.impact_score       * 0.20
        )
        return max(1, min(10, round(weighted / 10)))

    # ════════════════════════════════════════════════════════
    #  RED FLAGS & RECOMMENDATIONS
    # ════════════════════════════════════════════════════════

    def _find_red_flags(self, a: CVAnalysis) -> list:
        flags = []

        if a.word_count < 200:
            flags.append("Resume is extremely short (<200 words) — likely missing critical sections")
        if a.word_count > 1500:
            flags.append("Resume may be too long (>1500 words) — consider trimming to 1-2 pages")

        if a.email == "Not Provided":
            flags.append("No email address found — critical contact information is missing")
        if a.phone == "Not Provided":
            flags.append("No phone number found — consider adding contact details")

        if "experience" not in a.sections_found:
            flags.append("No work experience section detected — this is a critical omission")
        if "education" not in a.sections_found:
            flags.append("No education section found")
        if "skills" not in a.sections_found:
            flags.append("No skills section found — makes it very hard for ATS and recruiters to evaluate")

        total_skills = sum(len(v) for v in a.skills_by_category.values())
        if total_skills < 3:
            flags.append("Fewer than 3 technical skills detected — skills section appears weak or missing")

        if a.quant_count == 0:
            flags.append("Zero quantified achievements detected — resume lacks measurable evidence of impact")

        if a.action_verb_count < 3:
            flags.append("Very few action verbs used — resume reads passively and weakly")

        if a.weak_lang_count >= 3:
            flags.append(f"Passive/weak phrasing detected ({a.weak_lang_count} instances) — replace with action verbs")

        if a.career_gap_months > 12:
            flags.append(f"Potential career gap of {a.career_gap_months // 12}+ year(s) detected between roles")
        elif a.career_gap_months > 6:
            flags.append(f"Possible {a.career_gap_months}-month career gap detected — consider addressing it")

        if a.career_progression == "unstable":
            flags.append("Short average tenure at companies detected — may raise job-hopping concerns")

        if a.degree_level == 0 and a.years_exp < 3:
            flags.append("No formal education or significant experience detected — profile appears very thin")

        return flags

    def _generate_recommendations(self, a: CVAnalysis) -> list:
        recs = []

        if a.quant_count < 3:
            recs.append(
                "Add measurable achievements to every role: e.g. 'Reduced API latency by 45%', "
                "'Managed a team of 6 engineers', 'Grew user base from 10k to 80k'"
            )
        if a.action_verb_count < 5:
            recs.append(
                "Start each bullet point with a strong action verb: Architected, Deployed, Optimised, "
                "Spearheaded, Engineered, Automated, Mentored"
            )
        if "summary" not in a.sections_found:
            recs.append(
                "Add a 3-4 sentence Professional Summary at the top highlighting your seniority, "
                "key skills, and career goal"
            )
        if "projects" not in a.sections_found:
            recs.append(
                "Add a Projects section with 2-3 personal or open-source projects including the "
                "tech stack used and a link to the code"
            )
        if not a.linkedin:
            recs.append("Add your LinkedIn profile URL — most recruiters check LinkedIn as a first step")
        if not a.github and any(c in a.skills_by_category for c in
                                 ["Programming Languages", "Web & Frontend", "Backend & Frameworks"]):
            recs.append("Add your GitHub profile — it provides evidence of your coding ability and activity")

        total_skills = sum(len(v) for v in a.skills_by_category.values())
        if total_skills < 8:
            recs.append(
                "Expand your skills section — list all frameworks, tools, libraries, and platforms you "
                "have worked with, even if briefly"
            )
        if not a.certifications:
            recs.append(
                "Earn and list at least one industry certification relevant to your role "
                "(e.g. AWS, Azure, GCP, PMP, Scrum Master, or a vendor-specific cert)"
            )
        if a.word_count < 300:
            recs.append(
                "Your resume is too short. Each job role should have 3-5 bullet points describing "
                "your contributions, tech used, and results achieved"
            )
        if a.weak_lang_count >= 2:
            recs.append(
                "Replace passive phrases ('responsible for', 'worked on') with active ones "
                "('Built', 'Owned', 'Drove', 'Delivered')"
            )
        if a.degree_level < 3 and a.years_exp < 5:
            recs.append(
                "Consider pursuing an online degree, bootcamp, or professional certificate to "
                "strengthen your academic credentials"
            )

        return recs[:7]

    # ════════════════════════════════════════════════════════
    #  NARRATIVE GENERATION
    # ════════════════════════════════════════════════════════

    def _generate_insights(self, a: CVAnalysis) -> tuple:
        pros, cons = [], []
        total_skills = sum(len(v) for v in a.skills_by_category.values())

        # Contact
        if a.email != "Not Provided" and a.phone != "Not Provided":
            pros.append("Full contact details present (email & phone)")
        else:
            if a.email == "Not Provided": cons.append("Missing email address")
            if a.phone == "Not Provided": cons.append("Missing phone number")

        # Skills
        if total_skills >= 20:
            pros.append(f"Comprehensive technical arsenal: {total_skills} skills across {len(a.skills_by_category)} domains")
        elif total_skills >= 10:
            pros.append(f"Good technical breadth with {total_skills} skills in {len(a.skills_by_category)} categories")
        elif total_skills >= 4:
            cons.append(f"Limited technical skill set ({total_skills} skills detected) — needs expansion")
        else:
            cons.append("Very few detectable technical skills — skills section may be poorly formatted")

        # Notable skill categories
        for cat in ["Data & AI / ML", "Cloud & DevOps", "Security", "Blockchain & Web3"]:
            if cat in a.skills_by_category:
                top = ", ".join(a.skills_by_category[cat][:4])
                pros.append(f"{cat} expertise: {top}")

        # Certifications
        if len(a.certifications) >= 3:
            pros.append(f"Strong certification portfolio: {', '.join(a.certifications[:3])}")
        elif a.certifications:
            pros.append(f"Holds {len(a.certifications)} professional certification(s)")
        else:
            cons.append("No recognised certifications found — consider earning one")

        # Education
        edu_labels = {5:"PhD level",4:"Master's/MBA",3:"Bachelor's degree",2:"Associate degree",1:"Diploma/Certificate"}
        if a.degree_level >= 3:
            pros.append(f"{edu_labels.get(a.degree_level, 'Formal')} qualification"
                        + (f" from {a.institution}" if a.institution else ""))
        elif a.degree_level > 0:
            pros.append(f"Formal qualification: {edu_labels.get(a.degree_level, '')}")
        else:
            cons.append("No formal academic qualification detected")

        # Experience
        if a.years_exp >= 8:
            pros.append(f"~{a.years_exp} years of experience — clearly a {a.seniority.lower()} professional")
        elif a.years_exp >= 4:
            pros.append(f"~{a.years_exp} years of solid mid-level experience")
        elif a.years_exp >= 1:
            cons.append(f"~{a.years_exp} year(s) of experience — junior/early career profile")
        else:
            cons.append("Experience duration unclear — add date ranges to all roles")

        # Impact
        if a.quant_count >= 5:
            pros.append(f"Excellent quantified impact ({a.quant_count} measurable achievements)")
        elif a.quant_count >= 2:
            pros.append(f"{a.quant_count} quantified achievements strengthen credibility")
        else:
            cons.append("No quantified achievements — add metrics to every bullet point")

        if a.strong_verb_count >= 5:
            pros.append(f"Strong, active writing style ({a.strong_verb_count} power verbs used)")
        elif a.action_verb_count < 4:
            cons.append("Passive resume language — rewrite with action verbs")

        # Soft skills
        if len(a.soft_skills) >= 5:
            pros.append(f"Well-rounded soft skills profile: {', '.join(a.soft_skills[:4])}")

        # Online presence
        if a.linkedin and a.github:
            pros.append("Both LinkedIn and GitHub profiles are linked")
        elif a.linkedin:
            pros.append("LinkedIn profile is included")
        elif a.github:
            pros.append("GitHub profile is linked — evidence of active coding work")
        else:
            cons.append("No LinkedIn or GitHub profile linked")

        # Red flags
        if a.career_gap_months > 12:
            cons.append(f"Significant career gap detected (~{a.career_gap_months // 12} year(s))")
        if a.career_progression == "unstable":
            cons.append("Short tenure pattern across multiple roles may raise concerns")
        if a.weak_lang_count >= 3:
            cons.append(f"Passive phrasing used {a.weak_lang_count}x — weakens professional image")

        return pros[:8], cons[:7]

    def _generate_verdict(self, a: CVAnalysis) -> str:
        total_skills = sum(len(v) for v in a.skills_by_category.values())

        # Tier language
        seniority_desc = {
            "Executive":  "an executive-level professional",
            "Director":   "a director-level professional",
            "Principal":  "a principal / staff-level engineer",
            "Senior":     "a senior-level professional",
            "Mid-Level":  "a mid-level professional",
            "Junior":     "a junior/early-career professional",
            "Entry Level":"an entry-level candidate",
        }.get(a.seniority, "a professional")

        exp_note = (
            f"approximately {a.years_exp} years of experience" if a.years_exp > 0
            else "an unspecified experience level"
        )
        edu_note = {
            5:"a PhD/doctorate",4:"a master's degree or MBA",3:"a bachelor's degree",
            2:"an associate degree",1:"a diploma or certificate",0:"no formal qualification"
        }.get(a.degree_level, "an unspecified qualification")

        archetype_note = f"best aligned with the {a.archetype} role archetype"

        skill_note = (
            f"demonstrates {total_skills} technical skills across {len(a.skills_by_category)} categories"
            if total_skills > 0 else "shows limited detectable technical skills"
        )

        cert_note = (
            f" holds {len(a.certifications)} professional certification(s) including {a.certifications[0]}"
            if a.certifications else " has no listed certifications"
        )

        impact_note = (
            f"The resume contains {a.quant_count} quantified achievement(s) and {a.action_verb_count} "
            f"action verbs, giving it a {'strong' if a.impact_score >= 60 else 'moderate' if a.impact_score >= 35 else 'weak'} impact tone."
        )

        completeness_note = (
            f"Profile completeness is {a.completeness_pct}% across 10 key resume criteria."
        )

        tone = {
            range(9, 11): "This is an exceptional candidate profile that stands out strongly.",
            range(7, 9):  "This is a strong candidate worth shortlisting.",
            range(5, 7):  "This is a competent candidate with room for improvement.",
            range(3, 5):  "This profile needs significant work before submission.",
            range(0, 3):  "This resume is unlikely to pass ATS or recruiter screening.",
        }
        tone_str = next((v for k, v in tone.items() if a.rating in k), "")

        return (
            f"{a.name} presents as {seniority_desc} with {exp_note}, holding {edu_note}, and is {archetype_note}. "
            f"The candidate {skill_note} and{cert_note}. "
            f"{impact_note} "
            f"{completeness_note} "
            f"{tone_str}"
        )


# ════════════════════════════════════════════════════════════
#  PUBLIC API
# ════════════════════════════════════════════════════════════

def parse_cv(text: str) -> dict:
    """
    Parse CV text and return a dict with both core fields (DB-compatible)
    and extended metadata for rich display.
    """
    a = CVParser().parse(text)
    return {
        # Core (stored in DB columns)
        "name":    a.name,
        "email":   a.email,
        "phone":   a.phone,
        "rating":  a.rating,
        "verdict": a.verdict,
        "pros":    a.pros,
        "cons":    a.cons,

        # Extended (stored as JSON in metadata column)
        "metadata": {
            # Identity
            "location": a.location,
            "linkedin": a.linkedin,
            "github":   a.github,
            "website":  a.website,

            # Professional
            "job_title":  a.job_title,
            "seniority":  a.seniority,
            "archetype":  a.archetype,
            "years_exp":  a.years_exp,
            "companies":  a.companies,

            # Skills
            "skills_by_category": a.skills_by_category,
            "top_skills":         a.top_skills,
            "soft_skills":        a.soft_skills,
            "certifications":     a.certifications,
            "languages_spoken":   a.languages_spoken,

            # Education
            "degree_level": a.degree_level,
            "degree_name":  a.degree_name,
            "institution":  a.institution,
            "grad_year":    a.grad_year,
            "gpa":          a.gpa,

            # Scores (0-100)
            "technical_score":    a.technical_score,
            "experience_score":   a.experience_score,
            "education_score":    a.education_score,
            "presentation_score": a.presentation_score,
            "impact_score":       a.impact_score,
            "ats_score":          a.ats_score,
            "completeness_pct":   a.completeness_pct,

            # Quality
            "word_count":       a.word_count,
            "bullet_count":     a.bullet_count,
            "action_verb_count":a.action_verb_count,
            "strong_verb_count":a.strong_verb_count,
            "quant_count":      a.quant_count,
            "sections_found":   a.sections_found,

            # Career
            "career_gap_months":  a.career_gap_months,
            "career_progression": a.career_progression,

            # Guidance
            "red_flags":       a.red_flags,
            "recommendations": a.recommendations,
        }
    }
