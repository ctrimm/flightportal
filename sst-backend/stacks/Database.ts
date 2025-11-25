import { StackContext, Table } from "sst/constructs";

export function Database({ stack }: StackContext) {
  // Device configurations table
  const configTable = new Table(stack, "config", {
    fields: {
      deviceId: "string",
      layoutId: "string",
      timestamp: "number",
    },
    primaryIndex: { partitionKey: "deviceId", sortKey: "timestamp" },
  });

  // Layouts table
  const layoutsTable = new Table(stack, "layouts", {
    fields: {
      layoutId: "string",
      version: "number",
    },
    primaryIndex: { partitionKey: "layoutId", sortKey: "version" },
  });

  // Device registry table
  const devicesTable = new Table(stack, "devices", {
    fields: {
      deviceId: "string",
      customerId: "string",
      lastSeen: "number",
    },
    primaryIndex: { partitionKey: "deviceId" },
    globalIndexes: {
      customerIndex: { partitionKey: "customerId", sortKey: "lastSeen" },
    },
  });

  // Firmware versions table
  const firmwareTable = new Table(stack, "firmware", {
    fields: {
      version: "string",
      released: "number",
    },
    primaryIndex: { partitionKey: "version", sortKey: "released" },
  });

  // Orders table (for Stripe purchases)
  const ordersTable = new Table(stack, "orders", {
    fields: {
      orderId: "string",
      customerId: "string",
      created: "number",
    },
    primaryIndex: { partitionKey: "orderId" },
    globalIndexes: {
      customerOrders: { partitionKey: "customerId", sortKey: "created" },
    },
  });

  return {
    configTable,
    layoutsTable,
    devicesTable,
    firmwareTable,
    ordersTable,
  };
}
