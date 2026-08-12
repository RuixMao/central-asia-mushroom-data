import { getDb } from "../../../../db";import { platforms } from "../../../../db/schema";
export async function GET(){return Response.json({records:await getDb().select().from(platforms)})}
