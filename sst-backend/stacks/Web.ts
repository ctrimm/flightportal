import { StackContext, NextjsSite, use } from "sst/constructs";
import { API } from "./API";

export function Web({ stack }: StackContext) {
  const { api } = use(API);

  // Marketing site
  const site = new NextjsSite(stack, "site", {
    path: "../marketing-site",
    environment: {
      NEXT_PUBLIC_API_URL: api.url,
      NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.STRIPE_PUBLISHABLE_KEY || "",
      STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY || "",
      STRIPE_PRICE_ID: process.env.STRIPE_PRICE_ID || "",
    },
  });

  // Custom domain for marketing site
  if (stack.stage === "prod") {
    site.attachCustomDomain({
      domainName: process.env.DOMAIN || "flightportal.com",
      domainAlias: `www.${process.env.DOMAIN || "flightportal.com"}`,
    });
  }

  stack.addOutputs({
    SiteUrl: site.url,
  });

  return { site };
}
