import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import { defineConfig } from "astro/config";

// Static output — the Astro default. Every page here is prose known at build time, so there
// is no adapter, no SSR and nothing to be compatible with on Cloudflare Pages.
export default defineConfig({
  site: "https://whatping.com",
  // Directory-per-route. Pages serves /docs/limits/ from /docs/limits/index.html without a
  // redirect hop, which a file-per-route build would need.
  trailingSlash: "always",
  build: { format: "directory" },
  integrations: [mdx(), sitemap()],
  markdown: {
    shikiConfig: {
      // Matches the site palette rather than shipping a second colour system in code blocks.
      theme: "vesper",
      wrap: true,
    },
  },
  devToolbar: { enabled: false },
});
