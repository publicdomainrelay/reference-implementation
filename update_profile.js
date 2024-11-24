import { BskyAgent } from '@atproto/api';

const agent = new BskyAgent({
  service: Deno.env.get("ATPROTO_BASE_URL")
})
await agent.login({
  identifier: Deno.env.get("ATPROTO_HANDLE"),
  password: Deno.env.get("ATPROTO_PASSWORD"),
})

await agent.upsertProfile(existingProfile => {
  const existing = existingProfile ?? {}

  // existing.pinnedPost = Deno.env.get("ATPROTO_PASSWORD")
  existing.description = `${process.env["ATPROTO_HANDLE"]}`;

  return existing
})
