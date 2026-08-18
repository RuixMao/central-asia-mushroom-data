import re

SPECIES={
 "button_mushroom":["шампиньон","шампиньондор","шампин.","шампин","champignon","button mushroom","gelin kömelek","şampinýon","şampinon","şampinjon","şampion","champinjon","shampinyon","sampinyon","shampinion","双孢菇"],"oyster_mushroom":["вешенк","veshenka","veshenki","weşenka kömelegi","устричный гриб","oyster mushroom","平菇"],
 "enoki":["эноки","enoki","enokitake","金针菇"],"shiitake":["шиитаке","шиитаки","shiitake","siitake","sitake","香菇"],"king_oyster_mushroom":["королевская вешенка","king oyster mushroom","king trumpet mushroom","эринги","eringi","杏鲍菇"],
 "shimeji":["шимиджи","shimeji","shimeji"],"wood_ear":["муэр","wood ear","древесный гриб","ағаш саңырауқұлағы"],"snow_fungus":["серебряное ухо","snow fungus"],
 "morel":["сморчок","morel"],"matsutake":["мацутакэ","matsutake"],"porcini":["белый гриб","гриб белый","боровик","подосиновик","подосиновики","красноголовик","porcini","ақ саңырауқұлақ"],
 "chanterelle":["лисичк","chanterelle"],"straw_mushroom":["вольвариелла","straw mushroom"],"honey_fungus":["опёнок","опенок","опята","honey mushroom","honey fungus","занбӯруғи асал","бал саңырауқұлағы"],
 "suillus":["маслёнок","масленок","маслята","suillus"],"truffle":["трюфель","truffle"]}
AMBIGUOUS=["грибы","mushrooms","саңырауқұлақ","козу карын","занбӯруғ","qo‘ziqorin","qo'ziqorin","золотые нити","древесные грибы","лесные грибы","kömelek","gömelek","komelek","kömelekler","kömelekli","komelekler","komelekli","вешенкалар","шампиньондар"]
EXCLUDE_ONLY=["грибной соус","mushroom sauce","mushroom flavour","蘑菇味","мицелий","грибница","семена гриб","споры гриб","ящик для грибов","увлажнитель","оборудование для гриб","субстрат","компост для гриб","набор для выращивания","электрод","светильник","лампа","игрушк","декор","саңырауқұлақ тәрізді","электр"]
FORMS=[("prepared_food",["готовое блюдо","в соусе","суп","лапша","приправа","соус"]),("frozen",["заморож","frozen"]),("dried",["сушен","сушён","сухие","сухой","сухая","dried","хушккарда"]),("pickled",["марин","pickled","marinadlanan"]),("canned",["консерв","canned","konserw"]),("powder",["порош","powder"]),("provisionally_preserved",["временно консерв"]),("chilled",["охлажден","chilled"]),("fresh",["свеж","fresh"])]

def _hits(text):
 matches=[]
 for sid,terms in SPECIES.items():
  for term in sorted(terms,key=len,reverse=True):
   start=text.find(term)
   while start>=0:
    matches.append((sid,term,start,start+len(term)))
    start=text.find(term,start+1)
 matches.sort(key=lambda item:len(item[1]),reverse=True)
 kept=[]
 for match in matches:
  if any(match[2]>=longer[2] and match[3]<=longer[3] for longer in kept):continue
  kept.append(match)
 return [(sid,term) for sid,term,_,_ in kept]

def _fix_mojibake(text):
    """修复 UTF-8 双重编码乱码(mojibake),幂等。

    现象:采集端把 UTF-8 字节再按 Latin-1 解码,ö(0xF6)变成 Ã¶(0xC3 0xB6)。
    修复:latin-1 重新编码 → utf-8 解码。已正确编码的文本不受影响(幂等)。
    """
    try:
        fixed = text.encode("latin-1").decode("utf-8")
        return fixed if fixed != text else text
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def classify(title,description="",category="",language="",image_metadata=None):
 title=_fix_mojibake(title);description=_fix_mojibake(description);category=_fix_mojibake(category)
 title_l=title.lower().replace("ё","е");description_l=description.lower().replace("ё","е");category_l=category.lower().replace("ё","е")
 if any(x in " ".join((title_l,description_l,category_l)) for x in EXCLUDE_ONLY):
  return {"species_id":None,"product_form":"prepared_food","classification_status":"excluded","status":"excluded","confidence":1.0,"evidence":[{"field":"title","rule":"excluded"}],"reasons":["non-mushroom retail product"]}
 title_hits=_hits(title_l);desc_hits=_hits(description_l);cat_hits=_hits(category_l);all_ids={x[0] for x in title_hits+desc_hits+cat_hits}
 form=next((f for f,terms in FORMS if any(t in " ".join((title_l,description_l,category_l)) for t in terms)),"fresh")
 if len({x[0] for x in title_hits})>1 or (not title_hits and len(all_ids)>1):status,species,confidence="mixed_species","mixed_mushrooms",.99
 elif title_hits and desc_hits and title_hits[0][0]!=desc_hits[0][0]:status,species,confidence="review_required",None,.45
 elif all_ids:
  status="classified";species=(title_hits or desc_hits or cat_hits)[0][0];confidence=.98 if title_hits else (.92 if desc_hits else .75)
 elif any(term in " ".join((title_l,description_l,category_l)) for term in AMBIGUOUS):
  # 本地语言食用菌总称(如 саңырауқұлақ/занбӯруғ/козу карын):确认为蘑菇但品种未定,不强行归类
  status,species,confidence="ambiguous",None,.5
 else:status,species,confidence="unknown",None,0.0
 evidence=[{"field":"title","term":t} for _,t in title_hits]+[{"field":"description","term":t} for _,t in desc_hits]+[{"field":"category","term":t} for _,t in cat_hits]
 return {"species_id":species,"product_form":form,"classification_status":status,"status":status,"confidence":confidence,"evidence":evidence,"reasons":[] if evidence else ["no deterministic synonym match"]}

def parse_package(text,allow_volume=False,volume_kg_per_l=1.0):
 s=text.lower().replace(",",".");evidence=None;count=1
 volume=re.search(r"(\d+(?:\.\d+)?)\s*(ml|мл|l|л|литр)\b",s)
 if volume:
  value=float(volume.group(1));unit=volume.group(2);litres=value/1000 if unit in ("ml","мл") else value
  if not allow_volume:
   return {"package_value":value,"package_unit":"ml" if unit in ("ml","мл") else "l","package_count":1,"normalized_quantity_kg":None,"parse_status":"volume_not_mass","evidence":volume.group(0),"value":value,"unit":"ml" if unit in ("ml","мл") else "l","quantity_kg":None,"conversion_basis":None}
  kg=litres*float(volume_kg_per_l)
  return {"package_value":value,"package_unit":"ml" if unit in ("ml","мл") else "l","package_count":1,"normalized_quantity_kg":kg,"parse_status":"valid_volume_estimate","evidence":volume.group(0),"value":value,"unit":"ml" if unit in ("ml","мл") else "l","quantity_kg":kg,"conversion_basis":f"1 L = {float(volume_kg_per_l):g} kg"}
 m=re.search(r"(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(kg|кг|gr|g|гр|г)\b",s)
 if m:count=int(m.group(1));value=float(m.group(2));unit=m.group(3);evidence=m.group(0)
 else:
  m=re.search(r"(\d+(?:\.\d+)?)\s*(kg|кг|gr|g|гр|г)\s*[x×]\s*(\d+)",s)
  if m:value=float(m.group(1));unit=m.group(2);count=int(m.group(3));evidence=m.group(0)
  else:
   m=re.search(r"(\d+(?:\.\d+)?)\s*(kg|кг|gr|g|гр|г)\b",s)
   if m:value=float(m.group(1));unit=m.group(2);evidence=m.group(0)
   elif re.search(r"(за|по|per)\s*(1\s*)?(kg|кг)",s):value,unit,evidence=1.0,"kg","per kg"
   else:return {"package_value":None,"package_unit":None,"package_count":None,"normalized_quantity_kg":None,"parse_status":"uncertain" if re.search(r"шт|pack|упак|件",s) else "invalid","evidence":None,"value":None,"unit":None,"quantity_kg":None}
 kg=(value if unit in ("kg","кг") else value/1000)*count
 return {"package_value":value,"package_unit":"kg" if unit in ("kg","кг") else "g","package_count":count,"normalized_quantity_kg":kg,"parse_status":"valid","evidence":evidence,"value":value,"unit":"kg" if unit in ("kg","кг") else "g","quantity_kg":kg}

def normalize_price(price,package_text,promotion_price=None,allow_volume=False,volume_kg_per_l=1.0):
 if price is not None and price<=0:raise ValueError("price must be positive")
 if promotion_price is not None and promotion_price<=0:raise ValueError("promotion price must be positive")
 package=parse_package(package_text,allow_volume=allow_volume,volume_kg_per_l=volume_kg_per_l);effective=promotion_price if promotion_price is not None else price
 return {**package,"price_per_kg":round(effective/package["normalized_quantity_kg"],2) if effective is not None and package["normalized_quantity_kg"] else None}
