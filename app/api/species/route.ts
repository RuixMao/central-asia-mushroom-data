import { getDb } from "../../../db";import { species } from "../../../db/schema";
export async function GET(){return Response.json({records:await getDb().select().from(species)})}
