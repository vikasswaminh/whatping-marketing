import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import { defineConfig } from "astro/config";

// Static output — the Astro default. Every page here is prose known at build time, so there
// is no adapter, no SSR and nothing to be compatible with on Cloudflare Pages.
export default defineConfig({
  site: "https://www.whatping.com",
  // Directory-per-route. Pages serves /docs/limits/ from /docs/limits/index.html without a
  // redirect hop, which a file-per-route build would need.
  trailingSlash: "always",
  build: { format: "directory" },
  // /og/ is the source for public/og.png, not a page anyone should land on. It carries a
  // noindex tag as well; this keeps it out of the sitemap we actively submit.
  integrations: [mdx(), sitemap({ filter: (page) => !page.includes("/og/") })],
  markdown: {
    shikiConfig: {
      // Code blocks are a dark console inset on every surface (dark pages AND the paper
      // docs — see `.prose pre` in global.css, which pins them to --console-bay), so the
      // highlighter is dark-themed. github-light on the dark inset was black-on-black.
      theme: "github-dark-default",
      wrap: true,
    },
  },
  devToolbar: { enabled: false },
});
