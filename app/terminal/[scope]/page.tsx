import {permanentRedirect} from "next/navigation";
export default async function Page({params}:{params:Promise<{scope:string}>}){const scope=decodeURIComponent((await params).scope);permanentRedirect(`/markets/${scope}`)}
