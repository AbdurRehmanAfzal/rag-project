export interface Project {
  id: string;
  category: string;
  title: string;
  thumbnail: string;
  fallbackThumbnail?: string;
  description: string;
  technologies: string[];
  links: { label: string; url: string }[];
  screenshots: string[];
  fallbackScreenshots?: string[];
}

// Decorative topic thumbnails (Unsplash).
const IMG = {
  code: "https://images.unsplash.com/photo-1555949963-aa79dcee981c?q=80&w=900&auto=format&fit=crop",
  mail: "https://images.unsplash.com/photo-1596526131083-e8c633c948d2?q=80&w=900&auto=format&fit=crop",
  robot: "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?q=80&w=900&auto=format&fit=crop",
  docs: "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?q=80&w=900&auto=format&fit=crop",
  car: "https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?q=80&w=900&auto=format&fit=crop",
  social: "https://images.unsplash.com/photo-1611162616475-46b635cb6868?q=80&w=900&auto=format&fit=crop",
  analytics: "https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?q=80&w=900&auto=format&fit=crop",
};

export const projectsData: Project[] = [
  {
    id: "13",
    category: "Agentic AI / Vision-Language Models",
    title: "AI Annotation: VLM-Powered Dashcam Safety Event Pipeline",
    thumbnail: IMG.car,
    description:
      "A production AI annotation service for a fleet-safety telematics platform that automatically reviews and labels dashcam safety events (crashes, hard braking, seat-belt violations, and road- and driver-facing camera obstruction), replacing slow manual review with consistent, explainable AI decisions at scale. Events arrive over AWS SQS and are routed to a dedicated LangGraph workflow per event type, where Triton-served computer vision models and multi-step Vision-Language Model (VLM) reasoning combine into structured decision labels, tuned by Statsig dynamic thresholds and false-positive rejection logic. My role: I owned the ML and AI side end to end: designing the AI annotation pipelines, building the LangChain/LangGraph agentic workflows and VLM prompt and decision logic, integrating the ML models (Triton inference, OpenRouter LLM/VLM APIs, Snowflake data), and the false-positive rejection and threshold tuning that keep labels accurate in production. The service ships as a containerised Python 3.12 app on Kubernetes across US, EU, and Canada with ArgoCD GitOps, Terraform, Datadog observability, and automated GitHub Actions CI/CD.",
    technologies: ["Python 3.12", "LangGraph", "LangChain", "Vision-Language Models", "Computer Vision", "OpenRouter", "NVIDIA Triton", "Prompt Engineering", "AWS SQS", "Snowflake", "Statsig", "Docker", "Kubernetes", "ArgoCD", "Terraform", "Datadog", "GitHub Actions"],
    links: [],
    screenshots: [],
  },
  {
    id: "14",
    category: "Voice AI / Telephony",
    title: "Mojeeb Agent: AI Voice Concierge on Hotel Phone Systems",
    thumbnail: IMG.robot,
    description:
      "Voice channel for Mojeeb Agent, a multi-tenant, white-labelled AI agent platform for the Saudi market. A hotel guest presses one button (800) on the room phone and talks to an AI concierge through the hotel's own PBX, with no telecom carrier, new number or SIM. I built the LiveKit SIP voice agent (Deepgram speech-to-text and text-to-speech, Groq LLM, Silero VAD and turn detection) and integrated it with a Yeastar PBX over a peer SIP trunk: the agent knows the caller's room automatically, transfers the call to reception via SIP REFER in about 0.6 s, and handles PBX-originated wake-up calls where the agent speaks within 1.3 s. Validated with G.722 HD audio and DTMF, latency across 20 test calls (about 1 s to the first word), and concurrent calls; wrote the technical report, hotel-IT runbook and CTO/CEO briefs, and planned the 3CX PBX extension.",
    technologies: ["Python 3.12", "LiveKit Agents", "LiveKit SIP", "Deepgram STT/TTS", "Groq LLM", "Silero VAD", "SIP / VoIP", "Yeastar PBX", "3CX", "G.722"],
    links: [
      { label: "Website", url: "https://www.mojeebai.com" },
    ],
    screenshots: [],
  },
  {
    id: "15",
    category: "Agentic AI Platform / Frontend",
    title: "Voicecake Agent Platform: Owner Web App (Arabic & English)",
    thumbnail: IMG.code,
    description:
      "The web app for the Voicecake agent platform (white-labelled per customer, e.g. Mojeeb), where business owners and their teams watch and steer their AI agents. As the front-end developer I built conversations, approvals (every action that sends or changes something asks Yes / No / Edit first), activity with step-by-step proof, a department-wise rulebook with history and change proposals, people and scope, and live updates over a server-sent event stream. Fully bilingual Arabic and English with right-to-left layout on every page, contract-first against an OpenAPI spec with generated TypeScript types and a single API client, and five page states (loading, empty, error, no access, live). Shipped as a Next.js 16 static export with unit, component and Playwright end-to-end tests in GitHub Actions CI.",
    technologies: ["Next.js 16", "React 19", "TypeScript", "TailwindCSS 4", "TanStack Query", "Server-Sent Events", "OpenAPI", "i18n / RTL", "Vitest", "Playwright", "GitHub Actions", "Vercel"],
    links: [],
    screenshots: [],
  },
  {
    id: "1",
    category: "RAG / Conversational AI",
    title: "B1 Chatbot: AI Real Estate Assistant",
    thumbnail: IMG.robot,
    description:
      "A production AI real estate assistant using GPT-4, LangChain, ChromaDB, Django, Vercel, and the Telegram Bot API. It combines vector search, custom embeddings, and a proprietary knowledge base with Telegram Bot integration for real-time property enquiries, reducing repetitive agent enquiry handling by 60%.",
    technologies: ["GPT-4", "LangChain", "ChromaDB", "Django", "Vercel", "Telegram Bot API"],
    links: [],
    screenshots: [],
  },
  {
    id: "2",
    category: "Computer Vision / Government",
    title: "AI-Powered EID Document Processing System",
    thumbnail: IMG.docs,
    description:
      "Built for the Hamriyah Free Zone Authority in the UAE, a government client, using Django, YOLOv8, PyTorch, OpenCV, Tesseract OCR, and EasyOCR. Automates extraction of 40+ structured fields from Emirates ID cards, passports, and visa documents through a 6-stage AI pipeline (upload, YOLOv8 detection, region cropping, dual OCR, data cleaning, storage), reducing document processing time from minutes to seconds.",
    technologies: ["Django", "YOLOv8", "PyTorch", "OpenCV", "Tesseract OCR", "EasyOCR"],
    links: [],
    screenshots: [],
  },
  {
    id: "3",
    category: "NLP / Automation",
    title: "AI-Assisted News Intelligence Platform",
    thumbnail: IMG.mail,
    description:
      "Ingests news from multiple RSS sources, filters articles with 30+ categorised keywords, summarises them with GPT-4 using a dynamic prompt templating engine, generates PDF reports, and delivers them by automated email, with a 12-component React dashboard.",
    technologies: ["Node.js", "Express.js", "PostgreSQL", "OpenAI GPT-4", "React", "node-cron"],
    links: [],
    screenshots: [],
  },
  {
    id: "4",
    category: "AdTech / Generative AI",
    title: "AdsGency AI — Ad Content Generation Module",
    thumbnail: IMG.social,
    description:
      "AI features contributed to AdsGency AI, an AI-powered advertising platform serving 150+ businesses with $50M+ in managed ad spend, using FastAPI, Django, DRF, and the OpenAI API. Built an OpenAI-powered ad content generation module alongside Google Ads and Meta Marketing API integrations and backend analytics APIs.",
    technologies: ["FastAPI", "Django", "DRF", "OpenAI API", "Google Ads API", "Meta Marketing API"],
    links: [
      { label: "Platform", url: "https://adsgency.ai" },
    ],
    screenshots: [],
  },
  {
    id: "5",
    category: "Full-Stack Web",
    title: "B1 Properties — Luxury Real Estate Platform",
    thumbnail: IMG.code,
    description:
      "A luxury real estate platform live at b1properties.ae, using Django 5.2, DRF, PostgreSQL, Next.js 16, TypeScript 5, TailwindCSS 4, AWS S3, Nginx, Gunicorn, and PM2. Includes 13+ Django models, 50+ REST API endpoints, 20+ normalised database tables, 15+ Next.js pages, advanced property search with 10+ filter criteria, and an appointment booking system.",
    technologies: ["Django 5.2", "DRF", "PostgreSQL", "Next.js 16", "TypeScript", "TailwindCSS", "AWS S3", "Nginx", "Gunicorn", "PM2"],
    links: [
      { label: "Live Platform", url: "https://b1properties.ae" },
    ],
    screenshots: [],
  },
  {
    id: "6",
    category: "AI / Fintech Tooling",
    title: "EasyKost: AI-Driven Cost Estimation System",
    thumbnail: IMG.analytics,
    description:
      "An AI-driven product cost estimation system using Django, DRF, Firestore, Firebase Storage, and gRPC. Migrated the monolithic system to a microservices architecture and led the database migration from MySQL to Firestore.",
    technologies: ["Django", "DRF", "Firestore", "Firebase Storage", "gRPC"],
    links: [],
    screenshots: [],
  },
  {
    id: "7",
    category: "Geospatial / Web Application",
    title: "VenueGPS: Venue & Events Discovery Platform",
    thumbnail: IMG.docs,
    description:
      "A location-based venue and events discovery platform using Django, DRF, PostgreSQL, Redis, and Google Maps API. Includes multi-role authentication with Facebook OAuth, business listing management, geospatial venue search, and a tiered hashtag monetisation system.",
    technologies: ["Django", "DRF", "PostgreSQL", "Redis", "Google Maps API"],
    links: [
      { label: "Live Platform", url: "https://develop.venuegps.com" },
    ],
    screenshots: [],
  },
  {
    id: "8",
    category: "Supply Chain / Enterprise SaaS",
    title: "Palletfly: B2B Supply Chain & Inventory Platform",
    thumbnail: IMG.analytics,
    description:
      "An enterprise B2B supply chain and inventory management platform using Django 3.2, Django Channels, DRF, Huey, Redis, PostgreSQL, Wagtail CMS, AWS, Docker, and GitHub Actions. Contains 40,000+ lines of Python across 10 Django apps, 91+ ORM models, and 380+ schema migrations, with real-time collaborative editing and an async task engine.",
    technologies: ["Django 3.2", "Django Channels", "DRF", "Huey", "Redis", "PostgreSQL", "Wagtail CMS", "AWS", "Docker", "GitHub Actions"],
    links: [
      { label: "Live Platform", url: "https://dbr.palletfly.com" },
    ],
    screenshots: [],
  },
  {
    id: "9",
    category: "Fintech / Cloud-Native",
    title: "WMC Pricing Intelligence Platform",
    thumbnail: IMG.analytics,
    description:
      "A cloud-native fintech mortgage comparison engine using Django 5.0.2, Google BigQuery, Redis, Docker, and Kubernetes on Google Kubernetes Engine (GKE). Queries live UK mortgage pricing data with 10+ filter parameters and uses Redis caching to reduce BigQuery costs, with fully automated GitHub Actions CI/CD deployment to GKE.",
    technologies: ["Django 5.0.2", "Google BigQuery", "Redis", "Docker", "Kubernetes", "GKE", "GitHub Actions"],
    links: [],
    screenshots: [],
  },
  {
    id: "10",
    category: "Workforce Management SaaS",
    title: "TimeKeepers (WorkFly): Multi-Tenant Workforce SaaS",
    thumbnail: IMG.social,
    description:
      "A multi-tenant workforce management SaaS at workfly.app, using Django 4.0, DRF, Django Channels, WebSockets, Celery, RabbitMQ, Redis, PostgreSQL, Angular 15, and Kotlin for Android. Serves security guard companies with 8 Django apps, 5 user role types, 64+ Angular components, real-time GPS tracking, and geofenced time-clock functionality.",
    technologies: ["Django 4.0", "DRF", "Django Channels", "WebSockets", "Celery", "RabbitMQ", "Redis", "PostgreSQL", "Angular 15", "Kotlin"],
    links: [
      { label: "Live Platform", url: "https://workfly.app" },
    ],
    screenshots: [],
  },
  {
    id: "11",
    category: "Real-Time Dashboard",
    title: "TRIXI TAXI: Ride-Sharing Admin Dashboard",
    thumbnail: IMG.car,
    description:
      "A real-time ride-sharing admin dashboard using React 18, Redux Toolkit, Socket.io, Google Maps API, and Material-UI. A multi-role admin panel for taxi operations covering drivers, vehicles, rides, companies, and billing, with real-time GPS tracking and automated fare calculation.",
    technologies: ["React 18", "Redux Toolkit", "Socket.io", "Google Maps API", "Material-UI"],
    links: [],
    screenshots: [],
  },
  {
    id: "12",
    category: "Telecom / Data Engineering",
    title: "Ericsson & Huawei LTE/WCDMA GPL Audit System",
    thumbnail: IMG.code,
    description:
      "A telecom network configuration auditing system using Python, PostgreSQL, Apache Kafka, pandas, and Jupyter Notebooks. Automates Golden Parameter List auditing across Ericsson and Huawei 4G and 3G networks, reducing manual audit time by 80%.",
    technologies: ["Python", "PostgreSQL", "Apache Kafka", "pandas", "Jupyter"],
    links: [],
    screenshots: [],
  },
  {
    id: "16",
    category: "RAG / AI Search (In Development)",
    title: "Nightlife.net AI Search Assistant (In Development)",
    thumbnail: IMG.social,
    description:
      "Currently in development: an AI search assistant for nightlife.net, a US nightlife and entertainment portal and business directory (nightclubs, bars, restaurants, hotels, concerts and events). Instead of clicking filters, users ask in plain language, for example \"a rooftop bar in Miami with live Latin music this Saturday\", and get grounded answers on the site's own pages. Designed as a separate FastAPI service that never modifies the existing product: hybrid retrieval with pgvector semantic search plus Postgres trigram keyword search, hard SQL filters for city, date and category extracted from the query, GPT-4o-mini answers grounded only in retrieved listings, Redis caching, a nightly sync job that re-embeds the catalogue from the existing GraphQL/PostgreSQL data into its own index table, and query and gap logging for the content team.",
    technologies: ["FastAPI", "Python", "OpenAI GPT-4o-mini", "pgvector", "PostgreSQL (pg_trgm)", "Hybrid Search", "Redis", "GraphQL", "Next.js"],
    links: [
      { label: "Client Site", url: "https://nightlife.net" },
    ],
    screenshots: [],
  },
];
