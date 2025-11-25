import { StackContext, Bucket } from "sst/constructs";

export function Storage({ stack }: StackContext) {
  // Firmware storage bucket
  const firmwareBucket = new Bucket(stack, "firmware", {
    cors: [
      {
        allowedMethods: ["GET"],
        allowedOrigins: ["*"],
        allowedHeaders: ["*"],
      },
    ],
  });

  // Device configs backup bucket
  const backupBucket = new Bucket(stack, "backups", {
    cors: false,
  });

  return { firmwareBucket, backupBucket };
}
