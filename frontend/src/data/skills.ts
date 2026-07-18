export interface SkillCategory {
  title: string;
  description: string;
  icon: string;
  skills: string[];
  color: string;
}

export const skillsData: SkillCategory[] = [
  {
    title: "AI / Machine Learning",
    description: "Agentic workflows, RAG pipelines, and applied computer vision in production.",
    icon: "Brain",
    skills: [
      "LangChain",
      "CrewAI",
      "RAG",
      "LLMs",
      "GPT-4",
      "Prompt Engineering",
      "Embeddings",
      "Semantic Search",
      "Vector DBs (ChromaDB, Pinecone)",
      "YOLOv8",
      "PyTorch",
      "OpenCV",
      "Tesseract OCR / EasyOCR",
      "n8n",
    ],
    color: "bg-violet-50 border-violet-100 text-violet-700",
  },
  {
    title: "Backend",
    description: "Production Python APIs and services across frameworks.",
    icon: "Server",
    skills: [
      "Python",
      "Django 3/4/5",
      "Django REST Framework",
      "Django Channels",
      "FastAPI",
      "Flask",
      "Celery",
      "Huey",
      "RabbitMQ",
      "GraphQL",
      "WebSockets",
      "gRPC",
      "JWT / OAuth 2.0",
      "Wagtail CMS",
    ],
    color: "bg-emerald-50 border-emerald-100 text-emerald-700",
  },
  {
    title: "Frontend",
    description: "Typed, modern web frontends.",
    icon: "Layout",
    skills: [
      "React 18/19",
      "Next.js 16",
      "Angular 15",
      "TypeScript 5",
      "TailwindCSS",
      "Redux Toolkit",
      "RxJS",
      "Material-UI",
    ],
    color: "bg-sky-50 border-sky-100 text-sky-700",
  },
  {
    title: "Cloud & DevOps",
    description: "Infrastructure, containers, and CI/CD across major clouds.",
    icon: "Cloud",
    skills: [
      "AWS (S3, EC2, RDS, ECS, ECR, SES, CloudWatch)",
      "Google Cloud Platform (BigQuery, GKE, Artifact Registry)",
      "Docker",
      "Kubernetes",
      "GitHub Actions",
      "Nginx",
      "Gunicorn",
      "PM2",
      "Linux / Bash",
    ],
    color: "bg-rose-50 border-rose-100 text-rose-700",
  },
  {
    title: "Databases",
    description: "Relational, document, and analytical data stores.",
    icon: "Database",
    skills: [
      "PostgreSQL",
      "MySQL",
      "MongoDB",
      "Redis",
      "Firebase / Firestore",
      "SQLite",
      "BigQuery",
      "Snowflake",
    ],
    color: "bg-amber-50 border-amber-100 text-amber-700",
  },
];
