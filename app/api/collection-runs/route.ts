import { desc } from "drizzle-orm";import { getDb } from "../../../db";import { collectionRuns } from "../../../db/schema";
export async function GET(){const records=await getDb().select().from(collectionRuns).orderBy(desc(collectionRuns.startedAt)).limit(100);return Response.json({records,count:records.length})}
