export const SITE_URL = "https://whatping.com";
export const APP_URL = "https://monitor.whatping.com";
export const CONTACT_EMAIL = "hello@whatping.com";

/** Docs sidebar order. Also drives prev/next, so it is the reading order too. */
export const DOCS_NAV: { group: string; items: { href: string; label: string }[] }[] = [
  {
    group: "Getting started",
    items: [
      { href: "/docs/", label: "Overview" },
      { href: "/docs/quickstart/", label: "Quickstart" },
      { href: "/docs/concepts/", label: "Concepts" },
    ],
  },
  {
    group: "Monitor types",
    items: [
      { href: "/docs/monitors/http/", label: "HTTP" },
      { href: "/docs/monitors/tcp/", label: "TCP" },
      { href: "/docs/monitors/heartbeat/", label: "Heartbeat" },
      { href: "/docs/monitors/ssl/", label: "Certificate" },
      { href: "/docs/monitors/domain/", label: "Domain expiry" },
      { href: "/docs/monitors/dns/", label: "DNS" },
      { href: "/docs/monitors/email-auth/", label: "Email auth" },
    ],
  },
  {
    group: "Alerting",
    items: [
      { href: "/docs/alerting/channels/", label: "Channels" },
      { href: "/docs/alerting/re-alert/", label: "Reminders" },
      { href: "/docs/alerting/second-opinion/", label: "Second opinion" },
    ],
  },
  {
    group: "Reference",
    items: [
      { href: "/docs/webhook-payload/", label: "Webhook payload" },
      { href: "/docs/heartbeat-api/", label: "Heartbeat ping" },
      { href: "/docs/limits/", label: "Limits" },
      { href: "/docs/security/", label: "Security model" },
      { href: "/docs/troubleshooting/", label: "Troubleshooting" },
      { href: "/docs/faq/", label: "FAQ" },
    ],
  },
];

export const DOCS_FLAT = DOCS_NAV.flatMap((g) => g.items);

/** Routes in the content collections are authored without a trailing slash. */
export const normalize = (route: string) =>
  route === "/" ? "/" : `${route.replace(/\/$/, "")}/`;
