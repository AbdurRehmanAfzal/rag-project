'use client';
import { useEffect } from 'react';
import fluidCursor from '@/hooks/use-FluidCursor';

// In chat view the transcript column (max-w-4xl = 896px, centered) must stay
// clean for readability, so the canvas is masked out over that column and the
// glow only shows in the side margins. On viewports narrower than the column
// the mask leaves nothing visible, which is correct: mobile chat is full-width.
const CHAT_MASK =
  'linear-gradient(to right, black 0%, black calc(50% - 520px), transparent calc(50% - 460px), transparent calc(50% + 460px), black calc(50% + 520px), black 100%)';

const FluidCursor = ({ view, theme }: { view: 'landing' | 'chat'; theme: 'light' | 'dark' }) => {
  useEffect(() => {
    const cleanup = fluidCursor();
    return () => {
      if (cleanup) cleanup();
    };
  }, []);

  const maskStyle =
    view === 'chat'
      ? { WebkitMaskImage: CHAT_MASK, maskImage: CHAT_MASK }
      : undefined;

  return (
    // z-0 keeps the fluid glow above the page background but behind all
    // content (<main> is z-10, header z-40) in both landing and chat views.
    // The glow palette is tuned for dark backgrounds; soften it on light.
    <div
      className={`fixed inset-0 z-0 pointer-events-none transition-opacity duration-500 ${
        theme === 'light' ? 'opacity-60' : 'opacity-100'
      }`}
      style={maskStyle}
    >
      <canvas id="fluid" className="fixed top-0 left-0 w-full h-full pointer-events-none" />
    </div>
  );
};

export default FluidCursor;
