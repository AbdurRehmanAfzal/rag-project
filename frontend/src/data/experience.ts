export interface Experience {
  id: string;
  period: string;
  company: string;
  role: string;
  startMonth: string;
  endMonth: string;
  ongoing: boolean;
  bullets: string[];
  certificate?: string;
}

export const experienceData: Experience[] = [
  {
    id: "1",
    period: "Jan 2025-Present",
    company: "B1 Properties · Dubai, UAE",
    role: "Full-Stack Python Developer",
    startMonth: "Jan 2025",
    endMonth: "Present",
    ongoing: true,
    bullets: [
      "Designed and deployed a LangChain + RAG (ChromaDB) real estate chatbot that increased client lead qualification rate by 60%, plus an AI Property Valuation System using GPT-4.",
      "Built an n8n GPT-4 automation pipeline that cut daily manual reporting effort by 70%.",
      "Delivered the production luxury real estate platform b1properties.ae: 100+ active property listings, 50+ REST API endpoints, 13 Django ORM models, and 20+ database tables.",
      "Eliminated all N+1 query incidents for a 30% API performance improvement, and achieved zero production downtime through a hardened Gunicorn, Nginx, PM2, and SSL/TLS infrastructure stack.",
    ],
  },
  {
    id: "2",
    period: "2024-2025",
    company: "Aircod Technologies · Lahore, Pakistan",
    role: "Senior Python Backend & AI Developer",
    startMonth: "2024",
    endMonth: "2025",
    ongoing: false,
    bullets: [
      "Integrated LangChain, CrewAI, and the OpenAI API to build an LLM-powered intelligent document triage system, cutting document processing turnaround time by ~70%.",
      "Contributed backend and AI features to AdsGency AI, a funded AI advertising platform with $50M+ in managed ad spend, including an OpenAI-powered ad content generation module.",
      "Reduced cloud infrastructure costs by 30% by migrating monolithic Django applications to AWS-hosted FastAPI microservices.",
      "Improved API throughput by 35% with Docker and GitHub Actions CI/CD pipelines.",
    ],
  },
  {
    id: "3",
    period: "2023-2024",
    company: "Synares Systems · Lahore, Pakistan",
    role: "Senior Software Engineer II / Backend Team Lead",
    startMonth: "2023",
    endMonth: "2024",
    ongoing: false,
    bullets: [
      "Led development of TimeKeepers/WorkFly (workfly.app), a multi-tenant SaaS spanning 8 Django apps, 5 user role types, 64+ Angular components, and a Kotlin Android app, eliminating 50% of workforce admin overhead.",
      "Delivered sub-100ms real-time response latency using Django Channels, WebSockets, and Redis pub/sub — a ~200x improvement over the previous polling system.",
      "Built a GPS-based geofencing time-clock system and led a team of 5 backend engineers, introducing Black, pre-commit hooks, and PyTest coverage standards.",
    ],
  },
  {
    id: "4",
    period: "2022-2023",
    company: "Merik Solutions · Islamabad, Pakistan",
    role: "Full-Stack Python Developer",
    startMonth: "2022",
    endMonth: "2023",
    ongoing: false,
    bullets: [
      "Reduced production bug rate by 30% by introducing PyTest and UnitTest suites and establishing Test-Driven Development as the team standard.",
      "Delivered Wagtail CMS platforms and DRF API layers, plus automated operational dashboards that cut client reporting turnaround from days to minutes.",
    ],
  },
  {
    id: "5",
    period: "2021-2022",
    company: "Viral Square · Lahore, Pakistan",
    role: "Python Developer",
    startMonth: "2021",
    endMonth: "2022",
    ongoing: false,
    bullets: [
      "Built and scaled Palletfly (dbr.palletfly.com) to 40,000+ lines of production Python across 10 Django apps, 91+ ORM models, and 380+ schema migrations, managing B2B supply chains for clients handling 10,000+ product SKUs.",
      "Implemented a real-time collaboration engine with Django Channels, WebSockets, and Redis.",
      "Reduced bulk data operation time by ~90% using a Huey + Redis async task engine.",
    ],
  },
  {
    id: "6",
    period: "2018-2021",
    company: "UEnergy Solar · Huddersfield, UK (Remote)",
    role: "Software Engineer",
    startMonth: "2018",
    endMonth: "2021",
    ongoing: false,
    bullets: [
      "Engineered and maintained two production platforms (uenergysolar.co.uk and uenergysolar.com) for a UK enterprise renewable energy company serving 20+ named enterprise clients including BP, Shell, NHS, Sainsbury's, and ASDA.",
      "Built a Django + DRF + PostgreSQL CRM and quoting system that accelerated sales proposal generation by ~60%, an invoicing and billing module, and an energy monitoring and analytics dashboard with Chart.js visualisations.",
    ],
  },
  {
    id: "7",
    period: "2018-2021",
    company: "University of Central Punjab (UCP) · Lahore, Pakistan",
    role: "Part-Time CS Instructor",
    startMonth: "2018",
    endMonth: "2021",
    ongoing: false,
    bullets: [
      "Taught 200+ undergraduate students across 7 Computer Science courses over 3 academic years, including OOP, Data Structures & Algorithms, Operating Systems, Networks, and Programming Fundamentals.",
    ],
  },
  {
    id: "8",
    period: "2015-2020",
    company: "SoftTechPanel (Co-Founder) & Somarnovative Labs",
    role: "Co-Founder / 3D Graphic Designer",
    startMonth: "2015",
    endMonth: "2020",
    ongoing: false,
    bullets: [
      "Co-founded SoftTechPanel (2015-2020), working on web development, customer service, complaint management, order fulfillment, and SEO.",
      "Earlier worked as a 3D Graphic Designer at Somarnovative Labs (2016), designing 3D models for games.",
    ],
  },
];
