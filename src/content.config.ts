import { glob } from "astro/loaders";
import { defineCollection, z } from "astro:content";

/**
 * Frontmatter is the same shape the content package was authored in, so `docs/site/` stays the
 * source of truth: `route` is the URL, and the routing pages read it rather than deriving a
 * path from the filename. That keeps `docs/site/02-SITEMAP.md` authoritative even though the
 * files here are flat.
 */
const page = z.object({
  route: z.string(),
  title: z.string(),
  description: z.string(),
  h1: z.string(),
  /** Optional subhead + kicker for the page header band; both default sensibly. */
  lede: z.string().optional(),
  eyebrow: z.string().optional(),
});

export const collections = {
  pages: defineCollection({
    loader: glob({ pattern: "**/*.mdx", base: "./src/content/pages" }),
    schema: page,
  }),
  docs: defineCollection({
    loader: glob({ pattern: "**/*.mdx", base: "./src/content/docs" }),
    schema: page,
  }),
};
