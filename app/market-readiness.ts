export type PriceGrade="A"|"B"|"C"|"D"|"E";
export type ReadinessRow={grade?:string;species_id?:string;product?:string;validation_status?:string};
export type MarketReadiness={level:"L0"|"L1"|"L2";label:"有数据态"|"参考态"|"种子态";N:number;S:number;verified:number};

const directGrades=new Set(["A","B","C","D"]);
const focusSpecies=[
  ["oyster_mushroom","平菇"],
  ["shiitake","香菇"],
  ["wood_ear","木耳"],
] as const;

export function marketReadiness(rows:ReadinessRow[]):MarketReadiness{
  const N=rows.filter(row=>directGrades.has(row.grade??"")).length;
  const S=focusSpecies.filter(([id,name])=>rows.some(row=>[...directGrades,"E"].includes(row.grade??"")&&(row.species_id===id||row.product?.includes(name)))).length;
  const verified=rows.filter(row=>directGrades.has(row.grade??"")&&(row.validation_status==="valid"||row.grade==="A")).length;
  if(N>=5||S>=2)return {level:"L0",label:"有数据态",N,S,verified};
  if(N>=1)return {level:"L1",label:"参考态",N,S,verified};
  return {level:"L2",label:"种子态",N,S,verified};
}
