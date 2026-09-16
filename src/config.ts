// ─────────────────────────────────────────────────────────────────────────────
//  PER-PROJECT BRANDING  ·  the ONLY file that changes between blog repos.
//  Owner-locked via CODEOWNERS — the SEO team does not edit this (see CONTRIBUTING.md).
// ─────────────────────────────────────────────────────────────────────────────
export const SITE = {
  brand: 'WhatPing',
  title: 'WhatPing Blog',
  description: 'Guides, tips, and product updates from the WhatPing team.',
  url: 'https://blogs.whatping.com',
  marketingUrl: 'https://whatping.com',
  marketingLabel: 'whatping.com',
  author: 'WhatPing Team',
  accent: '#22c55e',
  tagline: 'Know the moment it goes down.',
  locale: 'en',
} as const;

export const NAV = [
  { label: 'Blog', href: '/' },
  { label: 'Tags', href: '/tags/' },
  { label: 'About', href: '/about/' },
];
