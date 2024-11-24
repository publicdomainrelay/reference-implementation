import { BskyAgent } from '@atproto/api'

const agent = new BskyAgent({
  service: Deno.env.get("ATPROTO_BASE_URL"),
})
await agent.login({
  identifier: Deno.env.get("ATPROTO_HANDLE"),
  password: Deno.env.get("ATPROTO_PASSWORD"),
})

await agent.upsertProfile(existingProfile => {
  const existing = existingProfile ?? {}

  existing.pinnedPost = {
    "uri": Deno.env.get("ATPROTO_PINNED_POST_URI"),
    "cid": Deno.env.get("ATPROTO_PINNED_POST_CID"),
  }

  return existing
})
