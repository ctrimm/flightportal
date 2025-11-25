import { StackContext, Api, use } from "sst/constructs";
import { Database } from "./Database";
import { Storage } from "./Storage";

export function API({ stack }: StackContext) {
  const { configTable, layoutsTable, devicesTable, firmwareTable, ordersTable } = use(Database);
  const { firmwareBucket, backupBucket } = use(Storage);

  // API with custom authorizer for device authentication
  const api = new Api(stack, "api", {
    defaults: {
      function: {
        bind: [
          configTable,
          layoutsTable,
          devicesTable,
          firmwareTable,
          ordersTable,
          firmwareBucket,
          backupBucket,
        ],
        environment: {
          SIGNING_KEY: process.env.SIGNING_KEY || "change-me-in-production",
          DEVICE_API_KEY: process.env.DEVICE_API_KEY || "change-me-in-production",
          ADMIN_API_KEY: process.env.ADMIN_API_KEY || "change-me-in-production",
        },
      },
    },
    authorizers: {
      device: {
        type: "lambda",
        function: {
          handler: "functions/authorizer.device",
        },
      },
      admin: {
        type: "lambda",
        function: {
          handler: "functions/authorizer.admin",
        },
      },
    },
    routes: {
      // Device endpoints (authenticated as device)
      "GET /api/config": {
        function: "functions/config.get",
        authorizer: "device",
      },
      "GET /api/layouts": {
        function: "functions/layouts.list",
        authorizer: "device",
      },
      "GET /api/layouts/{id}": {
        function: "functions/layouts.get",
        authorizer: "device",
      },
      "GET /api/firmware/check": {
        function: "functions/firmware.check",
        authorizer: "device",
      },
      "GET /api/firmware/download": {
        function: "functions/firmware.download",
        authorizer: "device",
      },
      "GET /api/fields/available": {
        function: "functions/fields.list",
        authorizer: "device",
      },

      // Admin endpoints (authenticated as admin)
      "PUT /api/config": {
        function: "functions/config.update",
        authorizer: "admin",
      },
      "POST /api/layouts": {
        function: "functions/layouts.create",
        authorizer: "admin",
      },
      "PUT /api/layouts/{id}": {
        function: "functions/layouts.update",
        authorizer: "admin",
      },
      "DELETE /api/layouts/{id}": {
        function: "functions/layouts.delete",
        authorizer: "admin",
      },
      "POST /api/firmware/upload": {
        function: "functions/firmware.upload",
        authorizer: "admin",
      },

      // Public endpoints
      "POST /api/orders/create": "functions/orders.create",
      "POST /api/stripe/webhook": "functions/stripe.webhook",
    },
  });

  // Custom domain (configure in Route 53)
  if (stack.stage === "prod") {
    api.attachCustomDomain({
      domainName: `api.${process.env.DOMAIN || "flightportal.com"}`,
    });
  }

  stack.addOutputs({
    ApiEndpoint: api.url,
    ApiId: api.httpApiId,
  });

  return { api };
}
