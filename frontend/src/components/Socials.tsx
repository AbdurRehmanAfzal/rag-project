// Real contact links only. Inline SVGs to avoid an icon-library dependency.
const socials = [
  {
    href: 'https://github.com/AbdurRehmanAfzal',
    label: 'GitHub',
    external: true,
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" className="h-[17px] w-[17px]" aria-hidden>
        <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.55v-2.17c-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.68-1.28-1.68-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.19 1.76 1.19 1.03 1.75 2.69 1.25 3.34.95.1-.74.4-1.25.72-1.54-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.16-1.18 3.16-1.18.63 1.59.24 2.76.12 3.05.74.81 1.19 1.83 1.19 3.09 0 4.41-2.7 5.38-5.27 5.67.41.35.78 1.05.78 2.12v3.14c0 .3.2.67.8.55A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z" />
      </svg>
    ),
  },
  {
    href: 'https://www.linkedin.com/in/abdurrehmanafzal/',
    label: 'LinkedIn',
    external: true,
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" className="h-[16px] w-[16px]" aria-hidden>
        <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12ZM7.12 20.45H3.56V9h3.56v11.45Z" />
      </svg>
    ),
  },
  {
    href: 'https://wa.me/923341500888',
    label: 'WhatsApp',
    external: true,
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" className="h-[17px] w-[17px]" aria-hidden>
        <path d="M12.04 2a9.9 9.9 0 0 0-8.57 14.86L2 22l5.28-1.38A9.9 9.9 0 1 0 12.04 2Zm5.82 14.12c-.24.68-1.4 1.3-1.93 1.35-.52.05-1.01.24-3.4-.71-2.87-1.13-4.68-4.06-4.82-4.25-.14-.19-1.15-1.53-1.15-2.92 0-1.39.73-2.07.99-2.36.26-.28.57-.35.76-.35l.55.01c.18 0 .41-.07.64.49.24.57.81 1.97.88 2.11.07.14.12.31.02.5-.09.19-.14.3-.28.47-.14.16-.3.37-.42.5-.14.14-.29.29-.13.57.17.28.74 1.22 1.59 1.98 1.09.97 2 1.27 2.29 1.41.28.14.45.12.61-.07.17-.19.7-.82.89-1.1.19-.28.38-.24.64-.14.26.09 1.64.77 1.92.91.28.14.47.21.54.33.07.12.07.68-.17 1.37Z" />
      </svg>
    ),
  },
  {
    href: 'mailto:abdurrehmanafzal786@gmail.com',
    label: 'Email',
    external: false,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-[17px] w-[17px]" aria-hidden>
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <path d="m3 7 9 6 9-6" />
      </svg>
    ),
  },
];

function SocialLink({ s, theme, size }: { s: (typeof socials)[number]; theme?: string; size: string }) {
  return (
    <a
      href={s.href}
      {...(s.external ? { target: '_blank', rel: 'noreferrer' } : {})}
      aria-label={s.label}
      title={s.label}
      className={`flex ${size} items-center justify-center rounded-full border backdrop-blur-xl shadow-sm transition-all duration-300 hover:scale-110 hover:text-iris hover:border-iris/60 ${
        theme === 'dark'
          ? 'bg-zinc-900/30 border-zinc-800/50 text-zinc-400'
          : 'bg-white/40 border-white/60 text-slate-500'
      }`}
    >
      {s.icon}
    </a>
  );
}

/* Fixed vertical dock on wide screens: always in reach for recruiters. */
export function SocialDock({ theme }: { theme?: string }) {
  return (
    <aside className="fixed left-4 top-1/2 z-40 hidden -translate-y-1/2 flex-col items-center gap-2.5 xl:flex">
      {socials.map((s) => (
        <SocialLink key={s.label} s={s} theme={theme} size="h-10 w-10" />
      ))}
    </aside>
  );
}

/* Inline row for the landing view where the fixed dock is hidden. */
export function SocialRow({ theme, className = '' }: { theme?: string; className?: string }) {
  return (
    <div className={`flex items-center justify-center gap-2.5 xl:hidden ${className}`}>
      {socials.map((s) => (
        <SocialLink key={s.label} s={s} theme={theme} size="h-11 w-11" />
      ))}
    </div>
  );
}
