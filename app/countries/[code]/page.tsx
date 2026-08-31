import {permanentRedirect} from "next/navigation";
export default async function CountryPage({params}:{params:Promise<{code:string}>}){const {code}=await params;permanentRedirect(`/markets/${code.toUpperCase()}`)}
