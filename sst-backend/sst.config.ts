import { SSTConfig } from "sst";
import { API } from "./stacks/API";
import { Database } from "./stacks/Database";
import { Storage } from "./stacks/Storage";
import { Web } from "./stacks/Web";

export default {
  config(_input) {
    return {
      name: "flight-portal",
      region: "us-east-1",
    };
  },
  stacks(app) {
    app
      .stack(Database)
      .stack(Storage)
      .stack(API)
      .stack(Web);
  },
} satisfies SSTConfig;
