import { getCollection, type CollectionEntry } from 'astro:content';

/** All non-draft posts (drafts hidden in production builds), newest first. */
export async function getPublishedPosts(): Promise<any[]> {
  const posts = await getCollection('blog', ({ data }) =>
    import.meta.env.PROD ? data.draft !== true : true,
  );
  const normalized = posts.map(post => ({
    ...post,
    slug: post.slug || post.id.replace(/\.mdx?$/, '')
  }));
  return normalized.sort((a, b) => {
    const dateA = a.data.pubDate ? new Date(a.data.pubDate).getTime() : 0;
    const dateB = b.data.pubDate ? new Date(b.data.pubDate).getTime() : 0;
    return dateB - dateA;
  });
}

/** Rough reading time in minutes from raw markdown body. */
export function readingTime(body: string = ''): number {
  if (!body) return 1;
  const words = body.trim().split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 200));
}
